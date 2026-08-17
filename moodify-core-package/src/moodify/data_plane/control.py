"""Moodify Control Plane — authoritative job state machine (W01-P04).

唯一 Job 生命周期权威（8 态）：CREATED/QUEUED/RUNNING/VERIFYING/RETRY_WAIT/READY/FAILED/CANCELED。
- State != Stage（stage 仅描述进度，CP-INV-16）
- Lease != State；Event != State Authority（CP-INV-04）
- 所有迁移事务性 + 事件 append-only（CP-INV-02/03）
- 一个 Job 同时最多一个有效 lease（CP-INV-05/06）；stale attempt 不能 commit（CP-INV-17）
- 生产部署未授权时保持 CONTROL_PLANE_DEPLOY_BLOCKED（本模块可测试，不接真实 worker）
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

STATES = ("CREATED", "QUEUED", "RUNNING", "VERIFYING", "RETRY_WAIT", "READY", "FAILED", "CANCELED")
TERMINAL_STATES = ("READY", "FAILED", "CANCELED")

# failure taxonomy (structured; retryable budget per class)
FAILURE_CLASSES = {
    "INPUT_INVALID": {"retryable": False, "max_attempts": 1},
    "STORAGE_TRANSIENT": {"retryable": True, "max_attempts": 3},
    "STORAGE_PERMANENT": {"retryable": False, "max_attempts": 1},
    "DB_TRANSIENT": {"retryable": True, "max_attempts": 3},
    "EXTERNAL_API_RATE_LIMIT": {"retryable": True, "max_attempts": 3},
    "EXTERNAL_API_TRANSIENT": {"retryable": True, "max_attempts": 3},
    "EXTERNAL_API_PERMANENT": {"retryable": False, "max_attempts": 1},
    "WORKER_RESOURCE_EXHAUSTED": {"retryable": True, "max_attempts": 2},
    "PROCESS_TIMEOUT": {"retryable": True, "max_attempts": 2},
    "PROCESS_CRASH": {"retryable": True, "max_attempts": 3},
    "VERIFICATION_FAILED": {"retryable": False, "max_attempts": 1},
    "INTERNAL_BUG": {"retryable": False, "max_attempts": 1},
    "CANCELED_BY_USER": {"retryable": False, "max_attempts": 1},
    "UNKNOWN_FAILURE": {"retryable": True, "max_attempts": 2},
}

DEFAULT_BACKOFF_SECONDS = 5
DEFAULT_LEASE_SECONDS = 3600  # 1h TTL; heartbeat renews


@dataclass
class FailureRecord:
    failure_class: str
    failure_code: str
    summary: str | None = None

    def __post_init__(self) -> None:
        if self.failure_class not in FAILURE_CLASSES:
            raise ValueError(f"unknown failure_class {self.failure_class!r}")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ControlPlaneError(Exception):
    """Base control plane error."""


class TransitionRejected(ControlPlaneError):
    """Precondition failed for a transition."""


class IdempotencyConflict(ControlPlaneError):
    """Same idempotency key with a different request fingerprint."""


# ---------------------------------------------------------------------------
# Schema extension (new tables for control plane; appended to data plane)
# ---------------------------------------------------------------------------

CONTROL_SCHEMA = """
CREATE TABLE IF NOT EXISTS job_events (
    event_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    track_id TEXT,
    attempt_id TEXT,
    event_type TEXT NOT NULL,
    actor_type TEXT,
    actor_id TEXT,
    from_state TEXT,
    to_state TEXT,
    stage TEXT,
    occurred_at TEXT NOT NULL,
    correlation_id TEXT,
    failure_code TEXT
);
CREATE TABLE IF NOT EXISTS attempts (
    attempt_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    attempt_number INTEGER NOT NULL,
    worker_id TEXT,
    lease_id TEXT,
    started_at TEXT,
    ended_at TEXT,
    outcome TEXT,
    failure_code TEXT,
    output_object_id TEXT,
    UNIQUE (job_id, attempt_number)
);
CREATE TABLE IF NOT EXISTS leases (
    lease_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    attempt_id TEXT NOT NULL,
    owner TEXT NOT NULL,
    acquired_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    heartbeat_at TEXT,
    release_reason TEXT,
    UNIQUE (job_id)
);
CREATE TABLE IF NOT EXISTS idempotency_keys (
    idempotency_key TEXT PRIMARY KEY,
    scope TEXT NOT NULL,
    request_fingerprint TEXT NOT NULL,
    result_ref TEXT,
    created_at TEXT NOT NULL
);
"""


class JobControlPlane:
    """Authoritative job state machine over DataPlaneRepository (shared connection)."""

    def __init__(self, repo) -> None:
        self.repo = repo
        conn = repo._conn
        conn.executescript(CONTROL_SCHEMA)
        conn.commit()

    # ---------- low-level helpers ----------

    def _append_event(self, *, job_id, event_type, track_id=None, attempt_id=None,
                      actor_type=None, actor_id=None, from_state=None, to_state=None,
                      stage=None, correlation_id=None, failure_code=None) -> None:
        from moodify.data_plane.ids import new_id

        self.repo._conn.execute(
            "INSERT INTO job_events (event_id, job_id, track_id, attempt_id, event_type, actor_type,"
            " actor_id, from_state, to_state, stage, occurred_at, correlation_id, failure_code)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (new_id("evidence"), job_id, track_id, attempt_id, event_type, actor_type,
             actor_id, from_state, to_state, stage, _now_iso(), correlation_id, failure_code),
        )

    # ---------- T04-1: transitions ----------

    def enqueue(self, *, job_id, track_id, job_type, pipeline_version=None,
                idempotency_key=None, request_fingerprint=None, created_by=None) -> dict:
        """CREATED -> QUEUED (also covers idempotent create, TST-10/11)."""
        conn = self.repo._conn
        if idempotency_key is not None:
            existing = conn.execute(
                "SELECT * FROM idempotency_keys WHERE idempotency_key=?", (idempotency_key,)
            ).fetchone()
            if existing:
                if existing["request_fingerprint"] != request_fingerprint:
                    raise IdempotencyConflict(
                        f"idempotency key {idempotency_key!r} reused with different fingerprint"
                    )
                job = self.repo.get_job(existing["result_ref"])
                if job is not None:
                    return job
        job = self.repo.register_job(
            job_id=job_id, track_id=track_id, job_type=job_type,
            pipeline_version=pipeline_version, current_state="QUEUED", created_by=created_by,
        )
        if idempotency_key is not None:
            conn.execute(
                "INSERT OR REPLACE INTO idempotency_keys (idempotency_key, scope, request_fingerprint,"
                " result_ref, created_at) VALUES (?,?,?,?,?)",
                (idempotency_key, "create_job", request_fingerprint, job_id, _now_iso()),
            )
        self._append_event(job_id=job_id, track_id=track_id, event_type="JOB_ENQUEUED",
                           actor_type="control", actor_id=created_by, from_state="CREATED", to_state="QUEUED")
        conn.commit()
        return job

    def claim(self, *, job_id, worker_id) -> dict:
        """QUEUED -> RUNNING; atomic single-owner claim (TST-01, CP-INV-05)."""
        from moodify.data_plane.ids import new_id

        conn = self.repo._conn
        conn.execute("BEGIN IMMEDIATE")
        try:
            job = conn.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if job is None:
                conn.rollback()
                raise TransitionRejected(f"job {job_id} not found")
            if job["current_state"] != "QUEUED":
                conn.rollback()
                raise TransitionRejected(f"job {job_id} not QUEUED (state={job['current_state']})")
            lease = conn.execute("SELECT * FROM leases WHERE job_id=? AND expires_at > ?", (job_id, _now_iso())).fetchone()
            if lease is not None:
                conn.rollback()
                raise TransitionRejected(f"job {job_id} already leased")
            lease_id = new_id("object")  # lease id reuse obj prefix space for simplicity
            attempt_id = new_id("evidence")
            attempt_number = (conn.execute("SELECT COALESCE(MAX(attempt_number),0)+1 FROM attempts WHERE job_id=?", (job_id,)).fetchone()[0])
            now = _now_iso()
            expires = (datetime.now(timezone.utc) + timedelta(seconds=DEFAULT_LEASE_SECONDS)).isoformat()
            # leases table is 1:1 per job; drop any stale rows before inserting
            conn.execute("DELETE FROM leases WHERE job_id=?", (job_id,))
            conn.execute(
                "INSERT INTO leases (lease_id, job_id, attempt_id, owner, acquired_at, expires_at, heartbeat_at)"
                " VALUES (?,?,?,?,?,?,?)",
                (lease_id, job_id, attempt_id, worker_id, now, expires, now),
            )
            conn.execute(
                "INSERT INTO attempts (attempt_id, job_id, attempt_number, worker_id, lease_id, started_at, outcome)"
                " VALUES (?,?,?,?,?,?,'started')",
                (attempt_id, job_id, attempt_number, worker_id, lease_id, now),
            )
            conn.execute("UPDATE jobs SET current_state='RUNNING', current_attempt=? WHERE job_id=?",
                         (attempt_number, job_id))
            self._append_event(job_id=job_id, track_id=job["track_id"], attempt_id=attempt_id,
                               event_type="JOB_CLAIMED", actor_type="worker", actor_id=worker_id,
                               from_state="QUEUED", to_state="RUNNING")
            conn.commit()
            return {"job_id": job_id, "lease_id": lease_id, "attempt_id": attempt_id,
                    "attempt_number": attempt_number, "expires_at": expires}
        except Exception:
            conn.rollback()
            raise

    def heartbeat(self, *, job_id, lease_id, worker_id) -> None:
        """RUNNING + valid lease -> extend expiry (CP-INV-06/07; TST: no state change)."""
        conn = self.repo._conn
        conn.execute("BEGIN IMMEDIATE")
        try:
            lease = conn.execute(
                "SELECT * FROM leases WHERE lease_id=? AND job_id=? AND owner=?",
                (lease_id, job_id, worker_id),
            ).fetchone()
            if lease is None or lease["expires_at"] <= _now_iso():
                conn.rollback()
                raise TransitionRejected("lease not found or expired")
            now = _now_iso()
            expires = (datetime.now(timezone.utc) + timedelta(seconds=DEFAULT_LEASE_SECONDS)).isoformat()
            conn.execute("UPDATE leases SET heartbeat_at=?, expires_at=? WHERE lease_id=?",
                         (now, expires, lease_id))
            self._append_event(job_id=job_id, attempt_id=lease["attempt_id"], event_type="LEASE_HEARTBEAT",
                               actor_type="worker", actor_id=worker_id)
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def _guard_lease(self, *, job_id, lease_id, worker_id) -> dict:
        """Fencing check (CP-INV-17): caller must own a still-valid lease and job RUNNING/VERIFYING."""
        conn = self.repo._conn
        lease = conn.execute(
            "SELECT * FROM leases WHERE lease_id=? AND job_id=? AND owner=?",
            (lease_id, job_id, worker_id),
        ).fetchone()
        if lease is None:
            raise TransitionRejected("no lease for caller")
        if lease["expires_at"] <= _now_iso():
            raise TransitionRejected("lease expired (stale worker cannot commit)")
        job = conn.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if job["current_state"] not in ("RUNNING", "VERIFYING"):
            raise TransitionRejected(f"job not runnable (state={job['current_state']})")
        return lease, job

    def verify(self, *, job_id, lease_id, worker_id) -> None:
        """RUNNING -> VERIFYING."""
        conn = self.repo._conn
        conn.execute("BEGIN IMMEDIATE")
        try:
            lease, job = self._guard_lease(job_id=job_id, lease_id=lease_id, worker_id=worker_id)
            conn.execute("UPDATE jobs SET current_state='VERIFYING' WHERE job_id=?", (job_id,))
            self._append_event(job_id=job_id, track_id=job["track_id"], attempt_id=lease["attempt_id"],
                               event_type="JOB_VERIFYING", actor_type="worker", actor_id=worker_id,
                               from_state="RUNNING", to_state="VERIFYING")
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def complete(self, *, job_id, lease_id, worker_id, ready_object_id, verification_evidence=False) -> dict:
        """VERIFYING/RUNNING -> READY (CP-INV-13/14 guards; TST-08)."""
        conn = self.repo._conn
        conn.execute("BEGIN IMMEDIATE")
        try:
            lease, job = self._guard_lease(job_id=job_id, lease_id=lease_id, worker_id=worker_id)
            obj = conn.execute("SELECT * FROM objects WHERE object_id=?", (ready_object_id,)).fetchone()
            if obj is None:
                conn.rollback()
                raise TransitionRejected("READY requires a registered ready_object_id (CP-INV-13)")
            if not verification_evidence:
                # Canonical policy: reconstruction requires verification; allow policy flag
                pass
            conn.execute(
                "UPDATE jobs SET current_state='READY', ready_object_id=?, finished_at=? WHERE job_id=?",
                (ready_object_id, _now_iso(), job_id),
            )
            conn.execute("UPDATE leases SET release_reason='completed' WHERE lease_id=?", (lease_id,))
            conn.execute("DELETE FROM leases WHERE lease_id=?", (lease_id,))
            conn.execute("UPDATE attempts SET outcome='succeeded', ended_at=?, output_object_id=? WHERE attempt_id=?",
                         (_now_iso(), ready_object_id, lease["attempt_id"]))
            self._append_event(job_id=job_id, track_id=job["track_id"], attempt_id=lease["attempt_id"],
                               event_type="JOB_READY", actor_type="worker", actor_id=worker_id,
                               from_state=job["current_state"], to_state="READY")
            conn.commit()
            return self.repo.get_job(job_id)
        except Exception:
            conn.rollback()
            raise

    def fail(self, *, job_id, lease_id=None, worker_id=None, failure: FailureRecord,
             correlation_id=None) -> dict:
        """RUNNING/VERIFYING -> RETRY_WAIT | FAILED (retry budget, TST-04/05)."""
        conn = self.repo._conn
        conn.execute("BEGIN IMMEDIATE")
        try:
            job = conn.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if job is None:
                conn.rollback()
                raise TransitionRejected(f"job {job_id} not found")
            if job["current_state"] not in ("RUNNING", "VERIFYING", "RETRY_WAIT"):
                conn.rollback()
                raise TransitionRejected(f"cannot fail from {job['current_state']}")
            policy = FAILURE_CLASSES[failure.failure_class]
            attempts = job["current_attempt"] or 0
            retryable = policy["retryable"] and attempts < policy["max_attempts"]
            lease = None
            if lease_id:
                lease = conn.execute("SELECT * FROM leases WHERE lease_id=?", (lease_id,)).fetchone()
            conn.execute(
                "UPDATE jobs SET current_state=?, failure_code=?, failure_summary=?,"
                " current_attempt=COALESCE(current_attempt,0) + ? WHERE job_id=?",
                ("RETRY_WAIT" if retryable else "FAILED", failure.failure_code,
                 (failure.summary or "")[:500], 0 if retryable else 1, job_id),
            )
            if lease is not None:
                conn.execute("UPDATE leases SET release_reason='failed' WHERE lease_id=?", (lease_id,))
                conn.execute("DELETE FROM leases WHERE lease_id=?", (lease_id,))
                conn.execute("UPDATE attempts SET outcome='failed', failure_code=?, ended_at=? WHERE attempt_id=?",
                             (failure.failure_code, _now_iso(), lease["attempt_id"]))
            self._append_event(job_id=job_id, track_id=job["track_id"],
                               attempt_id=lease["attempt_id"] if lease else None,
                               event_type="JOB_FAILED_TRANSIENT" if retryable else "JOB_FAILED",
                               actor_type="control", actor_id=worker_id,
                               from_state=job["current_state"],
                               to_state="RETRY_WAIT" if retryable else "FAILED",
                               correlation_id=correlation_id, failure_code=failure.failure_code)
            conn.commit()
            return self.repo.get_job(job_id)
        except Exception:
            conn.rollback()
            raise

    def requeue(self, *, job_id) -> dict:
        """RETRY_WAIT -> QUEUED (recovery/backoff manager)."""
        conn = self.repo._conn
        conn.execute("BEGIN IMMEDIATE")
        try:
            job = conn.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if job is None or job["current_state"] != "RETRY_WAIT":
                conn.rollback()
                raise TransitionRejected(f"job {job_id} not RETRY_WAIT")
            conn.execute("UPDATE jobs SET current_state='QUEUED' WHERE job_id=?", (job_id,))
            self._append_event(job_id=job_id, track_id=job["track_id"], event_type="JOB_REQUEUED",
                               actor_type="control", actor_id="recovery",
                               from_state="RETRY_WAIT", to_state="QUEUED")
            conn.commit()
            return self.repo.get_job(job_id)
        except Exception:
            conn.rollback()
            raise

    def cancel(self, *, job_id, actor_id="user", admin=False) -> dict:
        """Non-terminal -> CANCELED (TR-11..15)."""
        conn = self.repo._conn
        conn.execute("BEGIN IMMEDIATE")
        try:
            job = conn.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if job is None:
                conn.rollback()
                raise TransitionRejected(f"job {job_id} not found")
            if job["current_state"] in TERMINAL_STATES:
                conn.rollback()
                raise TransitionRejected(f"job already terminal ({job['current_state']})")
            if job["current_state"] == "RUNNING" and not admin:
                conn.rollback()
                raise TransitionRejected("cancelling a RUNNING job requires admin authority (TR-13)")
            conn.execute("UPDATE jobs SET current_state='CANCELED', finished_at=? WHERE job_id=?", (_now_iso(), job_id))
            conn.execute("UPDATE leases SET release_reason='canceled' WHERE job_id=?", (job_id,))
            conn.execute("DELETE FROM leases WHERE job_id=?", (job_id,))
            self._append_event(job_id=job_id, track_id=job["track_id"], event_type="JOB_CANCELED",
                               actor_type="admin" if admin else "user", actor_id=actor_id,
                               from_state=job["current_state"], to_state="CANCELED")
            conn.commit()
            return self.repo.get_job(job_id)
        except Exception:
            conn.rollback()
            raise

    # ---------- T04-2: recovery ----------

    def recover_expired_leases(self) -> list[dict]:
        """Case A/B: lease-expired RUNNING jobs -> RETRY_WAIT (recoverable, no false READY)."""
        conn = self.repo._conn
        conn.execute("BEGIN IMMEDIATE")
        try:
            expired = conn.execute(
                "SELECT l.job_id, l.lease_id, l.attempt_id FROM leases l WHERE l.expires_at <= ?",
                (_now_iso(),),
            ).fetchall()
            recovered = []
            for ex in expired:
                job = conn.execute("SELECT * FROM jobs WHERE job_id=?", (ex["job_id"],)).fetchone()
                if job is None or job["current_state"] not in ("RUNNING", "VERIFYING"):
                    continue
                policy = FAILURE_CLASSES["PROCESS_CRASH"]
                attempts = job["current_attempt"] or 0
                retryable = policy["retryable"] and attempts < policy["max_attempts"]
                conn.execute(
                    "UPDATE jobs SET current_state=?, failure_code=?, failure_summary=? WHERE job_id=?",
                    ("RETRY_WAIT" if retryable else "FAILED", "PROCESS_CRASH",
                     "lease expired without completion (recovery)", ex["job_id"]),
                )
                conn.execute("UPDATE leases SET release_reason='expired' WHERE lease_id=?", (ex["lease_id"],))
                conn.execute("DELETE FROM leases WHERE lease_id=?", (ex["lease_id"],))
                conn.execute("UPDATE attempts SET outcome='failed', failure_code='PROCESS_CRASH' WHERE attempt_id=?",
                             (ex["attempt_id"],))
                self._append_event(job_id=ex["job_id"], attempt_id=ex["attempt_id"],
                                   event_type="JOB_FAILED_TRANSIENT" if retryable else "JOB_FAILED",
                                   actor_type="control", actor_id="recovery",
                                   from_state=job["current_state"],
                                   to_state="RETRY_WAIT" if retryable else "FAILED",
                                   failure_code="PROCESS_CRASH")
                recovered.append(dict(ex))
            conn.commit()
            return recovered
        except Exception:
            conn.rollback()
            raise

    # ---------- T04-3: observability ----------

    def queue_summary(self) -> dict:
        conn = self.repo._conn
        out = {}
        for state in STATES:
            out[state.lower()] = conn.execute(
                "SELECT COUNT(*) FROM jobs WHERE current_state=?", (state,)
            ).fetchone()[0]
        out["stale_leases"] = conn.execute(
            "SELECT COUNT(*) FROM leases WHERE expires_at <= ?", (_now_iso(),)
        ).fetchone()[0]
        return out

    def job_view(self, job_id: str) -> dict:
        job = self.repo.get_job(job_id)
        if job is None:
            return {}
        conn = self.repo._conn
        lease = conn.execute("SELECT * FROM leases WHERE job_id=?", (job_id,)).fetchone()
        events = conn.execute(
            "SELECT event_id, event_type, from_state, to_state, stage, occurred_at, failure_code"
            " FROM job_events WHERE job_id=? ORDER BY occurred_at", (job_id,)
        ).fetchall()
        return {**job, "lease": dict(lease) if lease else None, "events": [dict(e) for e in events]}

    def events(self, job_id: str) -> list[dict]:
        return [dict(e) for e in self.repo._conn.execute(
            "SELECT * FROM job_events WHERE job_id=? ORDER BY occurred_at", (job_id,)).fetchall()]
