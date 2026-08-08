"""Governance cadence checks (023 Stage D).

- daily: lightweight — ledger validation, conflict count, in-progress count
- weekly: state review — accepted share, awaiting-review backlog
- stage: reconciliation — gate report + next-task-openable judgment

In-progress exceeding a configured cap only warns; nothing auto-closes.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.project_governance.gate import validate_ledger  # noqa: E402
from tools.project_governance.ledger import load_ledger  # noqa: E402
from tools.project_governance.views import (  # noqa: E402
    build_awaiting_review_table,
    build_conflict_table,
    build_in_progress_table,
)

IN_PROGRESS_CAP = 5  # warning threshold, not a hard gate


def daily_check(ledger_path: Path) -> dict:
    ledger = load_ledger(ledger_path)
    issues = validate_ledger(ledger)
    conflicts = build_conflict_table(ledger)
    in_progress = build_in_progress_table(ledger)
    awaiting = build_awaiting_review_table(ledger)
    warnings = []
    if len(in_progress) > IN_PROGRESS_CAP:
        warnings.append(f"in-progress count {len(in_progress)} exceeds cap {IN_PROGRESS_CAP} (warning only)")
    return {
        "check": "daily",
        "ledger_ok": not issues,
        "validation_issues": len(issues),
        "conflicts": len(conflicts),
        "in_progress": len(in_progress),
        "awaiting_review": len(awaiting),
        "warnings": warnings,
        "pass": not issues and not warnings,
    }


def weekly_check(ledger_path: Path) -> dict:
    ledger = load_ledger(ledger_path)
    states = [ledger.state_of(t)[0] for t in ledger.all_task_ids()]
    accepted = sum(1 for s in states if s == "ACCEPTED")
    total_started = sum(1 for s in states if s != "PLANNED")
    return {
        "check": "weekly",
        "tasks": len(states),
        "accepted": accepted,
        "started": total_started,
        "accepted_share_pct": round(100 * accepted / total_started, 1) if total_started else None,
        "awaiting_review": len(build_awaiting_review_table(ledger)),
        "pass": True,  # weekly is a review, not a pass/fail gate
    }


def stage_check(ledger_path: Path, *, openable_in_progress_cap: int = 5) -> dict:
    ledger = load_ledger(ledger_path)
    issues = validate_ledger(ledger)
    in_progress = len(build_in_progress_table(ledger))
    awaiting = len(build_awaiting_review_table(ledger))
    next_openable = (
        not issues
        and in_progress < openable_in_progress_cap
    )
    return {
        "check": "stage",
        "validation_ok": not issues,
        "in_progress": in_progress,
        "awaiting_review": awaiting,
        "next_task_openable": next_openable,
        "reason": (
            "ready"
            if next_openable
            else (f"ledger issues: {len(issues)}" if issues else f"in-progress cap reached ({in_progress})")
        ),
        "pass": next_openable,
    }


def main() -> int:
    ledger_path = Path(__file__).resolve().parents[2] / "project_analytics" / "task_ledger.jsonl"
    cadence = sys.argv[1] if len(sys.argv) > 1 else "daily"
    checks = {
        "daily": daily_check,
        "weekly": weekly_check,
        "stage": stage_check,
    }
    if cadence not in checks:
        print(f"ERROR: unknown cadence {cadence!r}; valid: daily | weekly | stage")
        return 2
    result = checks[cadence](ledger_path)
    print(f"cadence: {result}")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
