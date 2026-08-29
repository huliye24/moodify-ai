"""Engine end-to-end tests (MFY-CR-P08)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from uuid import uuid4

import pytest

from moodify.reconstruction_job.contract import (
    JobStatus,
    ReconstructionJob,
)
from moodify.reconstruction_job.engine import run_reconstruction_job
from moodify.reconstruction_job.selection import SelectDecision

pytestmark = pytest.mark.v01


def _job(owner: str = "user-alice", key: str | None = "k", cancel: bool = False) -> ReconstructionJob:
    return ReconstructionJob(
        job_id=f"job_{uuid4().hex}",
        owner_id=owner,
        source_asset_id="asset-1",
        source_sha256="pending",
        status=JobStatus.QUEUED.value,
        progress_stage=None,
        requested_at="2026-08-17T00:00:00+00:00",
        idempotency_key=key,
        cancel_requested=cancel,
    )


def _stage(workspace_root: Path, job: ReconstructionJob, src: Path) -> None:
    ws = workspace_root / job.job_id
    (ws / "input").mkdir(parents=True, exist_ok=True)
    (ws / "tmp").mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, ws / "input" / src.name)
    (ws / "tmp" / "scratch.bin").write_bytes(b"x" * 1024)


def test_source_wins_path(clean_fullband_wav, empty_store, engine_config):
    job = _job()
    _stage(engine_config.workspace_root, job, clean_fullband_wav)
    empty_store.insert_job(job)
    status = run_reconstruction_job(job, empty_store, engine_config)
    assert status == JobStatus.SOURCE_WINS.value
    stored = empty_store.get_job(job.owner_id, job.job_id)
    assert stored.status == JobStatus.SOURCE_WINS.value
    assert stored.result_object_id is not None
    result = empty_store.get_result(job.owner_id, job.job_id)
    assert result.selected_candidate == "SOURCE"
    assert result.audio_object_ref.endswith("input/source.wav")


def test_succeeded_path(lowpass_wav, empty_store, engine_config):
    job = _job(key="s")
    _stage(engine_config.workspace_root, job, lowpass_wav)
    empty_store.insert_job(job)
    run_reconstruction_job(job, empty_store, engine_config)
    stored = empty_store.get_job(job.owner_id, job.job_id)
    assert stored.status in (JobStatus.SUCCEEDED.value, JobStatus.SOURCE_WINS.value), stored.status
    assert stored.result_object_id is not None
    result = empty_store.get_result(job.owner_id, job.job_id)
    assert result.production_case_id.startswith("case_")
    assert result.source_sha256 == stored.source_sha256


def test_unsupported_format_fails(tmp_path, empty_store, engine_config):
    bogus = tmp_path / "song.txt"
    bogus.write_text("not audio", encoding="utf-8")
    job = _job(key="u")
    _stage(engine_config.workspace_root, job, bogus)
    empty_store.insert_job(job)
    status = run_reconstruction_job(job, empty_store, engine_config)
    assert status == JobStatus.FAILED.value
    stored = empty_store.get_job(job.owner_id, job.job_id)
    assert stored.failure_code == "UNSUPPORTED_FORMAT"
    assert stored.retry_policy == "PERMANENT"


def test_engine_invokes_pipeline_once(lowpass_wav, empty_store, engine_config, monkeypatch):
    calls = []
    import moodify.reconstruction_job.engine as engine_mod
    from moodify.reconstruction.pipeline import run_golden_pipeline

    def fake(source_wav, out_dir, **kwargs):
        calls.append(str(source_wav))
        return run_golden_pipeline(source_wav, out_dir, **kwargs)

    monkeypatch.setattr(engine_mod, "run_golden_pipeline", fake)
    job = _job(key="p")
    _stage(engine_config.workspace_root, job, lowpass_wav)
    empty_store.insert_job(job)
    run_reconstruction_job(job, empty_store, engine_config)
    assert len(calls) == 1


def test_tmp_cleaned_and_case_not_duplicated(lowpass_wav, empty_store, engine_config):
    job = _job(key="t")
    _stage(engine_config.workspace_root, job, lowpass_wav)
    empty_store.insert_job(job)
    run_reconstruction_job(job, empty_store, engine_config)
    ws = engine_config.workspace_root / job.job_id
    assert not (ws / "tmp").exists()
    case_dir = ws / "case"
    case_file = case_dir / "production_case.json"
    assert case_file.is_file()
    case = json.loads(case_file.read_text(encoding="utf-8"))
    assert case["case_id"].startswith("case_")
    # exactly one production case, one evidence registry
    assert len(list(case_dir.glob("production_case.json"))) == 1
    assert (case_dir / "evidence.json").is_file()
    # result references canonical evidence
    assert (ws / "result" / "result.json").is_file()


def test_human_required_stops_without_result(lowpass_wav, empty_store, engine_config, monkeypatch):
    import moodify.reconstruction_job.engine as engine_mod
    monkeypatch.setattr(
        engine_mod, "select_result",
        lambda pipeline: SelectDecision(
            status=JobStatus.HUMAN_REQUIRED.value, selected_candidate="HUMAN_REQUIRED",
            plan_hash=None, identity_status="HUMAN_REQUIRED", technical_status="deferred",
            human_reasons=("test",),
        ),
    )
    job = _job(key="h")
    _stage(engine_config.workspace_root, job, lowpass_wav)
    empty_store.insert_job(job)
    status = run_reconstruction_job(job, empty_store, engine_config)
    assert status == JobStatus.HUMAN_REQUIRED.value
    stored = empty_store.get_job(job.owner_id, job.job_id)
    assert stored.status == JobStatus.HUMAN_REQUIRED.value
    assert stored.result_object_id is None  # never auto-approves


def test_cancel_requested_stops_at_stage_boundary(clean_fullband_wav, empty_store, engine_config):
    job = _job(key="c", cancel=True)
    _stage(engine_config.workspace_root, job, clean_fullband_wav)
    empty_store.insert_job(job)
    status = run_reconstruction_job(job, empty_store, engine_config)
    assert status == JobStatus.CANCELLED.value
    stored = empty_store.get_job(job.owner_id, job.job_id)
    assert stored.status == JobStatus.CANCELLED.value


def test_retryable_failure_requeues(lowpass_wav, empty_store, engine_config, monkeypatch):
    import moodify.reconstruction_job.engine as engine_mod

    def boom(*args, **kwargs):
        raise RuntimeError("transient network")

    monkeypatch.setattr(engine_mod, "run_golden_pipeline", boom)
    job = _job(key="r")
    _stage(engine_config.workspace_root, job, lowpass_wav)
    empty_store.insert_job(job)
    status = run_reconstruction_job(job, empty_store, engine_config)
    assert status == JobStatus.FAILED.value
    stored = empty_store.get_job(job.owner_id, job.job_id)
    assert stored.status == JobStatus.QUEUED.value  # requeued for bounded retry
    assert stored.failure_code == "PIPELINE_FAILED"
    assert stored.retry_policy == "TRANSIENT"
