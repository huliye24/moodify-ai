"""Stem separation API tests — LALAL-STEMS-001.

Uses a fake LalalClient injected via monkeypatch (no network, no billing).
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from moodify.stems import service
from moodify.stems.errors import StemLicenseInvalid, StemUpstreamRejected


class FakeLalal:
    def __init__(self, *, check_status="progress", check_progress=50, result_urls=None,
                 upload_error=None, split_error=None):
        self.check_status = check_status
        self.check_progress = check_progress
        self.result_urls = result_urls or {}
        self.upload_error = upload_error
        self.split_error = split_error
        self.upload_calls = 0
        self.upload_paths: list[Path] = []
        self.split_calls: list[dict] = []
        self.check_calls: list[list[str]] = []

    def upload(self, path, filename):
        self.upload_calls += 1
        self.upload_paths.append(Path(path))
        if self.upload_error:
            raise self.upload_error
        return "src_1"

    def split(self, source_id, presets):
        self.split_calls.append(presets)
        if self.split_error:
            raise self.split_error
        return f"task_{len(self.split_calls)}"

    def check(self, task_ids):
        self.check_calls.append(list(task_ids))
        result = {}
        for task_id in task_ids:
            if self.check_status == "success":
                url = self.result_urls.get(task_id, f"https://cdn/{task_id}.wav")
                result[task_id] = {
                    "status": "success", "progress": 100,
                    "result": {
                        "tracks": [
                            {"type": "stem", "label": "vocals", "url": url},
                            {"type": "back", "label": "no_vocals", "url": f"{url}?part=back"},
                        ],
                        "duration": 25,
                    },
                }
            elif self.check_status == "cancelled":
                result[task_id] = {"status": "cancelled"}
            elif self.check_status == "error":
                result[task_id] = {"status": "error", "message": "upstream boom"}
            else:
                result[task_id] = {
                    "status": "progress", "progress": self.check_progress,
                    "presets": {"stem": "vocals", "extraction_level": "deep_extraction", "splitter": "auto"},
                }
        return result


@pytest.fixture(autouse=True)
def api_env(tmp_path, monkeypatch):
    fake = FakeLalal()
    monkeypatch.setenv("MOODIFY_STEMS_DB", str(tmp_path / "stems.sqlite3"))
    monkeypatch.setenv("LALAL_LICENSE_KEY", "test-key")
    monkeypatch.setenv("MOODIFY_STEMS_POLL_MIN_SECONDS", "0")
    monkeypatch.setattr(service, "_client", lambda: fake)
    from fastapi.testclient import TestClient

    from moodify.api.main import app

    client = TestClient(app)
    yield client, fake, tmp_path


def _post(client, *, stems="vocals", filename="song.wav", content=b"RIFF-wav-data", **extra):
    return client.post(
        "/api/v1/stems/jobs",
        files={"audio": (filename, content, "audio/wav")},
        data={"stems": stems, **extra},
    )


def test_submit_happy_path(api_env):
    client, fake, tmp_path = api_env
    resp = _post(client)
    assert resp.status_code == 202
    body = resp.json()
    job = body["job"]
    assert job["status"] == "PROCESSING"
    assert job["stems"] == ["vocals"]
    assert job["extraction_level"] == "deep_extraction"
    assert job["splitter"] == "auto"
    assert job["source_name"] == "song.wav"
    assert job["progress"] == 0
    # internal fields must never leak
    assert "source_path" not in job
    assert "source_id" not in job
    assert "task_ids" not in job
    assert "presets" not in job
    assert fake.upload_calls == 1
    assert len(fake.split_calls) == 1
    assert fake.split_calls[0]["stem"] == "vocals"
    # source copy is removed after submission
    assert not fake.upload_paths[0].exists()
    assert job["estimated_pro_minutes"] is None  # undecodable fake bytes


def test_submit_with_real_wav_estimates_billing(api_env, mock_wav):
    client, fake, _ = api_env
    with open(mock_wav, "rb") as handle:
        content = handle.read()
    resp = _post(client, filename="test.wav", content=content)
    assert resp.status_code == 202
    job = resp.json()["job"]
    assert job["estimated_pro_minutes"] == 1  # ceil(10s/60) * 1 stem


def test_submit_multiple_stems_creates_one_task_each(api_env):
    client, fake, _ = api_env
    resp = _post(client, stems="vocals,drum,bass")
    assert resp.status_code == 202
    job = resp.json()["job"]
    assert job["stems"] == ["vocals", "drum", "bass"]
    assert [call["stem"] for call in fake.split_calls] == ["vocals", "drum", "bass"]
    assert job["estimated_pro_minutes"] is None  # undecodable fake bytes


def test_submit_unknown_stem_422(api_env):
    client, fake, _ = api_env
    resp = _post(client, stems="banjo")
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "STEM_TYPE_INVALID"
    assert fake.upload_calls == 0
    assert fake.split_calls == []


def test_submit_empty_stems_422(api_env):
    client, _, _ = api_env
    resp = _post(client, stems=",")
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "STEM_TYPE_INVALID"


def test_submit_bad_extraction_level_422(api_env):
    client, _, _ = api_env
    resp = _post(client, extraction_level="turbo")
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "STEM_PARAM_INVALID"


def test_submit_bad_splitter_422(api_env):
    client, _, _ = api_env
    resp = _post(client, splitter="deepseek")
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "STEM_PARAM_INVALID"


def test_submit_bad_suffix_415(api_env):
    client, _, _ = api_env
    resp = _post(client, filename="song.mp4", content=b"x")
    assert resp.status_code == 415
    assert resp.json()["detail"]["code"] == "AUDIO_TYPE_UNSUPPORTED"


def test_submit_empty_file_422(api_env):
    client, _, _ = api_env
    resp = _post(client, content=b"")
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "AUDIO_EMPTY"


def test_submit_too_large_413(api_env, monkeypatch):
    from moodify.api.routes import stems as routes

    monkeypatch.setattr(routes, "MAX_SIZE", 16)
    client, _, _ = api_env
    resp = _post(client, content=b"x" * 1024)
    assert resp.status_code == 413
    assert resp.json()["detail"]["code"] == "AUDIO_TOO_LARGE"


def test_submit_without_license_503(monkeypatch, tmp_path):
    monkeypatch.setenv("LALAL_LICENSE_KEY", "")
    from fastapi.testclient import TestClient

    from moodify.api.main import app

    client = TestClient(app)
    resp = _post(client)
    assert resp.status_code == 503
    assert resp.json()["detail"]["code"] == "STEM_LICENSE_MISSING"


def test_submit_license_invalid_502(api_env):
    client, fake, _ = api_env
    fake.upload_error = StemLicenseInvalid("lalal.ai rejected license key")
    resp = _post(client)
    assert resp.status_code == 502
    assert resp.json()["detail"]["code"] == "STEM_LICENSE_INVALID"


def test_submit_split_rejected_marks_failed_and_502(api_env):
    client, fake, _ = api_env
    fake.split_error = StemUpstreamRejected("lalal.ai rejected split: 422 bad stem")
    resp = _post(client)
    assert resp.status_code == 502
    assert resp.json()["detail"]["code"] == "STEM_UPSTREAM_REJECTED"

    job_id = client.get("/api/v1/stems/jobs").json()["jobs"][0]["job_id"]
    job = client.get(f"/api/v1/stems/jobs/{job_id}").json()["job"]
    assert job["status"] == "FAILED"
    assert "StemUpstreamRejected" in job["last_error"]


def test_capacity_limit_503(api_env, monkeypatch):
    from moodify.api.routes import stems as routes

    monkeypatch.setattr(routes, "MAX_RETAINED", 1)
    client, _, _ = api_env
    assert _post(client).status_code == 202
    resp = _post(client)
    assert resp.status_code == 503
    assert resp.json()["detail"]["code"] == "STEM_CAPACITY_REACHED"


def test_get_job_live_refreshes_progress(api_env):
    client, fake, _ = api_env
    job_id = _post(client).json()["job"]["job_id"]

    resp = client.get(f"/api/v1/stems/jobs/{job_id}")
    assert resp.status_code == 200
    job = resp.json()["job"]
    assert job["status"] == "PROCESSING"
    assert job["progress"] == 50
    assert fake.check_calls == [["task_1"]]


def test_get_job_success_returns_results(api_env):
    client, fake, _ = api_env
    job_id = _post(client).json()["job"]["job_id"]
    fake.check_status = "success"
    fake.result_urls = {"task_1": "https://cdn/vocals.wav"}

    resp = client.get(f"/api/v1/stems/jobs/{job_id}")
    job = resp.json()["job"]
    assert job["status"] == "SUCCEEDED"
    assert job["progress"] == 100
    assert job["results"]["vocals"] == "https://cdn/vocals.wav"
    assert job["results"]["vocals_back"] == "https://cdn/vocals.wav?part=back"
    assert job["finished_at"] is not None


def test_get_job_terminal_does_not_call_upstream(api_env):
    client, fake, _ = api_env
    job_id = _post(client).json()["job"]["job_id"]
    fake.check_status = "success"
    client.get(f"/api/v1/stems/jobs/{job_id}")  # transitions to SUCCEEDED
    calls_after_transition = len(fake.check_calls)

    client.get(f"/api/v1/stems/jobs/{job_id}")
    assert len(fake.check_calls) == calls_after_transition


def test_get_job_throttled(api_env, monkeypatch):
    monkeypatch.setenv("MOODIFY_STEMS_POLL_MIN_SECONDS", "600")
    client, fake, _ = api_env
    job_id = _post(client).json()["job"]["job_id"]

    client.get(f"/api/v1/stems/jobs/{job_id}")
    assert len(fake.check_calls) == 0  # throttled: just submitted


def test_get_job_lalal_error_marks_failed(api_env):
    client, fake, _ = api_env
    job_id = _post(client).json()["job"]["job_id"]
    fake.check_status = "error"

    resp = client.get(f"/api/v1/stems/jobs/{job_id}")
    job = resp.json()["job"]
    assert job["status"] == "FAILED"
    assert "upstream boom" in job["last_error"]


def test_get_job_cancelled(api_env):
    client, fake, _ = api_env
    job_id = _post(client).json()["job"]["job_id"]
    fake.check_status = "cancelled"

    resp = client.get(f"/api/v1/stems/jobs/{job_id}")
    assert resp.json()["job"]["status"] == "CANCELLED"


def test_get_job_not_found_404(api_env):
    client, _, _ = api_env
    resp = client.get("/api/v1/stems/jobs/stem_doesnotexist")
    assert resp.status_code == 404
    assert resp.json()["detail"]["code"] == "STEM_JOB_NOT_FOUND"


def test_download_redirect_307(api_env):
    client, fake, _ = api_env
    job_id = _post(client).json()["job"]["job_id"]
    fake.check_status = "success"
    client.get(f"/api/v1/stems/jobs/{job_id}")

    resp = client.get(f"/api/v1/stems/jobs/{job_id}/download/vocals", follow_redirects=False)
    assert resp.status_code == 307
    assert resp.headers["location"] == "https://cdn/task_1.wav"


def test_download_backing_track_307(api_env):
    client, fake, _ = api_env
    job_id = _post(client).json()["job"]["job_id"]
    fake.check_status = "success"
    client.get(f"/api/v1/stems/jobs/{job_id}")

    resp = client.get(f"/api/v1/stems/jobs/{job_id}/download/vocals_back", follow_redirects=False)
    assert resp.status_code == 307
    assert resp.headers["location"] == "https://cdn/task_1.wav?part=back"


def test_download_not_ready_409(api_env):
    client, _, _ = api_env
    job_id = _post(client).json()["job"]["job_id"]
    resp = client.get(f"/api/v1/stems/jobs/{job_id}/download/vocals")
    assert resp.status_code == 409
    assert resp.json()["detail"]["code"] == "STEM_RESULT_NOT_READY"


def test_download_stem_not_in_job_409(api_env):
    client, fake, _ = api_env
    job_id = _post(client, stems="vocals").json()["job"]["job_id"]
    fake.check_status = "success"
    client.get(f"/api/v1/stems/jobs/{job_id}")

    resp = client.get(f"/api/v1/stems/jobs/{job_id}/download/drum")
    assert resp.status_code == 409
    assert resp.json()["detail"]["code"] == "STEM_RESULT_NOT_READY"


def test_download_unknown_stem_422(api_env):
    client, fake, _ = api_env
    job_id = _post(client).json()["job"]["job_id"]
    fake.check_status = "success"
    client.get(f"/api/v1/stems/jobs/{job_id}")

    resp = client.get(f"/api/v1/stems/jobs/{job_id}/download/banjo")
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "STEM_TYPE_INVALID"


def test_download_expired_410(api_env):
    client, fake, _ = api_env
    job_id = _post(client).json()["job"]["job_id"]
    fake.check_status = "success"
    client.get(f"/api/v1/stems/jobs/{job_id}")

    import sqlite3
    from datetime import datetime, timedelta, timezone

    old = (datetime.now(timezone.utc) - timedelta(hours=30)).isoformat()
    with sqlite3.connect(os.environ["MOODIFY_STEMS_DB"]) as con:
        con.execute("UPDATE stem_jobs SET finished_at=? WHERE job_id=?", (old, job_id))

    resp = client.get(f"/api/v1/stems/jobs/{job_id}/download/vocals")
    assert resp.status_code == 410
    assert resp.json()["detail"]["code"] == "STEM_DOWNLOAD_EXPIRED"


def test_download_job_not_found_404(api_env):
    client, _, _ = api_env
    resp = client.get("/api/v1/stems/jobs/nope/download/vocals")
    assert resp.status_code == 404


def test_list_and_usage(api_env):
    client, fake, _ = api_env
    j1 = _post(client).json()["job"]["job_id"]
    _post(client, stems="vocals,drum")
    fake.check_status = "success"
    client.get(f"/api/v1/stems/jobs/{j1}")

    listing = client.get("/api/v1/stems/jobs").json()
    assert listing["count"] == 2
    assert listing["jobs"][0]["stems"] in (["vocals", "drum"], ["vocals"])

    filtered = client.get("/api/v1/stems/jobs?status=SUCCEEDED").json()
    assert filtered["count"] == 1
    assert client.get("/api/v1/stems/jobs?status=BOGUS").status_code == 422

    usage = client.get("/api/v1/stems/usage").json()
    assert usage["total_tasks"] == 2
    assert usage["succeeded"] == 1
    assert len(usage["recent"]) == 2
