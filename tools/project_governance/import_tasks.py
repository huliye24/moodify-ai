"""Import task events from the existing task directories into the ledger.

Scan rules (023 Stage A):
- orchestration event: 00_TASK_ORCHESTRATION.md exists (authorized scope)
- handoff event: HANDOFF.md exists with Status line
- acceptance event: CODEX_FINAL_ACCEPTANCE_*.md or CODEX_*ACCEPTANCE*.md exists
- conflicts are surfaced as reconciliation events, never resolved by
  last-modified-wins
"""

from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.project_governance.ledger import TaskLedger, load_ledger, new_event  # noqa: E402

TASKS_ROOT = Path(__file__).resolve().parents[2] / "docs" / "tasks" / "deepseek"


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def scan_task_dirs(root: Path = TASKS_ROOT) -> list[tuple[str, Path]]:
    """Return (task_id, dir) for directories containing orchestration."""
    tasks = []
    if not root.exists():
        return tasks
    for d in sorted(root.iterdir()):
        if d.is_dir() and (d / "00_TASK_ORCHESTRATION.md").exists():
            tasks.append((d.name, d))
    return tasks


def _handoff_status(handoff: Path) -> str:
    text = handoff.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^\*\*Status:\*\*\s*(\S+)", text, re.M)
    if m:
        return m.group(1)
    for line in text.splitlines()[:20]:
        if "Status" in line and ":" in line:
            return line.split(":", 1)[1].strip()
    return "UNKNOWN"


def _acceptance_files(task_dir: Path) -> list[Path]:
    return sorted(p for p in task_dir.glob("CODEX*ACCEPTANCE*.md") if p.is_file())


def build_import_events(now: str | None = None) -> list:
    """Build import events (idempotent: deterministic event_ids).

    Each task gets an ordered synthetic timeline (orchestration < handoff <
    acceptance) with incrementing seconds, so the state machine's
    timestamp ordering reflects the logical fact order, not an arbitrary
    import-time tie. A task whose handoff already reports acceptance gets
    a single acceptance event (no separate handoff event to avoid
    ACCEPTED -> ACCEPTED noise).
    """
    base = now or _utc_now()
    events = []
    for task_id, task_dir in scan_task_dirs():
        sequence = 0

        def stamp() -> str:
            nonlocal sequence
            sequence += 1
            return f"{base[:19]}{sequence:02d}Z"

        events.append(new_event(
            task_id=task_id,
            event_id=f"imp-orch-{task_id}",
            event_type="orchestration",
            actor="import",
            timestamp=stamp(),
            source=str(task_dir / "00_TASK_ORCHESTRATION.md"),
            evidence="orchestration file exists",
        ))
        handoff = task_dir / "HANDOFF.md"
        acceptance_files = _acceptance_files(task_dir)
        if handoff.exists():
            status = _handoff_status(handoff)
            if status in ("ACCEPTED", "ACCEPTED_AFTER_CODEX_FINISH_WITH_BENCHMARK_LIMITS"):
                events.append(new_event(
                    task_id=task_id,
                    event_id=f"imp-acceptance-{task_id}",
                    event_type="acceptance",
                    actor="import",
                    timestamp=stamp(),
                    source=str(handoff),
                    evidence=f"handoff status: {status}",
                ))
            else:
                events.append(new_event(
                    task_id=task_id,
                    event_id=f"imp-handoff-{task_id}",
                    event_type="handoff",
                    actor="import",
                    timestamp=stamp(),
                    source=str(handoff),
                    evidence=f"handoff status: {status}",
                ))
        for acc in acceptance_files:
            events.append(new_event(
                task_id=task_id,
                event_id=f"imp-acc-{task_id}-{acc.stem[:20]}",
                event_type="acceptance",
                actor="import",
                timestamp=stamp(),
                source=str(acc),
                evidence="Codex acceptance file exists",
            ))
    return events


def import_to_ledger(ledger_path: Path) -> tuple[TaskLedger, int]:
    """Import events into the ledger (append-only; skip existing event_ids)."""
    ledger = load_ledger(ledger_path)
    existing_ids = {e.event_id for e in ledger.events}
    added = 0
    for event in build_import_events():
        if event.event_id in existing_ids:
            continue
        ledger.append(event)
        added += 1
    return ledger, added


def main() -> int:
    ledger_path = Path(__file__).resolve().parents[2] / "project_analytics" / "task_ledger.jsonl"
    ledger, added = import_to_ledger(ledger_path)
    from tools.project_governance.ledger import save_ledger

    save_ledger(ledger, ledger_path)
    print(f"ledger: {ledger_path}")
    print(f"  tasks: {len(ledger.all_task_ids())}  events: {len(ledger.events)}  added: {added}")
    for task_id in sorted(ledger.all_task_ids()):
        state, conflict = ledger.state_of(task_id)
        flag = f"  CONFLICT: {conflict}" if conflict else ""
        print(f"  {task_id:48s} {state}{flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
