from datetime import datetime, timedelta, timezone

from moodify.node.db import connect
from moodify.node.queue import JobQueue


def _source(tmp_path, name="song.wav"):
    source = tmp_path / name
    source.write_bytes(b"test")
    return source


def test_queue_persists_across_process_restart(tmp_path):
    q1 = JobQueue(tmp_path / "node.sqlite3", lease_seconds=60)
    q1.enqueue(_source(tmp_path), tmp_path / "out")

    q2 = JobQueue(tmp_path / "node.sqlite3", lease_seconds=60)  # new instance, same db
    assert q2.counts()["QUEUED"] == 1


def test_fail_stores_error_and_increments_attempts(tmp_path):
    q = JobQueue(tmp_path / "node.sqlite3", lease_seconds=60)
    job = q.enqueue(_source(tmp_path), tmp_path / "out")
    q.lease_next()
    q.fail(job.job_id, "boom")

    failed = q.get(job.job_id)
    assert failed.status == "FAILED"
    assert failed.last_error == "boom"
    assert failed.attempts == 1

    q.requeue(job.job_id)
    q.lease_next()
    assert q.get(job.job_id).attempts == 2


def test_recover_expired_lease(tmp_path):
    source = tmp_path / "song.wav"
    source.write_bytes(b"test")
    q = JobQueue(tmp_path / "node.sqlite3", lease_seconds=60)
    job = q.enqueue(source, tmp_path / "out")
    q.lease_next()
    expired = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    with connect(q.db_path) as con:
        con.execute("UPDATE jobs SET lease_until=? WHERE job_id=?", (expired, job.job_id))
    assert q.recover_expired() == 1
    assert q.get(job.job_id).status == "QUEUED"


def test_recover_interrupted_worker_without_waiting_for_lease(tmp_path):
    q = JobQueue(tmp_path / "node.sqlite3", lease_seconds=6 * 60 * 60)
    job = q.enqueue(_source(tmp_path), tmp_path / "out")
    q.lease_next()

    assert q.recover_interrupted() == 1
    recovered = q.get(job.job_id)
    assert recovered.status == "QUEUED"
    assert recovered.lease_until is None
    assert "worker process restart" in recovered.last_error


def test_retry_or_fail_is_bounded(tmp_path):
    q = JobQueue(tmp_path / "node.sqlite3", lease_seconds=60)
    job = q.enqueue(_source(tmp_path), tmp_path / "out")
    for attempt in range(1, 4):
        q.lease_next()
        status = q.retry_or_fail(job.job_id, f"failure {attempt}", max_attempts=3)
        assert status == ("QUEUED" if attempt < 3 else "FAILED")
    failed = q.get(job.job_id)
    assert failed.attempts == 3
    assert failed.last_error == "failure 3"
