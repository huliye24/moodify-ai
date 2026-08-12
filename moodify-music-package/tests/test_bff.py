from __future__ import annotations

from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

from moodify_music.bff.main import app


client = TestClient(app)


def test_bootstrap_contract_is_flat_and_marks_demo_auth():
    response = client.get("/api/v1/music/bootstrap")
    assert response.status_code == 200
    body = response.json()
    assert "user" not in body
    assert body["auth_state"] == "PUBLIC_USER_AUTH_NOT_PRODUCTION_READY"
    assert "id" in body


def test_write_body_and_idempotency_key_are_forwarded():
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


def test_empty_object_write_body_is_forwarded():
    upstream = httpx.Response(200, json={"following": True})
    with patch("moodify_music.bff.main.httpx.request", return_value=upstream) as request:
        response = client.put("/api/v1/music/users/u1/follows/c1", json={})
    assert response.status_code == 200
    assert request.call_args.kwargs["json"] == {}


def test_non_json_upstream_error_is_normalized_without_leaking_body():
    upstream = httpx.Response(500, text="database traceback must not reach clients")
    with patch("moodify_music.bff.main.httpx.request", return_value=upstream):
        response = client.post("/api/v1/music/tracks", json={"title": "Probe"})
    assert response.status_code == 502
    body = response.json()["error"]
    assert body["code"] == "UPSTREAM_INVALID_RESPONSE"
    assert body["upstream_status"] == 500
    assert "traceback" not in response.text
