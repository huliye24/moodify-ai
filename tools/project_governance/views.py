"""Derived views from the task ledger (023 Stage C).

Views are read-only projections: task table, conflict table, in-progress
table, awaiting-review table. Deterministic for identical input; timestamps
come from the ledger, never generated here.
"""

from __future__ import annotations

from tools.project_governance.ledger import TaskLedger


def build_task_table(ledger: TaskLedger) -> list[dict]:
    rows = []
    for task_id in ledger.all_task_ids():
        state, conflict = ledger.state_of(task_id)
        events = ledger.events_for(task_id)
        latest = events[-1] if events else None
        rows.append({
            "task_id": task_id,
            "state": state,
            "conflict": conflict,
            "last_event": latest.event_type if latest else None,
            "last_timestamp": latest.timestamp if latest else None,
            "event_count": len(events),
        })
    return sorted(rows, key=lambda r: r["task_id"])


def build_conflict_table(ledger: TaskLedger) -> list[dict]:
    rows = []
    for task_id in ledger.all_task_ids():
        state, conflict = ledger.state_of(task_id)
        if conflict:
            rows.append({"task_id": task_id, "state": state, "conflict": conflict})
    return sorted(rows, key=lambda r: r["task_id"])


def build_in_progress_table(ledger: TaskLedger) -> list[dict]:
    """PLANNED tasks are not yet started; in-progress means actively worked."""
    rows = []
    for task_id in ledger.all_task_ids():
        state, _ = ledger.state_of(task_id)
        if state in ("IN_PROGRESS", "REWORK"):
            rows.append({"task_id": task_id, "state": state})
    return sorted(rows, key=lambda r: r["task_id"])


def build_awaiting_review_table(ledger: TaskLedger) -> list[dict]:
    rows = []
    for task_id in ledger.all_task_ids():
        state, _ = ledger.state_of(task_id)
        if state == "READY_FOR_REVIEW":
            rows.append({"task_id": task_id, "state": state})
    return sorted(rows, key=lambda r: r["task_id"])
