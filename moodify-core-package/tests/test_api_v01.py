"""Smoke tests for Moodify v01 FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from moodify.api.main import app

pytestmark = pytest.mark.skip(
    reason="Auditory Intervention Laboratory API is outside the Moodify 1.0 default surface",
)


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.mark.v01
def test_api_health_returns_v01_mainline(client):
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"
    assert data["mode"] == "v01"
    assert data["mainline"] == "v01_pipeline"


@pytest.mark.v01
def test_api_presets_returns_three_v01_presets(client):
    response = client.get("/presets")
    assert response.status_code == 200

    data = response.json()
    assert data["version"] == "0.1.0"
    assert data["mode"] == "v01"
    assert data["default"] == "clean_master"

    presets = data["presets"]
    assert isinstance(presets, list)
    assert len(presets) == 3

    keys = {p["key"] for p in presets}
    assert keys == {"warm_vocal", "clean_master", "wide_space"}

    for p in presets:
        assert "name" in p
        assert "name_zh" in p
        assert "description" in p


@pytest.mark.v01
def test_api_process_rejects_invalid_preset(client, mock_wav):
    with open(mock_wav, "rb") as f:
        response = client.post(
            "/process",
            files={"audio": ("test.wav", f, "audio/wav")},
            data={"preset": "not_a_real_preset"},
        )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "Unknown preset" in detail["error"]


@pytest.mark.v01
def test_api_process_returns_wav_for_clean_master(client, mock_wav):
    with open(mock_wav, "rb") as f:
        response = client.post(
            "/process",
            files={"audio": ("test.wav", f, "audio/wav")},
            data={"preset": "clean_master"},
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/wav")
    assert len(response.content) > 0


@pytest.mark.v01
def test_api_process_accepts_all_v01_presets(client, mock_wav):
    for preset in ["warm_vocal", "clean_master", "wide_space"]:
        with open(mock_wav, "rb") as f:
            response = client.post(
                "/process",
                files={"audio": ("test.wav", f, "audio/wav")},
                data={"preset": preset},
            )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("audio/wav")
        assert len(response.content) > 0
