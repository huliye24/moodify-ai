"""Derived views from the task ledger (023 Stage C).

Read-only projections: task table, conflict table, in-progress table,
awaiting-review table, plus the validation gate summary. Deterministic for
identical ledger input.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.project_governance.gate import validate_ledger  # noqa: E402
from tools.project_governance.ledger import load_ledger  # noqa: E402
from tools.project_governance.views import (  # noqa: E402
    build_awaiting_review_table,
    build_conflict_table,
    build_in_progress_table,
    build_task_table,
)


def build_report(ledger_path: Path) -> dict:
    ledger = load_ledger(ledger_path)
    issues = validate_ledger(ledger)
    report = {
        "schema": "moodify.task-report/0.1",
        "tasks": len(ledger.all_task_ids()),
        "events": len(ledger.events),
        "validation_issues": issues,
        "task_table": build_task_table(ledger),
        "conflict_table": build_conflict_table(ledger),
        "in_progress_table": build_in_progress_table(ledger),
        "awaiting_review_table": build_awaiting_review_table(ledger),
    }
    return report


def main() -> int:
    ledger_path = Path(__file__).resolve().parents[2] / "project_analytics" / "task_ledger.jsonl"
    report = build_report(ledger_path)
    issue_count = len(report["validation_issues"])
    validation = "PASS" if issue_count == 0 else f"{issue_count} issues"
    print(f"ledger report: {ledger_path}")
    print(f"  tasks: {report['tasks']}  events: {report['events']}  validation: {validation}")
    print(f"  conflicts: {len(report['conflict_table'])}  in_progress: {len(report['in_progress_table'])}  "
          f"awaiting_review: {len(report['awaiting_review_table'])}")
    print("\n  task states:")
    for row in report["task_table"]:
        print(f"    {row['task_id']:48s} {row['state']}")
    if report["conflict_table"]:
        print("\n  conflicts:")
        for row in report["conflict_table"]:
            print(f"    {row['task_id']}: {row['conflict']}")

    target = ledger_path.parent / "task_report.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  report: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
