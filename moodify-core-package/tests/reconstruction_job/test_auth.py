"""Authorization tests (MFY-CR-P08): owner boundary + short-lived tokens."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from moodify.api.main import app
from moodify.reconstruction_job.auth import issue_audio_token

pytestmark = pytest.mark.v01

CLIENT = TestClient(app)


@pytest.fixture(autouse=True)
def _isolated_state(tmp_path, monkeypatch):
    monkeypatch.setenv("MOODIFY_RECON_WORKSPACE_ROOT", str(tmp_path / "ws"))
    monkeypatch.setenv("MOODIFY_RECON_DB", str(tmp_path / "jobs.db"))
    monkeypatch.setenv("MOODIFY_AUTH_MODE", "owner")
    monkeypatch.setenv("MOODIFY_AUDIO_TOKEN_SECRET", "test-secret")


def _upload_as(owner, path, headers=None):
    with open(path, "rb") as fh:
        return CLIENT.post(
            "/api/v1/reconstruction/jobs",
            files={"source": ("song.wav", fh, "audio/wav")},
            headers={"X-Moodify-Actor-User-Id": owner, **(headers or {})},
        )


def test_owner_mode_requires_actor_header(lowpass_wav):
    resp = _upload_as("", lowpass_wav)
    assert resp.status_code == 401


def test_owner_can_read_own_job(lowpass_wav):
    job_id = _upload_as("user-a", lowpass_wav).json()["job"]["job_id"]
    resp = CLIENT.get(
        f"/api/v1/reconstruction/jobs/{job_id}",
        headers={"X-Moodify-Actor-User-Id": "user-a"},
    )
    assert resp.status_code == 200


def test_cross_owner_denied_as_404(lowpass_wav):
    job_id = _upload_as("user-a", lowpass_wav).json()["job"]["job_id"]
    resp = CLIENT.get(
        f"/api/v1/reconstruction/jobs/{job_id}",
        headers={"X-Moodify-Actor-User-Id": "user-b"},
    )
    assert resp.status_code == 404
    resp = CLIENT.post(
        f"/api/v1/reconstruction/jobs/{job_id}/cancel",
        headers={"X-Moodify-Actor-User-Id": "user-b"},
    )
    assert resp.status_code == 404


def test_token_valid_flow(lowpass_wav, tmp_path):
    job_id = _upload_as("user-a", lowpass_wav).json()["job"]["job_id"]
    token = issue_audio_token(job_id, "user-a")
    resp = CLIENT.get(
        f"/api/v1/reconstruction/jobs/{job_id}/result/audio",
        params={"token": token},
        headers={"X-Moodify-Actor-User-Id": "user-a"},
    )
    # job not finished yet -> 404 result; token itself validated owner-side
    assert resp.status_code in (404, 409)


def test_token_cross_owner_denied(lowpass_wav):
    job_id = _upload_as("user-a", lowpass_wav).json()["job"]["job_id"]
    token = issue_audio_token(job_id, "user-b")  # forged for another owner
    resp = CLIENT.get(
        f"/api/v1/reconstruction/jobs/{job_id}/result/audio",
        params={"token": token},
        headers={"X-Moodify-Actor-User-Id": "user-a"},
    )
    assert resp.status_code == 403


def test_expired_token_denied(lowpass_wav, monkeypatch):
    job_id = _upload_as("user-a", lowpass_wav).json()["job"]["job_id"]
    import moodify.reconstruction_job.auth as auth_mod
    monkeypatch.setattr(auth_mod, "AUDIO_TOKEN_TTL_S", -60)
    token = issue_audio_token(job_id, "user-a")
    resp = CLIENT.get(
        f"/api/v1/reconstruction/jobs/{job_id}/result/audio",
        params={"token": token},
        headers={"X-Moodify-Actor-User-Id": "user-a"},
    )
    assert resp.status_code == 401


def test_garbage_token_rejected(lowpass_wav):
    job_id = _upload_as("user-a", lowpass_wav).json()["job"]["job_id"]
    resp = CLIENT.get(
        f"/api/v1/reconstruction/jobs/{job_id}/result/audio",
        params={"token": "garbage"},
        headers={"X-Moodify-Actor-User-Id": "user-a"},
    )
    assert resp.status_code == 401


def test_missing_secret_fails_closed(lowpass_wav, monkeypatch, tmp_path):
    job_id = _upload_as("user-a", lowpass_wav).json()["job"]["job_id"]
    from moodify.reconstruction_job.worker import WorkerConfig, run_once
    run_once(WorkerConfig(db_path=tmp_path / "jobs.db", workspace_root=tmp_path / "ws"))
    status = CLIENT.get(
        f"/api/v1/reconstruction/jobs/{job_id}",
        headers={"X-Moodify-Actor-User-Id": "user-a"},
    ).json()["job"]["status"]
    if status not in ("SUCCEEDED", "SOURCE_WINS"):
        pytest.skip("job did not auto-finalize; token path not exercised")
    monkeypatch.delenv("MOODIFY_AUDIO_TOKEN_SECRET")
    resp = CLIENT.get(
        f"/api/v1/reconstruction/jobs/{job_id}/result",
        headers={"X-Moodify-Actor-User-Id": "user-a"},
    )
    assert resp.status_code == 500
    assert resp.json()["detail"]["code"] == "TOKEN_SECRET_MISSING"


def test_single_user_mode_default(monkeypatch, tmp_path, lowpass_wav):
    monkeypatch.setenv("MOODIFY_AUTH_MODE", "single_user")
    monkeypatch.setenv("MOODIFY_RECON_WORKSPACE_ROOT", str(tmp_path / "ws2"))
    monkeypatch.setenv("MOODIFY_RECON_DB", str(tmp_path / "jobs2.db"))
    from tests.reconstruction_job.test_api import _upload  # reuse helper
    # single_user accepts requests without the actor header
    resp = _upload(lowpass_wav)
    assert resp.status_code == 202
