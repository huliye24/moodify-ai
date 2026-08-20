"""API surface tests (MFY-CR-P08)."""

from __future__ import annotations


import pytest
from fastapi.testclient import TestClient

from moodify.api.main import app

pytestmark = pytest.mark.v01

CLIENT = TestClient(app)


@pytest.fixture(autouse=True)
def _isolated_state(tmp_path, monkeypatch):
    monkeypatch.setenv("MOODIFY_RECON_WORKSPACE_ROOT", str(tmp_path / "ws"))
    monkeypatch.setenv("MOODIFY_RECON_DB", str(tmp_path / "jobs.db"))
    monkeypatch.setenv("MOODIFY_AUTH_MODE", "single_user")
    monkeypatch.setenv("MOODIFY_AUDIO_TOKEN_SECRET", "test-secret")


def _upload(path, headers=None, **form):
    from pathlib import Path as _P
    with open(path, "rb") as fh:
        return CLIENT.post(
            "/api/v1/reconstruction/jobs",
            files={"source": (_P(path).name, fh, "audio/wav")},
            data=form or None,
            headers=headers or {},
        )


def test_capabilities():
    resp = CLIENT.get("/api/v1/reconstruction/capabilities")
    assert resp.status_code == 200
    body = resp.json()
    assert body["api_version"] == "v0.1"
    assert ".wav" in body["supported_formats"]
    assert body["stems_available"] is False
    assert body["reconstruction_mode"] == ["auto"]


def test_create_job(lowpass_wav):
    resp = _upload(lowpass_wav)
    assert resp.status_code == 202
    body = resp.json()
    assert body["idempotency"] == "CREATED"
    assert body["job"]["status"] == "QUEUED"
    assert body["job"]["progress"] == "Preparing"
    # product view hides internals
    assert "workspace_path" not in body["job"]
    assert "source_asset_id" not in body["job"]


def test_engineering_params_rejected(lowpass_wav):
    resp = _upload(lowpass_wav, reconstruction_mode="manual")
    assert resp.status_code == 400
    resp = _upload(lowpass_wav, training_permission="true")
    assert resp.status_code == 400
    resp = _upload(lowpass_wav, public_demo_permission="true")
    assert resp.status_code == 400


def test_unsupported_type_rejected(tmp_path):
    bogus = tmp_path / "song.txt"
    bogus.write_text("x")
    resp = _upload(bogus)
    assert resp.status_code == 415


def test_job_status_and_result_projection(lowpass_wav, empty_store):
    created = _upload(lowpass_wav).json()
    job_id = created["job"]["job_id"]
    resp = CLIENT.get(f"/api/v1/reconstruction/jobs/{job_id}")
    assert resp.status_code == 200
    assert resp.json()["job"]["status"] == "QUEUED"
    # result not ready yet
    assert CLIENT.get(f"/api/v1/reconstruction/jobs/{job_id}/result").status_code == 409


def test_cancel_queued_job(lowpass_wav):
    job_id = _upload(lowpass_wav).json()["job"]["job_id"]
    resp = CLIENT.post(f"/api/v1/reconstruction/jobs/{job_id}/cancel")
    assert resp.status_code == 202
    assert resp.json()["job"]["status"] == "CANCELLED"
    # terminal: second cancel refused
    assert CLIENT.post(f"/api/v1/reconstruction/jobs/{job_id}/cancel").status_code == 409


def test_unknown_job_404(lowpass_wav):
    assert CLIENT.get("/api/v1/reconstruction/jobs/job_nope").status_code == 404
    assert CLIENT.post("/api/v1/reconstruction/jobs/job_nope/cancel").status_code == 404
    assert CLIENT.get("/api/v1/reconstruction/jobs/job_nope/result").status_code == 404


def test_full_flow_via_worker(lowpass_wav, tmp_path):
    """Upload -> worker runs -> result available with short-lived audio token."""
    from moodify.reconstruction_job.worker import WorkerConfig, run_once
    created = _upload(lowpass_wav).json()
    job_id = created["job"]["job_id"]
    config = WorkerConfig(
        db_path=tmp_path / "jobs.db",
        workspace_root=tmp_path / "ws",
        poll_seconds=0.0,
    )
    assert run_once(config) == 1
    status = CLIENT.get(f"/api/v1/reconstruction/jobs/{job_id}").json()["job"]["status"]
    assert status in ("SUCCEEDED", "SOURCE_WINS", "HUMAN_REQUIRED")
    if status in ("SUCCEEDED", "SOURCE_WINS"):
        result = CLIENT.get(f"/api/v1/reconstruction/jobs/{job_id}/result").json()["result"]
        assert result["selected_candidate"] in ("SOURCE", "A", "B", "C")
        assert "audio_url" in result
        audio_url = result["audio_url"].split("?")[0] + "?" + result["audio_url"].split("?")[1]
        resp = CLIENT.get(audio_url)
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "audio/wav"
