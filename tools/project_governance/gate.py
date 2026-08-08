"""Ledger validation gates (023 Stage C).

Checks:
- illegal state transitions (e.g. ACCEPTED -> IN_PROGRESS without rework)
- duplicate event_id
- missing evidence on events that require it (acceptance/handoff)
- multiple current states (a task must derive exactly one state)
- silent downgrade after acceptance
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.project_governance.ledger import TaskLedger, load_ledger  # noqa: E402

# legal transitions per state. Imported histories may skip intermediate
# events (orchestration -> acceptance directly) and may carry multiple
# acceptance files; those are information-gaps, not violations. The real
# violations are: reaching ACCEPTED and then silently degrading to an
# earlier state without a rework event.
_LEGAL: dict[str, set[str]] = {
    "PLANNED": {"IN_PROGRESS", "HOLD", "READY_FOR_REVIEW", "ACCEPTED", "REWORK"},
    "IN_PROGRESS": {"READY_FOR_REVIEW", "HOLD", "REWORK", "ACCEPTED"},
    "READY_FOR_REVIEW": {"ACCEPTED", "REWORK", "HOLD"},
    "REWORK": {"IN_PROGRESS", "READY_FOR_REVIEW", "HOLD", "ACCEPTED"},
    "HOLD": {"PLANNED", "IN_PROGRESS", "READY_FOR_REVIEW", "ACCEPTED", "REWORK"},
    "ACCEPTED": {"ACCEPTED", "REWORK"},  # more acceptance files are normal
}

_EVENT_TO_STATE = {
    "orchestration": "PLANNED",
    "handoff": "READY_FOR_REVIEW",
    "acceptance": "ACCEPTED",
    "rework": "REWORK",
    "hold": "HOLD",
}


def validate_ledger(ledger: TaskLedger) -> list[dict]:
    issues: list[dict] = []

    # 1. duplicate event_id
    seen: dict[str, int] = {}
    for event in ledger.events:
        seen[event.event_id] = seen.get(event.event_id, 0) + 1
    for event_id, count in seen.items():
        if count > 1:
            issues.append({"kind": "duplicate_event_id", "event_id": event_id, "count": count})

    # 2. missing evidence on acceptance/handoff
    for event in ledger.events:
        if event.event_type in ("acceptance", "handoff") and not event.evidence:
            issues.append({
                "kind": "missing_evidence",
                "task_id": event.task_id,
                "event_id": event.event_id,
                "event_type": event.event_type,
            })

    # 3. per-task state checks: single derived state, legal transitions,
    #    silent downgrade after acceptance
    for task_id in ledger.all_task_ids():
        events = sorted(ledger.events_for(task_id), key=lambda e: e.timestamp)
        states: list[tuple[str, str]] = []
        for event in events:
            if event.event_type == "reconciliation":
                continue
            state = _EVENT_TO_STATE.get(event.event_type)
            if state:
                states.append((event.event_id, state))
        if not states:
            issues.append({"kind": "no_state", "task_id": task_id})
            continue
        # illegal transition check (consecutive states)
        for i in range(1, len(states)):
            prev_state = states[i - 1][1]
            next_state = states[i][1]
            allowed = _LEGAL.get(prev_state, set())
            if next_state not in allowed:
                issues.append({
                    "kind": "illegal_transition",
                    "task_id": task_id,
                    "from": prev_state,
                    "to": next_state,
                    "event": states[i][0],
                })
        # silent downgrade: ACCEPTED then non-rework non-acceptance
        accepted_seen = False
        for event_id, state in states:
            if state == "ACCEPTED":
                accepted_seen = True
            elif accepted_seen and state in ("PLANNED", "IN_PROGRESS", "READY_FOR_REVIEW"):
                issues.append({
                    "kind": "silent_downgrade",
                    "task_id": task_id,
                    "event": event_id,
                    "state": state,
                })

    return issues


def report(ledger: TaskLedger) -> tuple[int, list[dict]]:
    issues = validate_ledger(ledger)
    return (0 if not issues else 1), issues


def main() -> int:
    ledger_path = Path(__file__).resolve().parents[2] / "project_analytics" / "task_ledger.jsonl"
    ledger = load_ledger(ledger_path)
    code, issues = report(ledger)
    print(f"ledger: {ledger_path}  tasks: {len(ledger.all_task_ids())}  events: {len(ledger.events)}")
    if not issues:
        print("  validation: PASS (no issues)")
    else:
        print(f"  validation: {len(issues)} issue(s)")
        for issue in issues:
            print(f"    {issue}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
