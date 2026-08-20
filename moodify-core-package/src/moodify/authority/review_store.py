"""Human review queue & audit — sqlite ledger in the Ear node state dir.

MFY_EAR_SCOPED_JUDGMENT_AND_HUMAN_ESCALATION_001 §3:
- reviewer identity and permission
- read-only case/evidence snapshot reference (never copies private audio)
- review question, allowed decisions, reason fields
- reviewer, timestamp, scope, evidence refs, decision version
- conflict review & second review
- retraction keeps the full audit history; a human decision never mutates the
  original measurements or overwrites algorithm records — it adds an
  authority-decision layer.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS review_tasks (
    id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    escalation JSON NOT NULL,
    snapshot_ref TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    decided_at TEXT,
    reviewer TEXT,
    reviewer_scope TEXT,
    decision TEXT,
    decision_reason TEXT,
    decision_version TEXT,
    superseded_by TEXT,
    retracted_at TEXT,
    retract_reason TEXT
);
CREATE INDEX IF NOT EXISTS idx_review_pending ON review_tasks(status);
CREATE INDEX IF NOT EXISTS idx_review_case ON review_tasks(case_id);
"""

ALLOWED_DECISIONS = ("APPROVE", "REJECT", "NEEDS_MORE_EVIDENCE")


class ReviewStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as con:
            con.executescript(SCHEMA)

    def _connect(self):
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        return con

    def enqueue(self, case_id: str, reason: str, escalation: dict, snapshot_ref: str, created_at: str) -> dict:
        """Idempotent: a pending task for the same case+reason is not duplicated."""
        with self._connect() as con:
            existing = con.execute(
                "SELECT id FROM review_tasks WHERE case_id=? AND status='pending' AND reason=?",
                (case_id, reason),
            ).fetchone()
            if existing:
                task_id = existing["id"]
            else:
                task_id = uuid.uuid4().hex[:24]
                con.execute(
                    "INSERT INTO review_tasks (id, case_id, reason, escalation, snapshot_ref, status, created_at) VALUES (?,?,?,?,?,?,?)",
                    (task_id, case_id, reason, json.dumps(escalation, ensure_ascii=False), snapshot_ref, "pending", created_at),
                )
        return self.get(task_id)  # type: ignore[return-value]

    def list_pending(self, limit: int = 100) -> list[dict]:
        with self._connect() as con:
            rows = con.execute(
                "SELECT * FROM review_tasks WHERE status='pending' ORDER BY created_at ASC LIMIT ?", (limit,),
            ).fetchall()
            return [self._row_dict(row) for row in rows]

    def list_by_case(self, case_id: str) -> list[dict]:
        with self._connect() as con:
            rows = con.execute("SELECT * FROM review_tasks WHERE case_id=? ORDER BY created_at ASC", (case_id,)).fetchall()
            return [self._row_dict(row) for row in rows]

    def get(self, task_id: str) -> dict | None:
        with self._connect() as con:
            row = con.execute("SELECT * FROM review_tasks WHERE id=?", (task_id,)).fetchone()
            return self._row_dict(row) if row else None

    def decide(self, task_id: str, reviewer: str, decision: str, reason: str, scope: str, decision_version: str, decided_at: str) -> dict:
        if not reviewer or not reviewer.strip():
            raise ValueError("a reviewer identity is required to decide")
        if not reason or not reason.strip():
            raise ValueError("a decision reason is required")
        if decision not in ALLOWED_DECISIONS:
            raise ValueError(f"decision must be one of {ALLOWED_DECISIONS}")
        with self._connect() as con:
            row = con.execute("SELECT * FROM review_tasks WHERE id=?", (task_id,)).fetchone()
            if row is None:
                raise KeyError(task_id)
            if row["status"] != "pending":
                raise ValueError("task is not pending")
            con.execute(
                "UPDATE review_tasks SET status='decided', decided_at=?, reviewer=?, reviewer_scope=?, "
                "decision=?, decision_reason=?, decision_version=? WHERE id=?",
                (decided_at, reviewer, scope, decision, reason[:2000], decision_version, task_id),
            )
        return self.get(task_id)  # type: ignore[return-value]

    def retract(self, task_id: str, reviewer: str, retract_reason: str, retracted_at: str) -> dict:
        """Retraction supersedes a decision; the original record is never erased."""
        with self._connect() as con:
            row = con.execute("SELECT * FROM review_tasks WHERE id=?", (task_id,)).fetchone()
            if row is None:
                raise KeyError(task_id)
            if row["status"] != "decided":
                raise ValueError("only decided tasks can be retracted")
            if row["retracted_at"] is not None:
                raise ValueError("already retracted")
            con.execute(
                "UPDATE review_tasks SET status='retracted', retracted_at=?, retract_reason=? WHERE id=?",
                (retracted_at, f"{reviewer}: {retract_reason[:2000]}", task_id),
            )
        return self.get(task_id)  # type: ignore[return-value]

    def _row_dict(self, row: sqlite3.Row) -> dict:
        data = dict(row)
        data["escalation"] = json.loads(data["escalation"])
        return data
