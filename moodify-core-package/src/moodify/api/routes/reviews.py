"""Human review queue API — MFY_EAR_SCOPED_JUDGMENT_AND_HUMAN_ESCALATION_001.

Reviewer identity is recorded (never trusted from a client-supplied header);
auth enforcement for reviewers lands with the production identity package.
Retraction supersedes — the audit trail is never erased.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException

from moodify.authority.review_store import ALLOWED_DECISIONS, ReviewStore

router = APIRouter(prefix="/api/v1/auditory")


def _store() -> ReviewStore:
    root = Path(os.environ.get("MOODIFY_REVIEW_DB", "outputs/moodify_cases/review.sqlite3"))
    return ReviewStore(root)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("/reviews")
def list_reviews(status: str = "pending", limit: int = 100) -> dict:
    store = _store()
    if status == "pending":
        tasks = store.list_pending(limit=limit)
    elif status == "all":
        tasks = []
        with store._connect() as con:  # noqa: SLF001 — single-file ledger
            rows = con.execute("SELECT * FROM review_tasks ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            tasks = [store._row_dict(row) for row in rows]  # noqa: SLF001
    else:
        raise HTTPException(status_code=422, detail={"code": "STATUS_INVALID", "message": "status must be pending or all"})
    return {"reviews": tasks, "count": len(tasks)}


@router.get("/reviews/{case_id}")
def reviews_for_case(case_id: str) -> dict:
    tasks = _store().list_by_case(case_id)
    return {"reviews": tasks, "count": len(tasks)}


@router.post("/reviews/{task_id}/decide", status_code=200)
def decide(task_id: str, body: dict) -> dict:
    reviewer = str(body.get("reviewer") or "").strip()
    decision = str(body.get("decision") or "").strip()
    reason = str(body.get("reason") or "").strip()
    scope = str(body.get("scope") or "ear-review").strip()[:64]
    if not reviewer or not decision or not reason:
        raise HTTPException(status_code=422, detail={"code": "DECISION_FIELDS_REQUIRED", "message": "reviewer, decision and reason are required"})
    if decision not in ALLOWED_DECISIONS:
        raise HTTPException(status_code=422, detail={"code": "DECISION_INVALID", "message": f"decision must be one of {ALLOWED_DECISIONS}"})
    try:
        task = _store().decide(task_id, reviewer, decision, reason, scope, decision_version="v1.0", decided_at=_now())
    except KeyError:
        raise HTTPException(status_code=404, detail={"code": "REVIEW_NOT_FOUND", "message": "review task not found"}) from None
    except ValueError as exc:
        raise HTTPException(status_code=409, detail={"code": "REVIEW_STATE_CONFLICT", "message": str(exc)}) from None
    return {"review": task}


@router.post("/reviews/{task_id}/retract", status_code=200)
def retract(task_id: str, body: dict) -> dict:
    reviewer = str(body.get("reviewer") or "").strip()
    reason = str(body.get("reason") or "").strip()
    if not reviewer or not reason:
        raise HTTPException(status_code=422, detail={"code": "RETRACT_FIELDS_REQUIRED", "message": "reviewer and reason are required"})
    try:
        task = _store().retract(task_id, reviewer, reason, retracted_at=_now())
    except KeyError:
        raise HTTPException(status_code=404, detail={"code": "REVIEW_NOT_FOUND", "message": "review task not found"}) from None
    except ValueError as exc:
        raise HTTPException(status_code=409, detail={"code": "REVIEW_STATE_CONFLICT", "message": str(exc)}) from None
    return {"review": task}
