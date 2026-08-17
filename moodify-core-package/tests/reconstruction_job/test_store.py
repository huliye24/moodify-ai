"""JobStore tests (MFY-CR-P08)."""

from __future__ import annotations

from uuid import uuid4

from moodify.reconstruction_job.contract import (
    FailureInfo,
    JobStatus,
    ReconstructionJob,
    ReconstructionResult,
    progress_label,
)
from moodify.reconstruction_job.store import JobStore, connect

SRC = "sha256:" + "a" * 64
OWNER = "user-alice"
VERSION = "reconstruction-job-v0.1"


def _job(owner: str = OWNER, key: str | None = None, status: str = "QUEUED") -> ReconstructionJob:
    suffix = key if key is not None else uuid4().hex[:8]
    return ReconstructionJob(
        job_id=f"job_{owner}_{suffix}",
        owner_id=owner,
        source_asset_id="asset-1",
        source_sha256=SRC,
        status=status,
        progress_stage=None,
        requested_at="2026-08-17T00:00:00+00:00",
        idempotency_key=key,
    )

def _result(job_id: str) -> ReconstructionResult:
    return ReconstructionResult(
        result_id="res_1", job_id=job_id, production_case_id="case_1",
        source_sha256=SRC, selected_candidate="SOURCE", audio_object_ref="case/result/source.wav",
        reconstruction_version=VERSION, plan_hash=None, engine_version="golden-pipeline-v0.1",
        identity_status="N/A", technical_status="source_wins", created_at="2026-08-17T00:01:00+00:00",
    )


def test_schema_creates_tables(tmp_path):
    db = tmp_path / "jobs.db"
    with connect(db) as con:
        tables = {r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"reconstruction_jobs", "reconstruction_results"} <= tables


def test_insert_and_get(tmp_path):
    store = JobStore(tmp_path / "jobs.db")
    inserted = store.insert_job(_job())
    job = store.get_job(OWNER, inserted.job_id)
    assert job is not None
    assert job.status == "QUEUED"
    assert job.billing_state_placeholder == "NOT_IMPLEMENTED"
    assert job.training_permission is False


def test_cross_owner_read_returns_none(tmp_path):
    store = JobStore(tmp_path / "jobs.db")
    store.insert_job(_job(owner="user-alice", key="k1"))
    assert store.get_job("user-bob", "job_user-alice_k1") is None


def test_unique_idempotency_constraint(tmp_path):
    store = JobStore(tmp_path / "jobs.db")
    store.insert_job(_job(key="key-1"))
    import sqlite3
    try:
        store.insert_job(_job(key="key-1"))
        assert False, "expected IntegrityError"
    except sqlite3.IntegrityError:
        pass


def test_null_idempotency_keys_do_not_conflict(tmp_path):
    store = JobStore(tmp_path / "jobs.db")
    store.insert_job(_job(key=None))
    store.insert_job(_job(key=None))
    assert len(store.list_jobs(OWNER)) == 2


def test_find_existing(tmp_path):
    store = JobStore(tmp_path / "jobs.db")
    store.insert_job(_job(key="key-2"))
    hit = store.find_existing(OWNER, SRC, VERSION, "key-2")
    assert hit is not None
    assert store.find_existing(OWNER, SRC, VERSION, "other") is None


def test_lease_next_and_lease_exclusion(tmp_path):
    store = JobStore(tmp_path / "jobs.db", lease_seconds=3600)
    store.insert_job(_job(key="a"))
    leased = store.lease_next()
    assert leased is not None
    assert leased.lease_until is not None
    assert store.lease_next() is None  # already leased


def test_recover_interrupted_requeues_expired_lease(tmp_path):
    store = JobStore(tmp_path / "jobs.db", lease_seconds=-10)
    store.insert_job(_job(key="a"))
    store.lease_next()
    assert store.recover_interrupted() == 1
    job = store.get_job(OWNER, "job_user-alice_a")
    assert job.status == "QUEUED"
    assert job.lease_until is None


def test_succeed_writes_result(tmp_path):
    store = JobStore(tmp_path / "jobs.db")
    store.insert_job(_job(key="a"))
    store.succeed("job_user-alice_a", JobStatus.SOURCE_WINS.value, _result("job_user-alice_a"))
    job = store.get_job(OWNER, "job_user-alice_a")
    assert job.status == "SOURCE_WINS"
    assert job.result_object_id == "res_1"
    result = store.get_result(OWNER, "job_user-alice_a")
    assert result is not None and result.selected_candidate == "SOURCE"


def test_fail_records_failure(tmp_path):
    store = JobStore(tmp_path / "jobs.db")
    store.insert_job(_job(key="a"))
    failure = FailureInfo(
        failure_code="DECODE_FAILED", stage="ingest", retry_policy="PERMANENT",
        user_action="provide a supported audio file",
        internal_detail="ffmpeg decode failed", public_message_key="reconstruction_source_invalid",
    )
    store.fail("job_user-alice_a", failure)
    job = store.get_job(OWNER, "job_user-alice_a")
    assert job.status == "FAILED"
    assert job.failure_code == "DECODE_FAILED"
    assert job.retry_policy == "PERMANENT"


def test_retry_or_fail_transient_requeues_then_fails(tmp_path):
    store = JobStore(tmp_path / "jobs.db")
    store.insert_job(_job(key="a"))
    failure = FailureInfo(
        failure_code="PIPELINE_FAILED", stage="pipeline", retry_policy="TRANSIENT",
        user_action="retry later", internal_detail="transient", public_message_key="reconstruction_retry",
    )
    # attempts increments on lease; bounded retry stops after max_attempts tries
    assert store.retry_or_fail("job_user-alice_a", failure, max_attempts=3) == "QUEUED"
    store.lease_next()  # attempt 1
    assert store.retry_or_fail("job_user-alice_a", failure, max_attempts=3) == "QUEUED"
    store.lease_next()  # attempt 2
    assert store.retry_or_fail("job_user-alice_a", failure, max_attempts=3) == "QUEUED"
    store.lease_next()  # attempt 3
    assert store.retry_or_fail("job_user-alice_a", failure, max_attempts=3) == "FAILED"


def test_cancel_queued_is_terminal(tmp_path):
    store = JobStore(tmp_path / "jobs.db")
    store.insert_job(_job(key="a"))
    job = store.request_cancel(OWNER, "job_user-alice_a")
    assert job.status == "CANCELLED"


def test_cancel_inflight_flags_without_stopping(tmp_path):
    store = JobStore(tmp_path / "jobs.db")
    store.insert_job(_job(key="a", status="ANALYZING"))
    job = store.request_cancel(OWNER, "job_user-alice_a")
    assert job.status == "ANALYZING"
    assert job.cancel_requested is True


def test_cancel_terminal_refused(tmp_path):
    store = JobStore(tmp_path / "jobs.db")
    store.insert_job(_job(key="a", status="SUCCEEDED"))
    job = store.request_cancel(OWNER, "job_user-alice_a")
    assert job.status == "SUCCEEDED"


def test_cross_owner_cancel_returns_none(tmp_path):
    store = JobStore(tmp_path / "jobs.db")
    store.insert_job(_job(owner="user-alice", key="k1"))
    assert store.request_cancel("user-bob", "job_user-alice_k1") is None


def test_list_and_counts(tmp_path):
    store = JobStore(tmp_path / "jobs.db")
    store.insert_job(_job(key="a"))
    store.insert_job(_job(key="b", status="FAILED"))
    assert len(store.list_jobs(OWNER)) == 2
    assert store.counts()["QUEUED"] == 1
    assert store.counts()["FAILED"] == 1


def test_progress_labels():
    assert progress_label("QUEUED") == "Preparing"
    assert progress_label("ANALYZING") == "Listening"
    assert progress_label("SUCCEEDED") == "Ready"
    assert progress_label("SOURCE_WINS") == "Ready"
    assert progress_label("HUMAN_REQUIRED") == "Verifying"
    assert progress_label("FAILED") == "Failed"


def test_product_view_hides_internals(tmp_path):
    store = JobStore(tmp_path / "jobs.db")
    store.insert_job(_job(key="a"))
    job = store.get_job(OWNER, "job_user-alice_a")
    view = job.product_view()
    assert "workspace_path" not in view
    assert "source_asset_id" not in view
    assert "last_error" not in view
    assert view["status"] == "QUEUED"
    assert view["result_available"] is False
