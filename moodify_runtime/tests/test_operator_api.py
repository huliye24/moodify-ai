"""Tests for operator_api."""
import pytest
from fastapi.testclient import TestClient
from moodify_runtime.operator_api import _get_app

@pytest.fixture
def client():
    return TestClient(_get_app())

class TestApp:
    def test_title(self):
        app = _get_app()
        assert app.title is not None
    def test_routes(self):
        app = _get_app()
        assert len(app.routes) > 0
    def test_openapi(self):
        app = _get_app()
        assert "paths" in app.openapi()

class TestEndpoints:
    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
    def test_list_jobs(self, client):
        r = client.get("/operator/jobs")
        assert r.status_code == 200
    def test_create_job(self, client):
        r = client.post("/operator/jobs", json={
            "sample_id": "test-001", "preset": "warm_vocal", "genre": "pop"})
        assert r.status_code in (200, 201, 422)
    def test_runtime_status(self, client):
        r = client.get("/runtime/status")
        assert r.status_code == 200
    def test_heartbeat(self, client):
        r = client.get("/runtime/heartbeat")
        assert r.status_code == 200
    def test_studio_status(self, client):
        r = client.get("/studio-os/status")
        assert r.status_code == 200
