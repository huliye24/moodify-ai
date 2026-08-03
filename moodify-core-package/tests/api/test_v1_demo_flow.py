"""End-to-end demo flow tests (DSK-MFY-DEMO-001).

Real upload -> real project -> real v01 pipeline job -> real artifacts.
"""

from __future__ import annotations

import hashlib
import math
import shutil
import struct
import time
import wave
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from moodify.api.main import app

_SAMPLE_DIR = Path("data/demo")
_TIMEOUT_S = 180


def _make_wav(path: Path, seconds: float = 2.0, sr: int = 22050) -> None:
    frames = int(seconds * sr)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        for i in range(frames):
            # 220 Hz sine, quiet-ish, int16 mono
            sample = int(12000 * math.sin(2 * math.pi * 220 * i / sr))
            w.writeframes(struct.pack("<h", sample))


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="module")
def sample_audio() -> Path:
    path = _SAMPLE_DIR / "demo_flow_input.wav"
    path.parent.mkdir(parents=True, exist_ok=True)
    _make_wav(path)
    yield path
    shutil.rmtree(_SAMPLE_DIR, ignore_errors=True)


@pytest.fixture(scope="module")
def paired(client: TestClient) -> str:
    resp = client.post("/api/v1/pair", json={"device_id": "android-demo-flow"})
    assert resp.status_code == 200
    return resp.json()["token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _upload(client: TestClient, token: str, sample_audio: Path,
            sha256: str | None = None, size_bytes: int | None = None):
    sha = sha256 if sha256 is not None else hashlib.sha256(
        sample_audio.read_bytes()).hexdigest()
    size = size_bytes if size_bytes is not None else sample_audio.stat().st_size
    with sample_audio.open("rb") as fh:
        return client.post(
            "/api/v1/uploads",
            headers=_auth(token),
            data={
                "project_id": "prj-demo-target",
                "filename": sample_audio.name,
                "size_bytes": str(size),
                "sha256": sha,
            },
            files={"file": (sample_audio.name, fh, "audio/wav")},
        )


def test_full_flow_end_to_end(client: TestClient, sample_audio: Path,
                              paired: str) -> None:
    token = paired

    # 1. upload a real file
    up = _upload(client, token, sample_audio)
    assert up.status_code == 200, up.text
    upload = up.json()
    assert upload["upload_id"].startswith("up-")
    assert upload["received_bytes"] == upload["total_bytes"]
    assert upload["status"] == "received"

    # 2. create a project -> auto-starts the real pipeline job
    prj = client.post(
        "/api/v1/projects",
        headers=_auth(token),
        json={"title": "Demo Flow 演示", "source_audio_ids": [upload["upload_id"]]},
    )
    assert prj.status_code == 200, prj.text
    project = prj.json()
    assert project["project_id"].startswith("prj-")
    assert project["status"] == "active"
    job_id = project["job_id"]
    assert job_id.startswith("job-")

    # 3. poll the job to completion; progress must move monotonically
    seen_stages: list[str] = []
    last_progress = -1.0
    deadline = time.monotonic() + _TIMEOUT_S
    while time.monotonic() < deadline:
        job = client.get(f"/api/v1/jobs/{job_id}", headers=_auth(token))
        assert job.status_code == 200
        body = job.json()
        if body["stage"] not in seen_stages:
            seen_stages.append(body["stage"])
        assert body["progress"] >= last_progress - 1e-6, (
            f"progress regressed: {last_progress} -> {body['progress']}"
        )
        last_progress = body["progress"]
        if body["status"] in ("done", "failed", "cancelled"):
            break
        time.sleep(1.0)
    else:
        pytest.fail("job did not finish within timeout")

    assert body["status"] == "done", f"job failed: {body}"
    assert body["progress"] == 1.0
    assert seen_stages, "no stage snapshots observed"
    assert body["stage"] == "done"

    # 4. real result summary with real metrics
    res = client.get(f"/api/v1/jobs/{job_id}/result", headers=_auth(token))
    assert res.status_code == 200, res.text
    summary = res.json()
    assert summary["filename"] == sample_audio.name
    assert summary["preset"] == "clean_master"
    assert summary["mrs_before"] is not None
    assert summary["mrs_delta"] is not None
    assert summary["quality_gate"] is not None
    assert summary["output_filename"].endswith(".wav")
    assert summary["artifact_id"].startswith("art-")
    assert summary["upload_id"].startswith("up-")

    # 4b. original audio download endpoint (A/B comparison)
    orig = client.get(
        f"/api/v1/uploads/{summary['upload_id']}/download", headers=_auth(token)
    )
    assert orig.status_code == 200, orig.text
    assert orig.headers["content-type"].startswith("audio/")
    assert len(orig.content) > 1000

    # 5. artifact metadata matches the real output file
    art = client.get(f"/api/v1/artifacts/{summary['artifact_id']}", headers=_auth(token))
    assert art.status_code == 200
    artifact = art.json()
    assert artifact["kind"] == "processed_audio"
    assert artifact["filename"] == summary["output_filename"]
    assert artifact["sha256"]

    # 6. download endpoint serves real bytes
    dl = client.get(
        f"/api/v1/artifacts/{summary['artifact_id']}/download", headers=_auth(token)
    )
    assert dl.status_code == 200
    assert dl.headers["content-type"].startswith("audio/")
    assert len(dl.content) > 1000

    # 7. project detail resolves
    detail = client.get(f"/api/v1/projects/{project['project_id']}", headers=_auth(token))
    assert detail.status_code == 200
    assert detail.json()["title"] == "Demo Flow 演示"


def test_catalog_lists_and_downloads(client: TestClient, paired: str) -> None:
    # seed one catalog song
    cat = Path("data/demo/catalog")
    cat.mkdir(parents=True, exist_ok=True)
    seed = cat / "catalog_seed.wav"
    seed.write_bytes(_SAMPLE_SEED)
    try:
        resp = client.get("/api/v1/catalog", headers=_auth(paired))
        assert resp.status_code == 200
        songs = resp.json()["songs"]
        seed_song = next((s for s in songs if s["song_id"] == "song-catalog_seed"), None)
        assert seed_song is not None, songs
        assert seed_song["artist"] == "泫榛"
        assert seed_song["duration_s"] is not None

        dl = client.get(f"/api/v1/catalog/{seed_song['song_id']}/download", headers=_auth(paired))
        assert dl.status_code == 200
        assert len(dl.content) > 0

        missing = client.get("/api/v1/catalog/song-nope/download", headers=_auth(paired))
        assert missing.status_code == 404
        assert missing.json()["error"]["code"] == "NOT_FOUND"

        noauth = client.get("/api/v1/catalog")
        assert noauth.status_code == 401
    finally:
        seed.unlink(missing_ok=True)


_SAMPLE_SEED = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80\x3e\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"


def test_upload_requires_token(client: TestClient, sample_audio: Path) -> None:
    resp = _upload(client, "", sample_audio)
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


def test_upload_rejects_bad_sha256(client: TestClient, sample_audio: Path,
                                   paired: str) -> None:
    resp = _upload(client, paired, sample_audio, sha256="0" * 64)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION"


def test_upload_rejects_bad_size(client: TestClient, sample_audio: Path,
                                 paired: str) -> None:
    resp = _upload(client, paired, sample_audio, size_bytes=12345)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION"


def test_project_requires_known_upload(client: TestClient, paired: str) -> None:
    resp = client.post(
        "/api/v1/projects",
        headers=_auth(paired),
        json={"title": "Ghost", "source_audio_ids": ["up-does-not-exist"]},
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


def test_unauthorized_token_rejected(client: TestClient, paired: str) -> None:
    resp = client.get("/api/v1/jobs/job-none", headers=_auth("bogus-token"))
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"
