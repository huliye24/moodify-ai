"""Contract tests for the experimental auditory-intelligence API facade."""

from fastapi.testclient import TestClient

from moodify.api.main import app


def test_intelligence_routes_are_registered():
    paths = {route.path for route in app.routes}

    assert "/api/v1/intelligence/analyze" in paths
    assert "/api/v1/intelligence/evaluate" in paths
    assert "/api/v1/intelligence/process" in paths


def test_health_exposes_current_identity_without_claiming_judge_one_exists():
    payload = TestClient(app).get("/api/v1/health").json()

    assert payload["identity"] == "Moodify Cloud — Audio Intelligence"
    assert payload["judge"]["model"] == "Judge-1"
    assert payload["judge"]["status"] == "NOT_IMPLEMENTED"


def test_ai_chat_fails_explicitly_when_model_is_unavailable(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    response = TestClient(app).post("/api/v1/ai/chat", json={"message": "这首歌发生了什么？"})

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "MODEL_UNAVAILABLE"


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
