"""Public Moodify 1.0 API contract."""

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from moodify.api.main import app


def test_release_identity_and_routes():
    client = TestClient(app)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["version"] == "1.0.0-rc.1"
    paths = {route.path for route in app.routes if isinstance(route, APIRoute)}
    assert "/api/v1/auditory/analyze" in paths
    assert "/api/v1/auditory/cases/{case_id}" in paths
    assert "/process" not in paths
    assert not any("feed" in path or "cwc" in path or "marketplace" in path for path in paths)


def test_missing_case_is_typed_and_private_path_free(tmp_path, monkeypatch):
    monkeypatch.setenv("MOODIFY_CASES_ROOT", str(tmp_path))
    response = TestClient(app).get("/api/v1/auditory/cases/case_" + "0" * 32)
    assert response.status_code == 404
    body = response.json()
    assert body["detail"]["code"] == "CASE_NOT_FOUND"
    assert str(tmp_path) not in response.text
