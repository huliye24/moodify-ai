"""Moodify Mobile API v1 contract tests (DSK-MFY-ANDROID-003)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from moodify.api.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def test_health_ok(client: TestClient) -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["api_version"] == "0.1.0"
    assert body["min_client_version"] == "0.1.0"
    assert body["mode"] == "mobile-v1"
    assert body["server_time"]


def test_health_never_leaks_paths(client: TestClient) -> None:
    resp = client.get("/api/v1/health")
    text = resp.text
    assert "E:\\" not in text
    assert "C:" not in text
    assert "Traceback" not in text


def test_pair_issues_token(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/pair",
        json={"device_id": "android-test-device-1", "device_name": "Xiaomi 10"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token"]
    assert body["token_id"]
    assert body["api_version"] == "0.1.0"
    # url-safe base64 token, no padding issues
    assert all(c.isalnum() or c in "-_" for c in body["token"])


def test_pair_is_idempotent_per_device(client: TestClient) -> None:
    first = client.post("/api/v1/pair", json={"device_id": "android-idem"})
    second = client.post("/api/v1/pair", json={"device_id": "android-idem"})
    assert first.status_code == second.status_code == 200
    assert first.json()["token"] == second.json()["token"]


def test_pair_rejects_missing_device_id(client: TestClient) -> None:
    resp = client.post("/api/v1/pair", json={})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION"


def test_pair_rejects_non_json_body(client: TestClient) -> None:
    resp = client.post("/api/v1/pair", content="not json")
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION"


def test_pair_never_leaks_token_in_error(client: TestClient) -> None:
    resp = client.post("/api/v1/pair", json={})
    assert "token" not in resp.text.lower()


def test_revoke_own_token(client: TestClient) -> None:
    paired = client.post("/api/v1/pair", json={"device_id": "android-revoke"})
    token = paired.json()["token"]
    revoked = client.post(
        "/api/v1/pair/revoke", headers={"Authorization": f"Bearer {token}"}
    )
    assert revoked.status_code == 200
    assert revoked.json()["revoked"] is True
    # revoking again -> unknown token
    again = client.post(
        "/api/v1/pair/revoke", headers={"Authorization": f"Bearer {token}"}
    )
    assert again.status_code == 401
    assert again.json()["error"]["code"] == "UNAUTHORIZED"


def test_revoke_missing_token(client: TestClient) -> None:
    resp = client.post("/api/v1/pair/revoke")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


def test_capabilities(client: TestClient) -> None:
    resp = client.get("/api/v1/capabilities")
    assert resp.status_code == 200
    body = resp.json()
    assert body["api_version"] == "0.1.0"
    assert body["endpoints"]["health"] == "live"
    assert body["endpoints"]["pair"] == "live"
    assert body["endpoints"]["projects_create"] == "frozen"
    assert "presets" in body
    assert body["max_upload_bytes"] > 0
    assert body["auth"] == "bearer-token"


def test_business_endpoints_require_auth(client: TestClient) -> None:
    """projects/uploads/jobs/artifacts are live (DSK-MFY-DEMO-001) and gated."""
    cases = [
        ("post", "/api/v1/projects", {}),
        ("get", "/api/v1/projects/p1", None),
        ("post", "/api/v1/uploads", {}),
        ("get", "/api/v1/jobs/j1", None),
        ("post", "/api/v1/jobs/j1/cancel", None),
        ("get", "/api/v1/jobs/j1/result", None),
        ("get", "/api/v1/artifacts/a1", None),
        ("get", "/api/v1/artifacts/a1/download", None),
    ]
    for method, path, body in cases:
        resp = client.request(method, path, json=body)
        assert resp.status_code == 401, f"{method} {path}: {resp.status_code}"
        err = resp.json()["error"]
        assert err["code"] == "UNAUTHORIZED"
        assert err["request_id"]


def test_error_body_has_no_traceback(client: TestClient) -> None:
    resp = client.post("/api/v1/projects", json={})
    assert resp.status_code == 401
    assert "Traceback" not in resp.text
    assert "File \"" not in resp.text


def test_request_id_roundtrip(client: TestClient) -> None:
    rid = "req-abc-123"
    resp = client.post(
        "/api/v1/pair", json={}, headers={"X-Moodify-Request-Id": rid}
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["request_id"] == rid
