"""Persistent stem job ledger (LALAL-STEMS-001).

Own SQLite file (stems.sqlite3) kept separate from the node worker queue:
paid tasks are never auto-retried, and a failed split attempt must stay
visible for operator reconciliation.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from moodify.compat import StrEnum

SCHEMA = """
CREATE TABLE IF NOT EXISTS stem_jobs (
    job_id TEXT PRIMARY KEY,
    source_name TEXT NOT NULL,
    source_path TEXT NOT NULL,
    source_bytes INTEGER NOT NULL,
    duration_seconds REAL,
    stems TEXT NOT NULL,
    extraction_level TEXT NOT NULL,
    splitter TEXT NOT NULL,
    dereverb_enabled INTEGER NOT NULL DEFAULT 0,
    multivocal TEXT,
    status TEXT NOT NULL,
    progress INTEGER NOT NULL DEFAULT 0,
    source_id TEXT,
    task_ids TEXT,
    presets TEXT,
    result_urls TEXT,
    estimated_pro_minutes REAL,
    last_error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    finished_at TEXT,
    last_checked_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_stem_jobs_status ON stem_jobs(status);
CREATE INDEX IF NOT EXISTS idx_stem_jobs_created ON stem_jobs(created_at);
"""

SOURCE_RETENTION_DAYS = 7


class StemStatus(StrEnum):
    PROCESSING = "PROCESSING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime | None = None) -> str:
    return (value or _now()).isoformat()


@dataclass
class StemJob:
    job_id: str
    source_name: str
    source_path: str
    source_bytes: int
    stems: list[str]
    extraction_level: str
    splitter: str
    status: str
    progress: int
    created_at: str
    updated_at: str
    dereverb_enabled: bool = False
    multivocal: str | None = None
    duration_seconds: float | None = None
    source_id: str | None = None
    task_ids: dict[str, str] = field(default_factory=dict)
    presets: dict[str, Any] | None = None
    result_urls: dict[str, str] = field(default_factory=dict)
    estimated_pro_minutes: float | None = None
    last_error: str | None = None
    finished_at: str | None = None
    last_checked_at: str | None = None

    @property
    def is_terminal(self) -> bool:
        return self.status in (StemStatus.SUCCEEDED, StemStatus.FAILED, StemStatus.CANCELLED)


def connect(path: Path) -> sqlite3.Connection:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, timeout=30.0)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    con.execute("PRAGMA busy_timeout=30000")
    con.executescript(SCHEMA)
    return con


def _row_to_job(row: sqlite3.Row) -> StemJob:
    return StemJob(
        job_id=row["job_id"],
        source_name=row["source_name"],
        source_path=row["source_path"],
        source_bytes=row["source_bytes"],
        stems=json.loads(row["stems"] or "[]"),
        extraction_level=row["extraction_level"],
        splitter=row["splitter"],
        status=row["status"],
        progress=row["progress"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        dereverb_enabled=bool(row["dereverb_enabled"]),
        multivocal=row["multivocal"],
        duration_seconds=row["duration_seconds"],
        source_id=row["source_id"],
        task_ids=json.loads(row["task_ids"] or "{}"),
        presets=json.loads(row["presets"]) if row["presets"] else None,
        result_urls=json.loads(row["result_urls"] or "{}"),
        estimated_pro_minutes=row["estimated_pro_minutes"],
        last_error=row["last_error"],
        finished_at=row["finished_at"],
        last_checked_at=row["last_checked_at"],
    )


class StemStore:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        with connect(self.db_path):
            pass

    def count(self) -> int:
        with connect(self.db_path) as con:
            row = con.execute("SELECT COUNT(*) AS n FROM stem_jobs").fetchone()
        return int(row["n"])

    def create(
        self,
        *,
        source_name: str,
        source_path: Path,
        source_bytes: int,
        stems: list[str],
        extraction_level: str,
        splitter: str,
        dereverb_enabled: bool = False,
        multivocal: str | None = None,
        duration_seconds: float | None = None,
        estimated_pro_minutes: float | None = None,
    ) -> StemJob:
        job_id = f"stem_{uuid4().hex}"
        now = _iso()
        with connect(self.db_path) as con:
            con.execute(
                "INSERT INTO stem_jobs(job_id, source_name, source_path, source_bytes, "
                "duration_seconds, stems, extraction_level, splitter, dereverb_enabled, "
                "multivocal, status, progress, estimated_pro_minutes, created_at, updated_at) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    job_id,
                    source_name,
                    str(Path(source_path).resolve()),
                    int(source_bytes),
                    duration_seconds,
                    json.dumps(list(stems)),
                    extraction_level,
                    splitter,
                    1 if dereverb_enabled else 0,
                    multivocal,
                    StemStatus.PROCESSING.value,
                    0,
                    estimated_pro_minutes,
                    now,
                    now,
                ),
            )
            row = con.execute("SELECT * FROM stem_jobs WHERE job_id=?", (job_id,)).fetchone()
        return _row_to_job(row)

    def get(self, job_id: str) -> StemJob | None:
        with connect(self.db_path) as con:
            row = con.execute("SELECT * FROM stem_jobs WHERE job_id=?", (job_id,)).fetchone()
        return _row_to_job(row) if row else None

    def list(self, status: str | None = None, limit: int = 50) -> list[StemJob]:
        with connect(self.db_path) as con:
            if status:
                rows = con.execute(
                    "SELECT * FROM stem_jobs WHERE status=? ORDER BY created_at DESC LIMIT ?",
                    (status, limit),
                ).fetchall()
            else:
                rows = con.execute(
                    "SELECT * FROM stem_jobs ORDER BY created_at DESC LIMIT ?", (limit,)
                ).fetchall()
        return [_row_to_job(row) for row in rows]

    def usage(self, limit: int = 20) -> dict:
        with connect(self.db_path) as con:
            agg = con.execute(
                "SELECT COUNT(*) AS total, "
                "SUM(CASE WHEN status='SUCCEEDED' THEN 1 ELSE 0 END) AS succeeded, "
                "SUM(CASE WHEN status='FAILED' THEN 1 ELSE 0 END) AS failed, "
                "SUM(CASE WHEN status='CANCELLED' THEN 1 ELSE 0 END) AS cancelled, "
                "SUM(source_bytes) AS bytes, SUM(estimated_pro_minutes) AS minutes "
                "FROM stem_jobs"
            ).fetchone()
            rows = con.execute(
                "SELECT job_id, stems, estimated_pro_minutes, status, created_at "
                "FROM stem_jobs ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return {
            "total_tasks": int(agg["total"] or 0),
            "succeeded": int(agg["succeeded"] or 0),
            "failed": int(agg["failed"] or 0),
            "cancelled": int(agg["cancelled"] or 0),
            "total_source_bytes": int(agg["bytes"] or 0),
            "total_estimated_pro_minutes": float(agg["minutes"] or 0.0),
            "recent": [
                {
                    "job_id": row["job_id"],
                    "stems": json.loads(row["stems"] or "[]"),
                    "estimated_pro_minutes": row["estimated_pro_minutes"],
                    "status": row["status"],
                    "created_at": row["created_at"],
                }
                for row in rows
            ],
        }

    def update_submitted(self, job_id: str, source_id: str, task_ids: dict[str, str]) -> None:
        now = _iso()
        with connect(self.db_path) as con:
            con.execute(
                "UPDATE stem_jobs SET source_id=?, task_ids=?, updated_at=?, last_checked_at=? "
                "WHERE job_id=?",
                (source_id, json.dumps(task_ids), now, now, job_id),
            )

    def update_status(
        self,
        job_id: str,
        *,
        status: StemStatus,
        progress: int | None = None,
        result_urls: dict[str, str] | None = None,
        presets: dict[str, Any] | None = None,
        last_error: str | None = None,
        checked: bool = True,
    ) -> None:
        now = _iso()
        sets = ["updated_at=?"]
        values: list[Any] = [now]
        if progress is not None:
            sets.append("progress=?")
            values.append(progress)
        if result_urls is not None:
            sets.append("result_urls=?")
            values.append(json.dumps(result_urls))
        if presets is not None:
            sets.append("presets=?")
            values.append(json.dumps(presets))
        if last_error is not None:
            sets.append("last_error=?")
            values.append(last_error[:8000])
        if status == StemStatus.SUCCEEDED:
            sets.append("finished_at=?")
            values.append(now)
        if status in (StemStatus.FAILED, StemStatus.CANCELLED):
            sets.append("finished_at=COALESCE(finished_at, ?)")
            values.append(now)
        sets.append("status=?")
        values.append(status.value)
        if checked:
            sets.append("last_checked_at=?")
            values.append(now)
        values.append(job_id)
        with connect(self.db_path) as con:
            con.execute(f"UPDATE stem_jobs SET {', '.join(sets)} WHERE job_id=?", values)

    def delete_source_file(self, job_id: str) -> None:
        """Remove the local source copy after upstream submission succeeded."""
        job = self.get(job_id)
        if job is None:
            return
        path = Path(job.source_path)
        try:
            if path.is_file():
                path.unlink()
        except OSError:
            pass

    def prune_old_sources(self, age_days: int = SOURCE_RETENTION_DAYS) -> int:
        """Delete stale source files still on disk and clear their paths."""
        cutoff = _iso(_now() - timedelta(days=age_days))
        removed = 0
        with connect(self.db_path) as con:
            rows = con.execute(
                "SELECT job_id, source_path FROM stem_jobs WHERE created_at < ?", (cutoff,)
            ).fetchall()
            for row in rows:
                path = Path(row["source_path"])
                try:
                    if path.is_file():
                        path.unlink()
                        removed += 1
                except OSError:
                    pass
                con.execute("UPDATE stem_jobs SET source_path='' WHERE job_id=?", (row["job_id"],))
        return removed
