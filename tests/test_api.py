"""Repository-level API smoke tests."""

from fastapi.testclient import TestClient

from moodify.api.main import app


def test_experimental_api_routes_are_registered_and_process_is_explicit():
    client = TestClient(app)
    paths = {route.path for route in app.routes}

    assert "/api/v1/intelligence/analyze" in paths
    response = client.post(
        "/api/v1/intelligence/process",
        files={"audio": ("fixture.wav", b"placeholder", "audio/wav")},
    )
    assert response.status_code == 501
    assert response.json()["status"] == "NOT_IMPLEMENTED"
