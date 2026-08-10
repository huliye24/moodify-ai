"""Durable single-worker SQLite queue."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from .db import connect
from .models import Job, JobStatus


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime | None = None) -> str:
    return (value or _now()).isoformat()


def _row_to_job(row) -> Job:
    return Job(**dict(row))


class JobQueue:
    def __init__(self, db_path: Path, lease_seconds: int = 6 * 60 * 60):
        self.db_path = Path(db_path)
        self.lease_seconds = int(lease_seconds)
        with connect(self.db_path):
            pass

    def enqueue(self, source_path: Path, output_root: Path) -> Job:
        source = Path(source_path).resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        job_id = f"job_{uuid4().hex}"
        now = _iso()
        with connect(self.db_path) as con:
            con.execute(
                "INSERT INTO jobs(job_id,source_path,output_root,status,created_at,updated_at) "
                "VALUES(?,?,?,?,?,?)",
                (job_id, str(source), str(Path(output_root)), JobStatus.QUEUED.value, now, now),
            )
            row = con.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        return _row_to_job(row)

    def lease_next(self) -> Job | None:
        now = _now()
        lease_until = now + timedelta(seconds=self.lease_seconds)
        with connect(self.db_path) as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT * FROM jobs WHERE status=? ORDER BY created_at LIMIT 1",
                (JobStatus.QUEUED.value,),
            ).fetchone()
            if row is None:
                con.commit()
                return None
            job_id = row["job_id"]
            con.execute(
                "UPDATE jobs SET status=?, attempts=attempts+1, started_at=?, updated_at=?, lease_until=?, last_error=NULL "
                "WHERE job_id=? AND status=?",
                (
                    JobStatus.RUNNING.value,
                    _iso(now),
                    _iso(now),
                    _iso(lease_until),
                    job_id,
                    JobStatus.QUEUED.value,
                ),
            )
            row = con.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            con.commit()
        return _row_to_job(row)

    def succeed(self, job_id: str, case_dir: Path) -> None:
        now = _iso()
        with connect(self.db_path) as con:
            con.execute(
                "UPDATE jobs SET status=?, case_dir=?, finished_at=?, updated_at=?, lease_until=NULL WHERE job_id=?",
                (JobStatus.SUCCEEDED.value, str(case_dir), now, now, job_id),
            )

    def fail(self, job_id: str, error: str) -> None:
        now = _iso()
        with connect(self.db_path) as con:
            con.execute(
                "UPDATE jobs SET status=?, last_error=?, finished_at=?, updated_at=?, lease_until=NULL WHERE job_id=?",
                (JobStatus.FAILED.value, error[-8000:], now, now, job_id),
            )

    def requeue(self, job_id: str) -> None:
        now = _iso()
        with connect(self.db_path) as con:
            con.execute(
                "UPDATE jobs SET status=?, updated_at=?, started_at=NULL, finished_at=NULL, lease_until=NULL WHERE job_id=?",
                (JobStatus.QUEUED.value, now, job_id),
            )

    def recover_expired(self) -> int:
        now = _iso()
        with connect(self.db_path) as con:
            cur = con.execute(
                "UPDATE jobs SET status=?, updated_at=?, started_at=NULL, lease_until=NULL, "
                "last_error=COALESCE(last_error,'') || ? "
                "WHERE status=? AND lease_until IS NOT NULL AND lease_until < ?",
                (
                    JobStatus.QUEUED.value,
                    now,
                    "\nRecovered expired worker lease.",
                    JobStatus.RUNNING.value,
                    now,
                ),
            )
            return cur.rowcount

    def get(self, job_id: str) -> Job | None:
        with connect(self.db_path) as con:
            row = con.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        return _row_to_job(row) if row else None

    def list(self, status: str | None = None, limit: int = 100) -> list[Job]:
        with connect(self.db_path) as con:
            if status:
                rows = con.execute(
                    "SELECT * FROM jobs WHERE status=? ORDER BY created_at DESC LIMIT ?", (status, limit)
                ).fetchall()
            else:
                rows = con.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [_row_to_job(row) for row in rows]

    def counts(self) -> dict[str, int]:
        with connect(self.db_path) as con:
            rows = con.execute("SELECT status, COUNT(*) AS n FROM jobs GROUP BY status").fetchall()
        result = {status.value: 0 for status in JobStatus}
        result.update({row["status"]: row["n"] for row in rows})
        return result
