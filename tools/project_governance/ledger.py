"""Append-only task ledger — the single source of truth for task state.

State model (023 orchestration §4):
    PLANNED -> IN_PROGRESS -> READY_FOR_REVIEW -> REWORK -> ACCEPTED
                             -> HOLD

Event semantics:
- orchestration describes authorized scope and plan, not completion;
- handoff describes the executor's current delivery, not acceptance;
- acceptance is the acceptance fact written by the Judge;
- the ledger computes current state from ordered events and never overwrites
  history;
- conflicts are explicit — "last modification time wins" is forbidden.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

SCHEMA_VERSION = "moodify.task-ledger/0.1"

TASK_STATUSES = (
    "PLANNED",
    "IN_PROGRESS",
    "READY_FOR_REVIEW",
    "REWORK",
    "ACCEPTED",
    "HOLD",
)

EventType = Literal["orchestration", "handoff", "acceptance", "rework", "hold", "reconciliation"]

# precedence for deriving state from event type (023 §4)
_EVENT_TO_STATUS: dict[str, str] = {
    "orchestration": "PLANNED",
    "handoff": "READY_FOR_REVIEW",
    "acceptance": "ACCEPTED",
    "rework": "REWORK",
    "hold": "HOLD",
    "reconciliation": None,  # handled specially
}


@dataclass(frozen=True)
class LedgerEvent:
    schema_version: str
    task_id: str
    event_id: str
    event_type: EventType
    actor: str
    timestamp: str
    source: str
    evidence: str = ""
    supersedes: str | None = None
    status: str | None = None  # explicit status for reconciliation events

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "task_id": self.task_id,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "actor": self.actor,
            "timestamp": self.timestamp,
            "source": self.source,
            "evidence": self.evidence,
            "supersedes": self.supersedes,
            "status": self.status,
        }


@dataclass
class TaskLedger:
    events: list[LedgerEvent] = field(default_factory=list)

    def append(self, event: LedgerEvent) -> None:
        if event.event_id in {e.event_id for e in self.events}:
            raise ValueError(f"duplicate event_id: {event.event_id}")
        self.events.append(event)

    def events_for(self, task_id: str) -> list[LedgerEvent]:
        return [e for e in self.events if e.task_id == task_id]

    def state_of(self, task_id: str) -> tuple[str, str | None]:
        """(derived state, conflict note) — never 'last modified wins'."""
        return derive_state(self.events_for(task_id))

    def all_task_ids(self) -> list[str]:
        seen: list[str] = []
        for e in self.events:
            if e.task_id not in seen:
                seen.append(e.task_id)
        return seen


def new_event(
    task_id: str,
    event_id: str,
    event_type: EventType,
    actor: str,
    timestamp: str,
    source: str,
    evidence: str = "",
    supersedes: str | None = None,
    status: str | None = None,
) -> LedgerEvent:
    return LedgerEvent(
        schema_version=SCHEMA_VERSION,
        task_id=task_id,
        event_id=event_id,
        event_type=event_type,
        actor=actor,
        timestamp=timestamp,
        source=source,
        evidence=evidence,
        supersedes=supersedes,
        status=status,
    )


def derive_state(events: list[LedgerEvent]) -> tuple[str, str | None]:
    """Compute current state from the ordered event stream.

    Rule: the last non-reconciliation event's status wins, unless an
    acceptance is present and a later event silently degrades it (which is
    a conflict — accepted state must not be silently downgraded).
    """
    if not events:
        return "UNKNOWN", "no events"
    ordered = sorted(events, key=lambda e: e.timestamp)
    accepted_at = next((e for e in ordered if e.event_type == "acceptance"), None)
    conflict: str | None = None

    for event in ordered:
        if event.event_type == "reconciliation" and event.status:
            continue  # reconciliation records a fact, does not change state
        if event.event_type == "acceptance":
            continue  # acceptance sets state below
        # a handoff/rework after acceptance is a conflict (silent downgrade)
        if accepted_at is not None and event.timestamp > accepted_at.timestamp:
            if event.event_type in ("handoff", "rework", "hold"):
                conflict = (
                    f"event {event.event_id} ({event.event_type}) occurs after "
                    f"acceptance {accepted_at.event_id} without reconciliation"
                )
            continue

    if accepted_at is not None:
        return "ACCEPTED", conflict
    # last status-bearing event
    for event in reversed(ordered):
        if event.event_type == "reconciliation":
            continue
        status = _EVENT_TO_STATUS.get(event.event_type)
        if status:
            return status, conflict
    return "UNKNOWN", conflict or "no status-bearing event"


def save_ledger(ledger: TaskLedger, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = "\n".join(json.dumps(e.to_dict(), ensure_ascii=False, sort_keys=True) for e in ledger.events)
    path.write_text(lines + ("\n" if lines else ""), encoding="utf-8")
    return path


def load_ledger(path: Path) -> TaskLedger:
    if not path.exists():
        return TaskLedger()
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(LedgerEvent(**json.loads(line)))
    return TaskLedger(events=events)
