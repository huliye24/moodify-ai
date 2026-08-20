"""Worker tests (MFY-CR-P08): serial processing, restart recovery, precheck."""

from __future__ import annotations

import shutil
from uuid import uuid4

import pytest

from moodify.reconstruction_job.contract import JobStatus, ReconstructionJob
from moodify.reconstruction_job.store import JobStore
from moodify.reconstruction_job.worker import WorkerConfig, _process_one

pytestmark = pytest.mark.v01


def _job(key: str) -> ReconstructionJob:
    return ReconstructionJob(
        job_id=f"job_{uuid4().hex}",
        owner_id="user-alice",
        source_asset_id="asset-1",
        source_sha256="pending",
        status=JobStatus.QUEUED.value,
        progress_stage=None,
        requested_at="2026-08-17T00:00:00+00:00",
        idempotency_key=key,
    )


def _config(tmp_path) -> WorkerConfig:
    return WorkerConfig(
        db_path=tmp_path / "jobs.db",
        workspace_root=tmp_path / "workspace",
        poll_seconds=0.0,
    )


def test_worker_processes_jobs_serially(lowpass_wav, tmp_path):
    config = _config(tmp_path)
    store = JobStore(config.db_path, lease_seconds=3600)
    jobs = [_job("a"), _job("b")]
    for j in jobs:
        ws = config.workspace_root / j.job_id
        (ws / "input").mkdir(parents=True, exist_ok=True)
        (ws / "tmp").mkdir(parents=True, exist_ok=True)
        shutil.copy2(lowpass_wav, ws / "input" / lowpass_wav.name)
        store.insert_job(j)
    assert _process_one(store, config) is True
    first = store.get_job("user-alice", jobs[0].job_id)
    second = store.get_job("user-alice", jobs[1].job_id)
    assert first.status in (JobStatus.SUCCEEDED.value, JobStatus.SOURCE_WINS.value,
                            JobStatus.HUMAN_REQUIRED.value)
    assert second.status == JobStatus.QUEUED.value  # serial: only first processed
    assert _process_one(store, config) is True
    assert store.get_job("user-alice", jobs[1].job_id).status != JobStatus.QUEUED.value


def test_worker_recovers_interrupted_running_job(tmp_path, monkeypatch):
    config = _config(tmp_path)
    store = JobStore(config.db_path, lease_seconds=3600)
    job = _job("r")
    store.insert_job(job)
    ws = config.workspace_root / job.job_id
    (ws / "input").mkdir(parents=True, exist_ok=True)
    (ws / "tmp").mkdir(parents=True, exist_ok=True)
    # simulate a previous worker that crashed mid-job: leased but not finished
    leased = store.lease_next()
    assert leased is not None
    store.update_progress(leased.job_id, JobStatus.ANALYZING.value)
    # new worker starts: recovery requeues it
    store2 = JobStore(config.db_path, lease_seconds=3600)
    assert store2.recover_interrupted() == 1
    assert store2.get_job("user-alice", job.job_id).status == JobStatus.QUEUED.value


def test_worker_defers_when_resources_low(tmp_path, monkeypatch):
    config = _config(tmp_path)
    store = JobStore(config.db_path, lease_seconds=3600)
    job = _job("d")
    store.insert_job(job)
    monkeypatch.setattr(
        "moodify.reconstruction_job.worker.safe_to_start",
        lambda *a, **k: (False, type("S", (), {"available_memory_mb": 1, "available_disk_gb": 0.1})(), "low mem"),
    )
    assert _process_one(store, config) is False
    assert store.get_job("user-alice", job.job_id).status == JobStatus.QUEUED.value
