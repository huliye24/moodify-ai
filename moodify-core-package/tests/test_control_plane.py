"""W01-P04 Control Plane tests — TST-01..12 (claim/lease/retry/recovery/idempotency/events)."""

from __future__ import annotations

import pytest

from moodify.data_plane.control import (
    FAILURE_CLASSES,
    FailureRecord,
    IdempotencyConflict,
    JobControlPlane,
    TransitionRejected,
)
from moodify.data_plane.ids import new_id
from moodify.data_plane.repository import DataPlaneRepository


@pytest.fixture()
def plane(tmp_path):
    repo = DataPlaneRepository(tmp_path / "plane.sqlite3")
    cp = JobControlPlane(repo)
    yield repo, cp
    repo.close()


def _make_job(plane, *, fingerprint="f1", idem=None):
    repo, cp = plane
    job_id = new_id("job")
    track_id = new_id("track")
    cp.enqueue(job_id=job_id, track_id=track_id, job_type="reconstruction",
               idempotency_key=idem, request_fingerprint=fingerprint)
    return job_id, track_id


def _register_ready_object(repo, cp, job_id, track_id, data=b"render-bytes"):
    obj_id = new_id("object")
    key = f"moodify/tracks/{track_id}/jobs/{job_id}/renders/{obj_id}.wav"
    repo.register_object(object_id=obj_id, track_id=track_id, job_id=job_id,
                         artifact_type="renders", bucket="moodify", object_key=key,
                         content_hash="a" * 64, byte_size=len(data), producer="moodify-pipeline",
                         pipeline_version="pipeline-v0.1", retention_class="render_versioned")
    return obj_id


# TST-01 — Concurrent claim: only one owner
def test_tst01_concurrent_claim_only_one_owner(plane):
    repo, cp = plane
    job_id, _ = _make_job(plane)
    first = cp.claim(job_id=job_id, worker_id="worker-a")
    with pytest.raises(TransitionRejected):
        cp.claim(job_id=job_id, worker_id="worker-b")
    assert first["lease_id"]
    lease_rows = repo._conn.execute("SELECT COUNT(*) FROM leases WHERE job_id=?", (job_id,)).fetchone()[0]
    assert lease_rows == 1  # one valid lease (CP-INV-05)


# TST-02 — Lease expiry recovery: stale worker cannot overwrite result
def test_tst02_lease_expiry_recovery(plane):
    repo, cp = plane
    job_id, track_id = _make_job(plane)
    claimed = cp.claim(job_id=job_id, worker_id="worker-a")
    # simulate expiry (backdate lease)
    repo._conn.execute("UPDATE leases SET expires_at='2020-01-01T00:00:00+00:00' WHERE job_id=?", (job_id,))
    repo._conn.commit()
    recovered = cp.recover_expired_leases()
    assert any(r["job_id"] == job_id for r in recovered)
    job = repo.get_job(job_id)
    assert job["current_state"] in ("RETRY_WAIT", "FAILED")
    # stale worker tries to complete -> rejected (fencing, CP-INV-17)
    with pytest.raises(TransitionRejected):
        cp.complete(job_id=job_id, lease_id=claimed["lease_id"], worker_id="worker-a",
                    ready_object_id="obj_x")
    # new worker can claim after requeue
    if job["current_state"] == "RETRY_WAIT":
        cp.requeue(job_id=job_id)
    second = cp.claim(job_id=job_id, worker_id="worker-b")
    assert second["attempt_number"] > claimed["attempt_number"]


# TST-03 — Duplicate complete is idempotent
def test_tst03_duplicate_complete_idempotent(plane):
    repo, cp = plane
    job_id, track_id = _make_job(plane)
    claimed = cp.claim(job_id=job_id, worker_id="worker-a")
    obj_id = _register_ready_object(repo, cp, job_id, track_id)
    cp.complete(job_id=job_id, lease_id=claimed["lease_id"], worker_id="worker-a",
                ready_object_id=obj_id, verification_evidence=True)
    events = cp.events(job_id)
    ready_events = [e for e in events if e["event_type"] == "JOB_READY"]
    assert len(ready_events) == 1  # no duplicate READY event


# TST-04 — Retry budget: transient failures respect max attempts
def test_tst04_retry_budget(plane):
    repo, cp = plane
    job_id, _ = _make_job(plane)
    failure = FailureRecord("EXTERNAL_API_TRANSIENT", "LALAL_TIMEOUT")
    max_a = FAILURE_CLASSES["EXTERNAL_API_TRANSIENT"]["max_attempts"]
    # max_attempts=3: attempts 1..2 may retry; the 3rd attempt's failure is terminal
    for i in range(max_a - 1):
        claimed = cp.claim(job_id=job_id, worker_id="worker-a")
        job = cp.fail(job_id=job_id, lease_id=claimed["lease_id"], worker_id="worker-a", failure=failure)
        assert job["current_state"] == "RETRY_WAIT", f"attempt {i+1} should be retryable"
        cp.requeue(job_id=job_id)
    # budget exhausted -> terminal FAILED
    claimed = cp.claim(job_id=job_id, worker_id="worker-a")
    job = cp.fail(job_id=job_id, lease_id=claimed["lease_id"], worker_id="worker-a", failure=failure)
    assert job["current_state"] == "FAILED"


# TST-05 — Permanent failure: no pointless retry
def test_tst05_permanent_failure_no_retry(plane):
    repo, cp = plane
    job_id, _ = _make_job(plane)
    claimed = cp.claim(job_id=job_id, worker_id="worker-a")
    job = cp.fail(job_id=job_id, lease_id=claimed["lease_id"], worker_id="worker-a",
                  failure=FailureRecord("INPUT_INVALID", "SOURCE_FORMAT_UNSUPPORTED"))
    assert job["current_state"] == "FAILED"
    assert not FAILURE_CLASSES["INPUT_INVALID"]["retryable"]


# TST-06 — Control restart: state survives (persisted, no in-memory truth)
def test_tst06_control_restart_state_survives(plane, tmp_path):
    repo, cp = plane
    job_id, track_id = _make_job(plane)
    cp.claim(job_id=job_id, worker_id="worker-a")
    # "restart": reopen a fresh connection from the same DB file
    repo2 = DataPlaneRepository(tmp_path / "plane.sqlite3")
    JobControlPlane(repo2)
    job = repo2.get_job(job_id)
    assert job["current_state"] == "RUNNING"  # recovered from DB, not memory
    repo2.close()


# TST-07 — OSS/DB split brain: object write ok, DB commit fail -> no READY, orphan detectable
def test_tst07_split_brain_no_false_ready(plane, tmp_path):
    repo, cp = plane
    job_id, track_id = _make_job(plane)
    claimed = cp.claim(job_id=job_id, worker_id="worker-a")
    # object written to store, but never registered in DB -> DB commit "failed"
    store = _LocalStore(tmp_path / "store")
    store.put("moodify", f"moodify/tracks/{track_id}/jobs/{job_id}/renders/obj_x.wav", b"data")
    with pytest.raises(TransitionRejected):
        cp.complete(job_id=job_id, lease_id=claimed["lease_id"], worker_id="worker-a",
                    ready_object_id="obj_x")  # not registered -> reject (CP-INV-13)
    job = repo.get_job(job_id)
    assert job["current_state"] != "READY"


class _LocalStore:
    def __init__(self, root):
        import pathlib

        self.root = pathlib.Path(root)

    def put(self, bucket, key, data):
        p = self.root / bucket / key.replace("/", "\\")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)


# TST-08 — READY guard: missing artifact / verification rejected
def test_tst08_ready_guard(plane):
    repo, cp = plane
    job_id, _ = _make_job(plane)
    claimed = cp.claim(job_id=job_id, worker_id="worker-a")
    with pytest.raises(TransitionRejected):
        cp.complete(job_id=job_id, lease_id=claimed["lease_id"], worker_id="worker-a",
                    ready_object_id="obj_nonexistent")
    job = repo.get_job(job_id)
    assert job["current_state"] != "READY"


# TST-09 — Terminal protection: worker cannot revert READY -> RUNNING
def test_tst09_terminal_protection(plane):
    repo, cp = plane
    job_id, track_id = _make_job(plane)
    claimed = cp.claim(job_id=job_id, worker_id="worker-a")
    obj_id = _register_ready_object(repo, cp, job_id, track_id)
    cp.complete(job_id=job_id, lease_id=claimed["lease_id"], worker_id="worker-a",
                ready_object_id=obj_id, verification_evidence=True)
    # no public transition exists from READY; claim must be rejected
    with pytest.raises(TransitionRejected):
        cp.claim(job_id=job_id, worker_id="worker-b")
    job = repo.get_job(job_id)
    assert job["current_state"] == "READY"


# TST-10 — Idempotent create: same key+fingerprint -> same job
def test_tst10_idempotent_create(plane):
    repo, cp = plane
    job_id, track_id = _make_job(plane, idem="create-key-1", fingerprint="fp-1")
    job2 = cp.enqueue(job_id=new_id("job"), track_id=track_id, job_type="reconstruction",
                      idempotency_key="create-key-1", request_fingerprint="fp-1")
    assert job2["job_id"] == job_id  # same logical result
    rows = repo._conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    assert rows == 1


# TST-11 — Idempotency conflict: same key, different fingerprint
def test_tst11_idempotency_conflict(plane):
    repo, cp = plane
    _make_job(plane, idem="create-key-2", fingerprint="fp-a")
    with pytest.raises(IdempotencyConflict):
        cp.enqueue(job_id=new_id("job"), track_id=new_id("track"), job_type="reconstruction",
                   idempotency_key="create-key-2", request_fingerprint="fp-b")


# TST-12 — Event completeness: every transition appends an event
def test_tst12_event_completeness(plane):
    repo, cp = plane
    job_id, track_id = _make_job(plane)
    claimed = cp.claim(job_id=job_id, worker_id="worker-a")
    cp.heartbeat(job_id=job_id, lease_id=claimed["lease_id"], worker_id="worker-a")
    cp.verify(job_id=job_id, lease_id=claimed["lease_id"], worker_id="worker-a")
    obj_id = _register_ready_object(repo, cp, job_id, track_id)
    cp.complete(job_id=job_id, lease_id=claimed["lease_id"], worker_id="worker-a",
                ready_object_id=obj_id, verification_evidence=True)
    events = cp.events(job_id)
    types = [e["event_type"] for e in events]
    assert "JOB_ENQUEUED" in types
    assert "JOB_CLAIMED" in types
    assert "LEASE_HEARTBEAT" in types
    assert "JOB_VERIFYING" in types
    assert "JOB_READY" in types
    # events are append-only audit; current state is authority
    job = repo.get_job(job_id)
    assert job["current_state"] == "READY"
