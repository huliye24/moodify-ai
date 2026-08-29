"""Durable single-worker SQLite store for reconstruction jobs (MFY-CR-P08).

The store persists the product-layer ReconstructionJob. Canonical production
truth (ProductionCase / EvidenceArtifact) lives in the job workspace, never
duplicated here. Lease/recovery semantics follow moodify.node.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path


from .contract import (
    TERMINAL_STATUSES,
    FailureInfo,
    JobStatus,
    ReconstructionJob,
    ReconstructionResult,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS reconstruction_jobs (
    job_id TEXT PRIMARY KEY,
    owner_id TEXT NOT NULL,
    source_asset_id TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    production_case_id TEXT,
    status TEXT NOT NULL,
    progress_stage TEXT,
    requested_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    failed_at TEXT,
    reconstruction_version TEXT NOT NULL,
    result_object_id TEXT,
    result_status TEXT,
    failure_code TEXT,
    failure_stage TEXT,
    retry_policy TEXT,
    attempts INTEGER NOT NULL DEFAULT 0,
    billing_state_placeholder TEXT NOT NULL DEFAULT 'NOT_IMPLEMENTED',
    privacy_policy_version TEXT NOT NULL DEFAULT 'privacy-policy-v0.1',
    training_permission INTEGER NOT NULL DEFAULT 0,
    public_demo_permission INTEGER NOT NULL DEFAULT 0,
    retention_policy TEXT NOT NULL DEFAULT 'retention-policy-v0.1',
    idempotency_key TEXT,
    workspace_path TEXT,
    cancel_requested INTEGER NOT NULL DEFAULT 0,
    lease_until TEXT,
    last_error TEXT,
    updated_at TEXT NOT NULL,
    UNIQUE(owner_id, source_sha256, reconstruction_version, idempotency_key)
);
CREATE INDEX IF NOT EXISTS idx_rj_status_created ON reconstruction_jobs(status, requested_at);
CREATE INDEX IF NOT EXISTS idx_rj_owner_status ON reconstruction_jobs(owner_id, status);

CREATE TABLE IF NOT EXISTS reconstruction_results (
    result_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES reconstruction_jobs(job_id),
    production_case_id TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    selected_candidate TEXT NOT NULL,
    audio_object_ref TEXT NOT NULL,
    reconstruction_version TEXT NOT NULL,
    plan_hash TEXT,
    engine_version TEXT NOT NULL,
    identity_status TEXT NOT NULL,
    technical_status TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_rr_job ON reconstruction_results(job_id);
"""


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime | None = None) -> str:
    return (value or _now()).isoformat()


def connect(db_path: Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, timeout=30.0)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    con.execute("PRAGMA busy_timeout=30000")
    con.executescript(SCHEMA)
    return con


def _row_to_job(row) -> ReconstructionJob:
    data = dict(row)
    data["training_permission"] = bool(data["training_permission"])
    data["public_demo_permission"] = bool(data["public_demo_permission"])
    data["cancel_requested"] = bool(data["cancel_requested"])
    return ReconstructionJob(**data)


class JobStore:
    """Persistent store; single-worker semantics (concurrency = 1)."""

    def __init__(self, db_path: Path, lease_seconds: int = 6 * 60 * 60):
        self.db_path = Path(db_path)
        self.lease_seconds = int(lease_seconds)
        with connect(self.db_path):
            pass

    # ---- create / read ----

    def insert_job(self, job: ReconstructionJob) -> ReconstructionJob:
        now = job.updated_at or _iso()
        with connect(self.db_path) as con:
            con.execute(
                "INSERT INTO reconstruction_jobs("
                " job_id, owner_id, source_asset_id, source_sha256, production_case_id,"
                " status, progress_stage, requested_at, started_at, completed_at, failed_at,"
                " reconstruction_version, result_object_id, result_status, failure_code,"
                " failure_stage, retry_policy, attempts, billing_state_placeholder,"
                " privacy_policy_version, training_permission, public_demo_permission,"
                " retention_policy, idempotency_key, workspace_path, cancel_requested,"
                " lease_until, last_error, updated_at)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    job.job_id, job.owner_id, job.source_asset_id, job.source_sha256,
                    job.production_case_id, job.status, job.progress_stage, job.requested_at,
                    job.started_at, job.completed_at, job.failed_at, job.reconstruction_version,
                    job.result_object_id, job.result_status, job.failure_code, job.failure_stage,
                    job.retry_policy, job.attempts, job.billing_state_placeholder,
                    job.privacy_policy_version, int(job.training_permission),
                    int(job.public_demo_permission), job.retention_policy, job.idempotency_key,
                    job.workspace_path, int(job.cancel_requested), job.lease_until,
                    job.last_error, now,
                ),
            )
        return self.get_job(job.owner_id, job.job_id)

    def get_job(self, owner_id: str, job_id: str) -> ReconstructionJob | None:
        """Owner-filtered read; cross-owner access returns None (deny via 404)."""
        with connect(self.db_path) as con:
            row = con.execute(
                "SELECT * FROM reconstruction_jobs WHERE job_id=? AND owner_id=?",
                (job_id, owner_id),
            ).fetchone()
        return _row_to_job(row) if row else None

    def find_existing(
        self,
        owner_id: str,
        source_sha256: str,
        reconstruction_version: str,
        idempotency_key: str | None,
    ) -> ReconstructionJob | None:
        """Idempotent lookup: same owner + source + version + key => existing job."""
        if not idempotency_key:
            return None
        with connect(self.db_path) as con:
            row = con.execute(
                "SELECT * FROM reconstruction_jobs WHERE owner_id=? AND source_sha256=? "
                "AND reconstruction_version=? AND idempotency_key=? ORDER BY requested_at LIMIT 1",
                (owner_id, source_sha256, reconstruction_version, idempotency_key),
            ).fetchone()
        return _row_to_job(row) if row else None

    def find_latest_success(
        self, owner_id: str, source_sha256: str, reconstruction_version: str
    ) -> ReconstructionJob | None:
        """Existing successful result for the same track/version (RETURN_EXISTING)."""
        with connect(self.db_path) as con:
            row = con.execute(
                "SELECT * FROM reconstruction_jobs WHERE owner_id=? AND source_sha256=? "
                "AND reconstruction_version=? AND status IN (?,?) "
                "ORDER BY completed_at DESC LIMIT 1",
                (owner_id, source_sha256, reconstruction_version,
                 JobStatus.SUCCEEDED.value, JobStatus.SOURCE_WINS.value),
            ).fetchone()
        return _row_to_job(row) if row else None

    # ---- lease / worker ----

    def lease_next(self) -> ReconstructionJob | None:
        """Claim the oldest QUEUED job; lease expires after lease_seconds."""
        now = _now()
        lease_until = now + timedelta(seconds=self.lease_seconds)
        with connect(self.db_path) as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT * FROM reconstruction_jobs WHERE status=? "
                "AND (lease_until IS NULL OR lease_until < ?) "
                "ORDER BY requested_at LIMIT 1",
                (JobStatus.QUEUED.value, _iso(now)),
            ).fetchone()
            if row is None:
                con.commit()
                return None
            job_id = row["job_id"]
            con.execute(
                "UPDATE reconstruction_jobs SET lease_until=?, attempts=attempts+1, "
                "updated_at=? WHERE job_id=? AND status=?",
                (_iso(lease_until), _iso(now), job_id, JobStatus.QUEUED.value),
            )
            row = con.execute(
                "SELECT * FROM reconstruction_jobs WHERE job_id=?", (job_id,)
            ).fetchone()
            con.commit()
        return _row_to_job(row)

    def recover_interrupted(self) -> int:
        """Requeue any non-terminal leased job (worker restart takeover).

        The worker is a single-process service: a fresh process owns every
        RUNNING/leased row left behind by its predecessor without waiting for
        the processing lease to expire (node semantics).
        """
        with connect(self.db_path) as con:
            cur = con.execute(
                "UPDATE reconstruction_jobs SET status=?, progress_stage=NULL, "
                "started_at=NULL, lease_until=NULL, "
                "last_error=COALESCE(last_error,'') || ? "
                "WHERE lease_until IS NOT NULL "
                "AND status NOT IN (?,?,?,?,?)",
                (
                    JobStatus.QUEUED.value,
                    "\nRecovered after worker process restart.",
                    JobStatus.HUMAN_REQUIRED.value, JobStatus.SUCCEEDED.value,
                    JobStatus.SOURCE_WINS.value, JobStatus.FAILED.value,
                    JobStatus.CANCELLED.value,
                ),
            )
            return cur.rowcount

    # ---- transitions ----

    def mark_started(self, job_id: str) -> None:
        now = _iso()
        with connect(self.db_path) as con:
            con.execute(
                "UPDATE reconstruction_jobs SET started_at=COALESCE(started_at,?), "
                "updated_at=? WHERE job_id=?", (now, now, job_id),
            )

    def update_progress(self, job_id: str, status: str, progress_stage: str | None = None) -> None:
        now = _iso()
        with connect(self.db_path) as con:
            con.execute(
                "UPDATE reconstruction_jobs SET status=?, progress_stage=?, updated_at=? "
                "WHERE job_id=?",
                (status, progress_stage, now, job_id),
            )

    def update_source_sha256(self, job_id: str, source_sha256: str) -> None:
        now = _iso()
        with connect(self.db_path) as con:
            con.execute(
                "UPDATE reconstruction_jobs SET source_sha256=?, updated_at=? WHERE job_id=?",
                (source_sha256, now, job_id),
            )

    def attach_case(self, job_id: str, production_case_id: str) -> None:
        now = _iso()
        with connect(self.db_path) as con:
            con.execute(
                "UPDATE reconstruction_jobs SET production_case_id=?, updated_at=? "
                "WHERE job_id=?", (production_case_id, now, job_id),
            )

    def succeed(
        self,
        job_id: str,
        status: str,
        result: ReconstructionResult | None = None,
        resource: dict | None = None,
    ) -> None:
        now = _iso()
        with connect(self.db_path) as con:
            if result is not None:
                con.execute(
                    "INSERT OR REPLACE INTO reconstruction_results("
                    " result_id, job_id, production_case_id, source_sha256, selected_candidate,"
                    " audio_object_ref, reconstruction_version, plan_hash, engine_version,"
                    " identity_status, technical_status, created_at)"
                    " VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        result.result_id, result.job_id, result.production_case_id,
                        result.source_sha256, result.selected_candidate, result.audio_object_ref,
                        result.reconstruction_version, result.plan_hash, result.engine_version,
                        result.identity_status, result.technical_status, result.created_at,
                    ),
                )
            con.execute(
                "UPDATE reconstruction_jobs SET status=?, result_object_id=?, "
                "result_status=?, completed_at=?, failed_at=NULL, lease_until=NULL, "
                "updated_at=? WHERE job_id=?",
                (status, result.result_id if result else None,
                 status if result else None, now, now, job_id),
            )

    def fail(self, job_id: str, failure: FailureInfo) -> None:
        now = _iso()
        with connect(self.db_path) as con:
            con.execute(
                "UPDATE reconstruction_jobs SET status=?, failure_code=?, failure_stage=?, "
                "retry_policy=?, last_error=?, failed_at=?, completed_at=NULL, "
                "lease_until=NULL, updated_at=? WHERE job_id=?",
                (JobStatus.FAILED.value, failure.failure_code, failure.stage,
                 failure.retry_policy, failure.internal_detail[-8000:], now, now, job_id),
            )

    def retry_or_fail(self, job_id: str, failure: FailureInfo, max_attempts: int = 3) -> str:
        """TRANSIENT failures requeue until the bounded unattended retry limit."""
        now = _iso()
        with connect(self.db_path) as con:
            row = con.execute(
                "SELECT attempts FROM reconstruction_jobs WHERE job_id=?", (job_id,)
            ).fetchone()
            if row is None:
                raise KeyError(job_id)
            retry = failure.retryable and int(row["attempts"]) < int(max_attempts)
            status = JobStatus.QUEUED.value if retry else JobStatus.FAILED.value
            con.execute(
                "UPDATE reconstruction_jobs SET status=?, failure_code=?, failure_stage=?, "
                "retry_policy=?, last_error=?, failed_at=?, completed_at=NULL, "
                "started_at=NULL, lease_until=NULL, updated_at=? WHERE job_id=?",
                (status, failure.failure_code, failure.stage, failure.retry_policy,
                 failure.internal_detail[-8000:], None if retry else now, now, job_id),
            )
        return status

    def request_cancel(self, owner_id: str, job_id: str) -> ReconstructionJob | None:
        """Cancel when safe: QUEUED/VALIDATING become CANCELLED; in-flight jobs
        are flagged and stop at the next stage boundary; terminal states refuse."""
        now = _iso()
        job = self.get_job(owner_id, job_id)
        if job is None:
            return None
        if job.status in TERMINAL_STATUSES:
            return job
        with connect(self.db_path) as con:
            if job.status in (JobStatus.QUEUED.value, JobStatus.VALIDATING.value):
                con.execute(
                    "UPDATE reconstruction_jobs SET status=?, completed_at=?, "
                    "lease_until=NULL, updated_at=? WHERE job_id=?",
                    (JobStatus.CANCELLED.value, now, now, job_id),
                )
            else:
                con.execute(
                    "UPDATE reconstruction_jobs SET cancel_requested=1, updated_at=? "
                    "WHERE job_id=?", (now, job_id),
                )
        return self.get_job(owner_id, job_id)

    def admin_cancel(self, job_id: str) -> None:
        now = _iso()
        with connect(self.db_path) as con:
            con.execute(
                "UPDATE reconstruction_jobs SET status=?, completed_at=?, "
                "lease_until=NULL, updated_at=? WHERE job_id=?",
                (JobStatus.CANCELLED.value, now, now, job_id),
            )

    # ---- result ----

    def get_result(self, owner_id: str, job_id: str) -> ReconstructionResult | None:
        job = self.get_job(owner_id, job_id)
        if job is None or job.result_object_id is None:
            return None
        with connect(self.db_path) as con:
            row = con.execute(
                "SELECT * FROM reconstruction_results WHERE job_id=?", (job_id,)
            ).fetchone()
        if row is None:
            return None
        return ReconstructionResult.from_dict(dict(row))

    # ---- listing ----

    def active_job_ids(self) -> set[str]:
        """Job ids currently leased (worker processing); sweeps must skip them."""
        with connect(self.db_path) as con:
            rows = con.execute(
                "SELECT job_id FROM reconstruction_jobs WHERE status NOT IN (?,?,?,?,?) "
                "AND lease_until IS NOT NULL",
                (JobStatus.HUMAN_REQUIRED.value, JobStatus.SUCCEEDED.value,
                 JobStatus.SOURCE_WINS.value, JobStatus.FAILED.value, JobStatus.CANCELLED.value),
            ).fetchall()
        return {row["job_id"] for row in rows}

    def list_jobs(self, owner_id: str, status: str | None = None, limit: int = 100) -> list[ReconstructionJob]:
        with connect(self.db_path) as con:
            if status:
                rows = con.execute(
                    "SELECT * FROM reconstruction_jobs WHERE owner_id=? AND status=? "
                    "ORDER BY requested_at DESC LIMIT ?", (owner_id, status, limit),
                ).fetchall()
            else:
                rows = con.execute(
                    "SELECT * FROM reconstruction_jobs WHERE owner_id=? "
                    "ORDER BY requested_at DESC LIMIT ?", (owner_id, limit),
                ).fetchall()
        return [_row_to_job(r) for r in rows]

    def counts(self) -> dict[str, int]:
        with connect(self.db_path) as con:
            rows = con.execute(
                "SELECT status, COUNT(*) AS n FROM reconstruction_jobs GROUP BY status"
            ).fetchall()
        result = {s.value: 0 for s in JobStatus}
        result.update({row["status"]: row["n"] for row in rows})
        return result
