"""Identity & access-privacy tests — MFY_PLATFORM_IDENTITY_ACCESS_PRIVACY_001.

Two layers:
1. internal auth service (Hangzhou): session issue/validate/revoke/expiry.
2. public BFF (LA): server-authoritative actor, CSRF, CORS, no-store,
   no demo identity on the public path, login rate limiting.
"""

from __future__ import annotations

import os

os.environ["MOODIFY_INTERNAL_API_KEY"] = "test-service-key"

from unittest.mock import patch

import httpx
import pytest
from fastapi.testclient import TestClient

from conftest import ENGINE
from moodify_music import models as M
from moodify_music.api.main import app as internal_app
from moodify_music.bff import main as bff_main
from moodify_music.bff.auth import COOKIE_NAME, CSRF_COOKIE_NAME, csrf_token, csrf_valid
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
    bff_main._session_cache.clear()
    bff_main._login_attempts.clear()


# ---------------------------------------------------------------- internal

def test_issue_validate_revoke_roundtrip():
    created = internal_client.post("/internal/v1/music/auth/sessions", headers=AUTH, json={
        "user_id": "user-1", "display_name": "Ada",
    })
    assert created.status_code == 201
    body = created.json()
    token = body["token"]
    assert body["user"]["id"] == "user-1"
    assert len(token) >= 32

    validated = internal_client.post("/internal/v1/music/auth/validate", headers=AUTH, json={"token": token})
    assert validated.status_code == 200
    assert validated.json()["user"]["id"] == "user-1"

    import json as _json

    revoked = internal_client.request(
        "DELETE", "/internal/v1/music/auth/sessions",
        headers={**AUTH, "Content-Type": "application/json"},
        content=_json.dumps({"token": token}),
    )
    assert revoked.status_code == 200 and revoked.json()["revoked"] is True

    after = internal_client.post("/internal/v1/music/auth/validate", headers=AUTH, json={"token": token})
    assert after.status_code == 401
    assert after.json()["error"]["code"] == "SESSION_INVALID"


def test_expired_session_is_invalid(monkeypatch):
    monkeypatch.setattr("moodify_music.api.identity.utcnow", lambda: M.utcnow().replace(year=2030))
    body = internal_client.post("/internal/v1/music/auth/sessions", headers=AUTH, json={
        "user_id": "user-2", "display_name": "Grace",
    }).json()
    token = body["token"]
    monkeypatch.setattr("moodify_music.api.identity.utcnow", lambda: M.utcnow().replace(year=2031))
    r = internal_client.post("/internal/v1/music/auth/validate", headers=AUTH, json={"token": token})
    assert r.status_code == 401


def test_unknown_token_is_invalid():
    r = internal_client.post("/internal/v1/music/auth/validate", headers=AUTH, json={"token": "nope"})
    assert r.status_code == 401


def test_ensure_user_is_idempotent_and_never_claims_existing():
    a = internal_client.post("/internal/v1/music/auth/ensure-user", headers=AUTH, json={
        "user_id": "user-3", "display_name": "Linus",
    })
    assert a.status_code == 201
    b = internal_client.post("/internal/v1/music/auth/ensure-user", headers=AUTH, json={
        "user_id": "user-3", "display_name": "Impostor",
    })
    assert b.status_code == 201
    assert a.json()["display_name"] == b.json()["display_name"] == "Linus"
    c = internal_client.post("/internal/v1/music/auth/ensure-user", headers=AUTH, json={"user_id": "user-new"})
    assert c.status_code == 422  # unknown id without display name must not be claimed


def test_auth_endpoints_require_service_key():
    r = internal_client.post("/internal/v1/music/auth/sessions", json={"user_id": "x", "display_name": "x"})
    assert r.status_code == 401


# ---------------------------------------------------------------- bff auth

def _set_invite_beta(monkeypatch):
    monkeypatch.setattr(bff_main, "AUTH_MODE", "invite_beta")


def _upstream_ok(monkeypatch, payload: dict, status: int = 201):
    monkeypatch.setattr(
        bff_main, "httpx",
        type("H", (), {"request": staticmethod(lambda *a, **k: httpx.Response(status, json=payload))}),
    )


def _upstream_recording(monkeypatch, payload: dict, status: int = 200, session_user: dict | None = None):
    seen = {}
    def fake_request(method, url, **kwargs):
        seen["method"] = method
        seen["url"] = url
        seen["json"] = kwargs.get("json")
        seen["headers"] = kwargs.get("headers") or {}
        if session_user is not None and url.endswith("/auth/validate"):
            return httpx.Response(200, json={"user": session_user})
        return httpx.Response(status, json=payload)
    monkeypatch.setattr(bff_main, "httpx", type("H", (), {"request": staticmethod(fake_request)}))
    return seen


def test_default_public_path_is_anonymous_without_demo_identity():
    assert bff_main.AUTH_MODE == "anonymous"
    body = bff_client.get("/api/v1/music/bootstrap").json()
    assert body["auth_state"] == "PUBLIC_ANONYMOUS_READ"
    assert "demo_creator_handle" not in body
    assert body["capabilities"] == {"account_actions": False, "creator_writes": False}


def test_login_sets_httponly_secure_samesite_session_and_csrf_cookies(monkeypatch):
    import hashlib

    _set_invite_beta(monkeypatch)
    digest = hashlib.sha256(b"code").hexdigest()
    _upstream_ok(monkeypatch, {"user": {"id": "user-1", "display_name": "Ada"}})
    monkeypatch.setenv("MOODIFY_BFF_BETA_INVITES", f'{{"{digest}": "user-1"}}')
    r = bff_client.post("/api/v1/music/session", json={"invite_code": "code"})
    assert r.status_code == 200
    session_cookie = r.headers.get("set-cookie", "")
    assert COOKIE_NAME in session_cookie and "HttpOnly" in session_cookie and "Secure" in session_cookie and "SameSite=lax" in session_cookie
    assert CSRF_COOKIE_NAME in r.headers.get("set-cookie", "")
    assert r.json()["user"]["id"] == "user-1"


def test_login_rate_limited(monkeypatch):
    import hashlib

    _set_invite_beta(monkeypatch)
    digest = hashlib.sha256(b"code").hexdigest()
    monkeypatch.setenv("MOODIFY_BFF_BETA_INVITES", f'{{"{digest}": "user-1"}}')
    for _ in range(5):
        r = bff_client.post("/api/v1/music/session", json={"invite_code": "wrong"})
        assert r.status_code == 401
    r = bff_client.post("/api/v1/music/session", json={"invite_code": "wrong"})
    assert r.status_code == 429


def test_logout_revokes_session_and_clears_cookies(monkeypatch):
    _set_invite_beta(monkeypatch)
    seen = _upstream_recording(monkeypatch, {"revoked": True})
    r = bff_client.delete("/api/v1/music/session", cookies={COOKIE_NAME: "tok-1", CSRF_COOKIE_NAME: "csrf-1"}, headers={"X-CSRF-Token": "csrf-1"})
    assert r.status_code == 200
    assert seen["method"] == "DELETE" and seen["json"] == {"token": "tok-1"}
    set_cookie = r.headers.get("set-cookie", "")
    assert COOKIE_NAME in set_cookie and "Max-Age=0" in set_cookie


def test_me_resolves_actor_from_session_only(monkeypatch):
    _set_invite_beta(monkeypatch)
    _upstream_ok(monkeypatch, {"user": {"id": "user-1"}}, status=200)
    r = bff_client.get("/api/v1/music/auth/me", cookies={COOKIE_NAME: "tok-1"})
    assert r.status_code == 200 and r.json()["user"]["id"] == "user-1"
    r = bff_client.get("/api/v1/music/auth/me")
    assert r.status_code == 200 and r.json()["user"] is None


def test_actor_spoof_header_is_ignored(monkeypatch):
    # client-supplied actor header must never become the upstream actor
    _set_invite_beta(monkeypatch)
    seen = _upstream_recording(monkeypatch, {"following": True}, session_user={"id": "session-user"})
    r = bff_client.put(
        "/api/v1/music/users/session-user/follows/c1",
        headers={"X-CSRF-Token": "csrf-1", "X-Moodify-Actor-User-Id": "forged"},
        cookies={COOKIE_NAME: "tok-1", CSRF_COOKIE_NAME: "csrf-1"},
        json={},
    )
    assert r.status_code == 200
    # the actor is resolved server-side from the session, never from the
    # client-supplied "forged" header
    assert seen["url"].endswith("/internal/v1/music/users/session-user/follows/c1")
    assert seen["headers"].get("X-Moodify-Actor-User-Id") == "session-user"


# ---------------------------------------------------------------- csrf/cors/cache

def test_state_changing_requires_csrf(monkeypatch):
    _set_invite_beta(monkeypatch)
    upstream = httpx.Response(200, json={"id": "track-1"})
    with patch("moodify_music.bff.main.httpx.request", return_value=upstream):
        r = bff_client.post("/api/v1/music/tracks", json={"creator_id": "c1", "title": "t"}, cookies={COOKIE_NAME: "tok-1"})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "CSRF_INVALID"


def test_csrf_valid_matches_token():
    token = csrf_token()
    assert csrf_valid(token, token) is True
    assert csrf_valid(token, "other") is False
    assert csrf_valid(None, token) is False


def test_cors_exact_origin_only(monkeypatch):
    monkeypatch.setattr(bff_main, "CORS_ORIGINS", ["https://listen.moodify.example"])
    disallowed = bff_client.get("/api/v1/music/catalogue", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in disallowed.headers
    allowed = bff_client.get("/api/v1/music/catalogue", headers={"Origin": "https://listen.moodify.example"})
    assert allowed.headers.get("access-control-allow-origin") == "https://listen.moodify.example"
    assert allowed.headers.get("access-control-allow-credentials") == "true"


def test_private_paths_and_set_cookie_responses_are_no_store(monkeypatch):
    _set_invite_beta(monkeypatch)
    _upstream_ok(monkeypatch, {"user": {"id": "u1"}}, status=200)
    r = bff_client.get("/api/v1/music/auth/me", cookies={COOKIE_NAME: "tok-1"})
    assert r.headers.get("cache-control") == "no-store"
    r = bff_client.post("/api/v1/music/session", json={"invite_code": "x"}, cookies={})
    assert r.headers.get("cache-control") == "no-store"


def test_public_catalogue_is_cacheable():
    with patch("moodify_music.bff.main.httpx.request", return_value=httpx.Response(200, json={"items": []})):
        r = bff_client.get("/api/v1/music/catalogue")
    assert r.headers.get("cache-control") != "no-store"
