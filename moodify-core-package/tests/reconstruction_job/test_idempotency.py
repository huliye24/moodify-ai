"""Idempotency tests (MFY-CR-P08)."""

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


def _upload(path, headers=None):
    with open(path, "rb") as fh:
        return CLIENT.post(
            "/api/v1/reconstruction/jobs",
            files={"source": ("song.wav", fh, "audio/wav")},
            headers=headers or {},
        )


def test_same_idempotency_key_returns_existing(lowpass_wav):
    first = _upload(lowpass_wav, headers={"Idempotency-Key": "net-retry-1"})
    second = _upload(lowpass_wav, headers={"Idempotency-Key": "net-retry-1"})
    assert first.status_code == 202
    assert second.status_code == 200
    assert second.json()["idempotency"] == "RETURN_EXISTING"
    assert first.json()["job"]["job_id"] == second.json()["job"]["job_id"]


def test_different_keys_create_distinct_jobs(lowpass_wav):
    a = _upload(lowpass_wav, headers={"Idempotency-Key": "k1"})
    b = _upload(lowpass_wav, headers={"Idempotency-Key": "k2"})
    assert a.json()["job"]["job_id"] != b.json()["job"]["job_id"]


def test_duplicate_after_success_returns_existing(lowpass_wav, tmp_path):
    created = _upload(lowpass_wav).json()
    job_id = created["job"]["job_id"]
    from moodify.reconstruction_job.worker import WorkerConfig, run_once
    run_once(WorkerConfig(db_path=tmp_path / "jobs.db", workspace_root=tmp_path / "ws"))
    # same owner + same sha256 + same version, no key -> RETURN_EXISTING
    again = _upload(lowpass_wav)
    assert again.json()["idempotency"] == "RETURN_EXISTING"
    assert again.json()["job"]["job_id"] == job_id


def test_rebuild_header_creates_new_job(lowpass_wav, tmp_path):
    created = _upload(lowpass_wav).json()
    job_id = created["job"]["job_id"]
    from moodify.reconstruction_job.worker import WorkerConfig, run_once
    run_once(WorkerConfig(db_path=tmp_path / "jobs.db", workspace_root=tmp_path / "ws"))
    rebuilt = _upload(lowpass_wav, headers={"X-Moodify-Rebuild": "true"})
    assert rebuilt.json()["idempotency"] == "CREATED"
    assert rebuilt.json()["job"]["job_id"] != job_id
