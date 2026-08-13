from __future__ import annotations

from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

from moodify_music.bff.main import app
from moodify_music.bff.auth import authenticate_invite, issue_session, verify_session


client = TestClient(app)


def test_bootstrap_contract_is_flat_and_marks_demo_auth():
    response = client.get("/api/v1/music/bootstrap")
    assert response.status_code == 200
    body = response.json()
    assert "user" not in body
    assert body["auth_state"] == "PUBLIC_USER_AUTH_NOT_PRODUCTION_READY"
    assert "id" in body
    assert body["capabilities"] == {"account_actions": False, "creator_writes": False}


def test_write_body_and_idempotency_key_are_forwarded(monkeypatch):
    monkeypatch.setattr("moodify_music.bff.main._account_actions_enabled", lambda request: True)
    monkeypatch.setattr("moodify_music.bff.main._actor_user_id", lambda request: "user-1")
    upstream = httpx.Response(200, json={"id": "track-1", "status": "draft"})
    with patch("moodify_music.bff.main.httpx.request", return_value=upstream) as request:
        response = client.post(
            "/api/v1/music/tracks",
            headers={"Idempotency-Key": "idem-track-1"},
            json={"creator_id": "creator-1", "title": "Signal"},
        )
    assert response.status_code == 200
    assert request.call_args.kwargs["json"] == {"creator_id": "creator-1", "title": "Signal"}
    assert request.call_args.kwargs["headers"]["Idempotency-Key"] == "idem-track-1"


def test_empty_object_write_body_is_forwarded(monkeypatch):
    monkeypatch.setattr("moodify_music.bff.main._account_actions_enabled", lambda request: True)
    monkeypatch.setattr("moodify_music.bff.main._actor_user_id", lambda request: "u1")
    upstream = httpx.Response(200, json={"following": True})
    with patch("moodify_music.bff.main.httpx.request", return_value=upstream) as request:
        response = client.put("/api/v1/music/users/u1/follows/c1", json={})
    assert response.status_code == 200
    assert request.call_args.kwargs["json"] == {}


def test_non_json_upstream_error_is_normalized_without_leaking_body(monkeypatch):
    monkeypatch.setattr("moodify_music.bff.main._account_actions_enabled", lambda request: True)
    monkeypatch.setattr("moodify_music.bff.main._actor_user_id", lambda request: "user-1")
    upstream = httpx.Response(500, text="database traceback must not reach clients")
    with patch("moodify_music.bff.main.httpx.request", return_value=upstream):
        response = client.post("/api/v1/music/tracks", json={"title": "Probe"})
    assert response.status_code == 502
    body = response.json()["error"]
    assert body["code"] == "UPSTREAM_INVALID_RESPONSE"
    assert body["upstream_status"] == 500
    assert "traceback" not in response.text


def test_public_actor_header_is_never_forwarded(monkeypatch):
    monkeypatch.setattr("moodify_music.bff.main._account_actions_enabled", lambda request: True)
    monkeypatch.setattr("moodify_music.bff.main._actor_user_id", lambda request: "server-demo-user")
    upstream = httpx.Response(200, json={"id": "track-1"})
    with patch("moodify_music.bff.main.httpx.request", return_value=upstream) as request:
        client.post(
            "/api/v1/music/tracks",
            headers={"X-Moodify-Actor-User-Id": "attacker"},
            json={"creator_id": "creator-1", "title": "Signal"},
        )
    assert request.call_args.kwargs["headers"]["X-Moodify-Actor-User-Id"] == "server-demo-user"


def test_user_scoped_route_rejects_path_identity_mismatch(monkeypatch):
    monkeypatch.setattr("moodify_music.bff.main._account_actions_enabled", lambda request: True)
    monkeypatch.setattr("moodify_music.bff.main._actor_user_id", lambda request: "server-demo-user")
    response = client.put(
        "/api/v1/music/users/attacker/favorites/track-1",
        headers={"X-Moodify-Actor-User-Id": "attacker"},
        json={},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "OWNERSHIP_DENIED"


def test_demo_mode_locks_creator_and_account_actions(monkeypatch):
    monkeypatch.setattr("moodify_music.bff.main.AUTH_MODE", "demo_read_only")
    monkeypatch.setattr("moodify_music.bff.main.DEMO_USER_ID", "demo-user")
    create = client.post("/api/v1/music/tracks", json={"creator_id": "c1", "title": "No"})
    favorite = client.put("/api/v1/music/users/demo-user/favorites/t1", json={})
    inbox = client.get("/api/v1/music/creators/c1/license-intents")
    assert {create.status_code, favorite.status_code, inbox.status_code} == {503}
    assert create.json()["error"]["code"] == "BETA_AUTH_REQUIRED"


def test_resource_routes_are_not_decorated_with_shared_static_cache_keys():
    routes = {route.path: route.endpoint for route in app.routes if hasattr(route, "endpoint")}
    assert not hasattr(routes["/api/v1/music/tracks/{track_id}"], "__wrapped__")
    assert not hasattr(routes["/api/v1/music/creators/{creator_id}/license-intents"], "__wrapped__")


def test_invite_session_is_signed_and_expires(monkeypatch):
    import hashlib
    import json

    code = "beta-code-for-test"
    monkeypatch.setenv("MOODIFY_BFF_SESSION_SECRET", "s" * 32)
    monkeypatch.setenv("MOODIFY_BFF_BETA_INVITES", json.dumps({hashlib.sha256(code.encode()).hexdigest(): "user-1"}))
    assert authenticate_invite(code) == "user-1"
    token = issue_session("user-1", now=1000)
    assert verify_session(token, now=1001) == "user-1"
    assert verify_session(token + "tampered", now=1001) is None
    assert verify_session(token, now=1000 + 12 * 60 * 60) is None


def test_invite_login_sets_hardened_cookie(monkeypatch):
    import hashlib
    import json

    code = "beta-login-test"
    monkeypatch.setattr("moodify_music.bff.main.AUTH_MODE", "invite_beta")
    monkeypatch.setenv("MOODIFY_BFF_SESSION_SECRET", "x" * 32)
    monkeypatch.setenv("MOODIFY_BFF_BETA_INVITES", json.dumps({hashlib.sha256(code.encode()).hexdigest(): "user-1"}))
    response = client.post("/api/v1/music/session", json={"invite_code": code})
    cookie = response.headers["set-cookie"].lower()
    assert response.status_code == 200
    assert "httponly" in cookie and "secure" in cookie and "samesite=lax" in cookie


def test_authenticated_audio_upload_is_scoped_and_hashed(monkeypatch, tmp_path):
    import hashlib

    monkeypatch.setenv("MOODIFY_BFF_MEDIA_ROOT", str(tmp_path))
    monkeypatch.setattr("moodify_music.bff.main._account_actions_enabled", lambda request: True)
    monkeypatch.setattr("moodify_music.bff.main._actor_user_id", lambda request: "user-1")
    audio = b"RIFF" + (36).to_bytes(4, "little") + b"WAVEfmt " + b"\x00" * 28
    response = client.put(
        "/api/v1/music/media",
        headers={"Content-Type": "audio/wav", "X-Filename": "My Song.wav"},
        content=audio,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["asset_key"].startswith("beta/user-1/")
    assert body["asset_key"].endswith("/My-Song.wav")
    assert body["sha256"] == hashlib.sha256(audio).hexdigest()
    assert (tmp_path / body["asset_key"]).read_bytes() == audio


def test_audio_upload_rejects_spoofed_signature_and_removes_temp(monkeypatch, tmp_path):
    monkeypatch.setenv("MOODIFY_BFF_MEDIA_ROOT", str(tmp_path))
    monkeypatch.setattr("moodify_music.bff.main._account_actions_enabled", lambda request: True)
    monkeypatch.setattr("moodify_music.bff.main._actor_user_id", lambda request: "user-1")
    response = client.put(
        "/api/v1/music/media",
        headers={"Content-Type": "audio/wav", "X-Filename": "fake.wav"},
        content=b"this is not a wave file",
    )
    assert response.status_code == 415
    assert response.json()["error"]["code"] == "AUDIO_SIGNATURE_INVALID"
    assert not list(tmp_path.rglob(".upload-*"))
