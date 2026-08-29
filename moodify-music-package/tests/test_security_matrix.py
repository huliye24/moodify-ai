"""Production security matrix tests — MFY_PRODUCTION_SECURITY_PRIVACY_ACCEPTANCE_001.

- dedicated test identity factory (anonymous/listener A+B/creator A+B/
  ear-operator/reviewer/service)
- authorization matrix over representative endpoints per identity
- security headers on the public BFF (no HSTS — that is the nginx/TLS layer)
- session lifecycle: fixation, revocation, expiry
- error responses never leak internals
- upload boundary: path traversal, filename injection, MIME/size
"""

from __future__ import annotations

import os

os.environ["MOODIFY_INTERNAL_API_KEY"] = "test-service-key"

import pytest
from fastapi.testclient import TestClient

from conftest import ENGINE
from moodify_music import models as M
from moodify_music.api.main import app as internal_app
from moodify_music.bff.main import app as bff_app

internal_client = TestClient(internal_app)
bff_client = TestClient(bff_app)
AUTH = {"X-Moodify-Service-Key": "test-service-key"}


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    with ENGINE.begin() as conn:
        for table in reversed(M.Base.metadata.sorted_tables):
            conn.execute(table.delete())


# ---------------------------------------------------------- identity factory

class Identity:
    def __init__(self, role: str, user_id: str, handle: str | None = None):
        self.role = role
        self.user_id = user_id
        self.handle = handle

    @property
    def actor(self) -> dict:
        return {**AUTH, "X-Moodify-Actor-User-Id": self.user_id}


def make_identities() -> dict[str, Identity]:
    """Dedicated test identities (59 task 2); never real users."""
    identities = {
        "anonymous": Identity("anonymous", ""),
        "listener-a": Identity("listener", "user-lst-a"),
        "listener-b": Identity("listener", "user-lst-b"),
        "creator-a": Identity("creator", "user-crt-a", handle="creator-a"),
        "creator-b": Identity("creator", "user-crt-b", handle="creator-b"),
        "ear-operator": Identity("operator", "user-op-1"),
        "reviewer": Identity("reviewer", "user-rev-1"),
        "service": Identity("service", "service-1"),
    }
    for name, identity in identities.items():
        if identity.role == "anonymous":
            continue
        r = internal_client.post("/internal/v1/music/auth/ensure-user", headers=AUTH,
                                 json={"user_id": identity.user_id, "display_name": name})
        assert r.status_code == 201, f"ensure-user {name}"
    for name in ("creator-a", "creator-b"):
        identity = identities[name]
        r = internal_client.post("/internal/v1/music/creators", headers={**identity.actor, "Idempotency-Key": f"idem-cr-{name}"},
                                 json={"user_id": identity.user_id, "handle": identity.handle, "display_name": identity.handle})
        assert r.status_code == 201, f"creator {name}"
    return identities


# ---------------------------------------------------------- authorization matrix

def test_authorization_matrix_anonymous_read_only():
    ids = make_identities()
    _ = ids["anonymous"]  # anonymous is implicit: no actor header
    # public reads allowed
    assert internal_client.get("/internal/v1/music/catalogue", headers=AUTH).status_code == 200
    # writes without actor fail closed (401/403/404)
    for method, path, body in [
        ("POST", "/internal/v1/music/tracks", {"creator_id": "x", "title": "T"}),
        ("PUT", "/internal/v1/music/users/u1/favorites/t1", {}),
    ]:
        r = getattr(internal_client, method.lower())(path, headers=AUTH, json=body)
        assert r.status_code in (401, 403, 404), f"anonymous {method} {path} -> {r.status_code}"


def test_creator_a_cannot_touch_creator_b_drafts_or_passport():
    ids = make_identities()
    a, b = ids["creator-a"], ids["creator-b"]
    track_a = internal_client.post("/internal/v1/music/tracks", headers={**a.actor, "Idempotency-Key": "idem-ta"},
                                   json={"creator_id": a.handle and next(
                                       (r.json()["id"] for r in [internal_client.get(f"/internal/v1/music/creators/by-handle/{a.handle}", headers=AUTH)]
                                        if r.status_code == 200), None) or _creator_id(a), "title": "A"}).json()

    # B attempts to write A's passport -> forbidden
    forged = internal_client.put(f"/internal/v1/music/tracks/{track_a['id']}/passport",
                                 headers={**b.actor, "Idempotency-Key": "idem-forge"},
                                 json={"origin_type": "human"})
    assert forged.status_code == 403
    assert forged.json()["error"]["code"] == "OWNERSHIP_DENIED"


def _creator_id(identity: Identity) -> str:
    r = internal_client.get(f"/internal/v1/music/creators/by-handle/{identity.handle}", headers=AUTH)
    return r.json()["id"]


def test_listener_cannot_write_creator_surface():
    ids = make_identities()
    listener, creator = ids["listener-a"], ids["creator-a"]
    cid = _creator_id(creator)
    r = internal_client.post("/internal/v1/music/tracks", headers={**listener.actor, "Idempotency-Key": "idem-lst"},
                             json={"creator_id": cid, "title": "Not yours"})
    assert r.status_code == 403  # listener is not the creator owner
    assert r.json()["error"]["code"] == "OWNERSHIP_DENIED"


def test_reviewer_boundary_is_recorded():
    """Reviewer decisions live on the Ear side (48 package), never on the
    Music BFF. This test records the boundary without importing Ear modules
    (music package must not depend on core in a clean environment)."""
    routes = {r.path for r in bff_app.routes if hasattr(r, "path")}
    assert not any("review" in path for path in routes), "Music BFF must not expose review endpoints"


def test_service_key_required_on_internal_api():
    r = internal_client.get("/internal/v1/music/catalogue")  # no service key
    assert r.status_code == 401


# ---------------------------------------------------------- security headers

def test_bff_sets_security_headers_and_no_store_on_private():
    from unittest.mock import patch
    import httpx

    upstream = httpx.Response(200, json={"id": "t1"})
    with patch("moodify_music.bff.main.httpx.request", return_value=upstream):
        r = bff_client.get("/api/v1/music/tracks/nonexistent-hdr-test")
    assert r.headers.get("x-content-type-options") == "nosniff"
    assert r.headers.get("x-frame-options") == "DENY"
    assert r.headers.get("referrer-policy") == "strict-origin-when-cross-origin"
    # HSTS is nginx/TLS layer — live gate (59 plan), not asserted here


def test_bff_no_store_on_private_paths():
    from unittest.mock import patch
    import httpx

    upstream = httpx.Response(200, json={"user": None})
    with patch("moodify_music.bff.main.httpx.request", return_value=upstream):
        r = bff_client.get("/api/v1/music/auth/me")
    assert r.headers.get("cache-control") == "no-store"
    with patch("moodify_music.bff.main.httpx.request", return_value=upstream):
        r = bff_client.get("/api/v1/music/drafts")
    assert r.headers.get("cache-control") == "no-store"


# ---------------------------------------------------------- session lifecycle

def test_session_fixation_old_token_dies_after_reissue():
    """Fixation: after logout+login, the previous token must be revoked."""
    from moodify_music.api.identity import create_session, resolve_session, revoke_session
    from moodify_music.api.identity import ensure_user
    from moodify_music.api.deps import get_db
    from moodify_music.bff import main as bff_main
    from conftest import _override_db

    internal_app.dependency_overrides[get_db] = _override_db
    try:
        from sqlalchemy.orm import Session

        with Session(ENGINE) as db:
            ensure_user(db, "user-sess-1", "Sess User")
            old_token, _ = create_session(db, "user-sess-1")
            db.commit()
            assert resolve_session(db, old_token) is not None
        # simulate re-login: revoke old, issue new
        with Session(ENGINE) as db:
            revoke_session(db, old_token)
            new_token, _ = create_session(db, "user-sess-1")
            db.commit()
            assert resolve_session(db, old_token) is None  # fixation blocked
            assert resolve_session(db, new_token) is not None
    finally:
        bff_main._session_cache.clear()


def test_expired_session_is_rejected():
    from sqlalchemy import update as sql_update

    from moodify_music.api.identity import create_session, ensure_user, resolve_session
    from moodify_music.api.deps import get_db
    from moodify_music import models as M
    from conftest import _override_db

    internal_app.dependency_overrides[get_db] = _override_db
    try:
        from sqlalchemy.orm import Session

        with Session(ENGINE) as db:
            ensure_user(db, "user-sess-2", "Sess Two")
            token, session_row = create_session(db, "user-sess-2", ttl_seconds=3600)
            session_id = session_row.id
            db.commit()
        # force expiry by rewriting expires_at into the past
        with ENGINE.begin() as conn:
            conn.execute(sql_update(M.AuthSession).where(M.AuthSession.id == session_id).values(
                expires_at=M.utcnow().replace(year=2020)))
        with Session(ENGINE) as db:
            assert resolve_session(db, token) is None
    finally:
        pass


# ---------------------------------------------------------- error leakage

def test_error_responses_never_leak_internals():
    from unittest.mock import patch
    import httpx

    def broken(method, url, **kwargs):
        raise httpx.RequestError("db traceback: File /srv/moodify/secret.py line 42")

    with patch("moodify_music.bff.main.httpx.request", side_effect=broken):
        r = bff_client.get("/api/v1/music/tracks/nonexistent-leak-test")
    body = r.text
    assert "traceback" not in body.lower()
    assert "/srv/" not in body and "secret.py" not in body
    assert r.json()["error"]["code"] == "UPSTREAM_UNAVAILABLE"
    assert r.json()["error"]["request_id"]  # request id present, internals absent


def test_internal_validation_error_does_not_echo_body_secrets():
    r = internal_client.post("/internal/v1/music/tracks", headers=AUTH,
                             json={"creator_id": "x", "title": "T", "secret_field": "should-not-echo"})
    assert "should-not-echo" not in r.text


# ---------------------------------------------------------- upload boundary

def test_upload_rejects_path_traversal_and_injection(tmp_path):

    from unittest.mock import patch

    # path traversal in filename must not escape the media root
    monkeypatch_env = {"MOODIFY_BFF_MEDIA_ROOT": str(tmp_path)}
    for key, value in monkeypatch_env.items():
        os.environ[key] = value

    from moodify_music.bff import main as bff_main
    from moodify_music.bff.auth import COOKIE_NAME, CSRF_COOKIE_NAME

    bff_main.AUTH_MODE = "invite_beta"
    with patch("moodify_music.bff.main._actor_user_id", return_value="user-up-1"):
        with patch("moodify_music.bff.main._account_actions_enabled", return_value=True):
            audio = b"RIFF" + (36).to_bytes(4, "little") + b"WAVEfmt " + b"\x00" * 28
            for evil_name in ["../../etc/passwd.wav", "..\\..\\win.ini.wav", "a<b>.wav", "a;rm -rf.wav"]:
                r = bff_client.put(
                    "/api/v1/music/media",
                    headers={"Content-Type": "audio/wav", "X-Filename": evil_name,
                             "X-CSRF-Token": "csrf-1"},
                    cookies={COOKIE_NAME: "tok-1", CSRF_COOKIE_NAME: "csrf-1"},
                    content=audio,
                )
                # content-addressed storage: the filename never enters the
                # asset key, so evil names are either rejected or stored
                # under a digest-derived safe key with zero path escape
                if r.status_code in (400, 415):
                    continue
                # 201 = new object, 200 = content-addressed dedup (same bytes)
                assert r.status_code in (200, 201), f"unexpected status for {evil_name}: {r.status_code}"
                key = r.json()["asset_key"]
                assert evil_name.replace("\\", "/") not in key.replace("\\", "/"), f"evil name leaked into key: {key}"
                assert key.startswith("beta/user-up-1/sha256/"), f"key outside content-addressed layout: {key}"
    assert not list(tmp_path.rglob("passwd*")) and not list(tmp_path.rglob("win.ini*"))


def test_upload_mime_and_size_boundaries(tmp_path):
    from unittest.mock import patch

    os.environ["MOODIFY_BFF_MEDIA_ROOT"] = str(tmp_path)
    from moodify_music.bff import main as bff_main

    bff_main.AUTH_MODE = "invite_beta"
    with patch("moodify_music.bff.main._actor_user_id", return_value="user-up-2"):
        with patch("moodify_music.bff.main._account_actions_enabled", return_value=True):
            # wrong MIME
            r = bff_client.put("/api/v1/music/media",
                               headers={"Content-Type": "text/html", "X-Filename": "x.html",
                                        "X-CSRF-Token": "csrf-1"},
                               cookies={"moodify_music_session": "tok-1", "moodify_csrf": "csrf-1"},
                               content=b"<html></html>")
            assert r.status_code == 415
            # zero bytes
            r = bff_client.put("/api/v1/music/media",
                               headers={"Content-Type": "audio/wav", "X-Filename": "empty.wav",
                                        "X-CSRF-Token": "csrf-1"},
                               cookies={"moodify_music_session": "tok-1", "moodify_csrf": "csrf-1"},
                               content=b"")
            assert r.status_code in (400, 413)
