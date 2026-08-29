"""Contract tests for the experimental auditory-intelligence API facade."""

from fastapi.testclient import TestClient

from moodify.api.main import app


def test_intelligence_routes_are_registered():
    paths = {route.path for route in app.routes}

    assert "/api/v1/intelligence/analyze" in paths
    assert "/api/v1/intelligence/evaluate" in paths
    assert "/api/v1/intelligence/process" in paths


def test_process_route_is_explicitly_reserved():
    response = TestClient(app).post(
        "/api/v1/intelligence/process",
        files={"audio": ("test.wav", b"placeholder", "audio/wav")},
    )

    assert response.status_code == 501
    assert response.json()["status"] == "NOT_IMPLEMENTED"


def test_analyze_route_returns_basic_acoustic_features(mock_wav):
    with open(mock_wav, "rb") as handle:
        response = TestClient(app).post(
            "/api/v1/intelligence/analyze",
            files={"audio": ("test.wav", handle, "audio/wav")},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["duration"] == 10.0
    assert payload["format"] == "wav"
    assert {"spectrum", "dynamics", "stereo"} <= set(payload["features"])


def test_evaluate_route_requires_explicit_mrs_features(mock_wav):
    with open(mock_wav, "rb") as handle:
        response = TestClient(app).post(
            "/api/v1/intelligence/evaluate",
            files={"audio": ("test.wav", handle, "audio/wav")},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["score"] is None
    assert payload["status"] == "FEATURES_REQUIRED"
