"""MHP-098/110: Structured Runtime Event Schema and Writer.

Probe level (MHP-098): 5 event types for runtime telemetry.
Build level (MHP-110): Full event writer with JSONL output.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .utils import utc_now_iso


# ═══════════════════════════════════════════════════════════════════════
# Event types (Probe: 5 minimal types)
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class RuntimeEvent:
    """Base event. All events share these fields."""
    event_id: str
    event_type: str    # "task_started" | "task_completed" | "task_failed" | "heartbeat" | "run_summary"
    run_id: str
    timestamp: str = field(default_factory=utc_now_iso)
    task_id: str = ""
    sample_id: str = ""
    preset: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_jsonl(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False) + "\n"


class EventWriter:
    """Append-only JSONL event log for runtime telemetry.

    Usage:
        writer = EventWriter(output_dir / "runtime_events.jsonl")
        writer.emit(RuntimeEvent(event_id="ev1", event_type="task_started", ...))
    """

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._count = 0

    def emit(self, event: RuntimeEvent) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(event.to_jsonl())
        self._count += 1

    @property
    def count(self) -> int:
        return self._count


def make_task_started(run_id: str, task_id: str, sample_id: str, preset: str, input_path: str) -> RuntimeEvent:
    return RuntimeEvent(
        event_id=f"ts_{run_id}_{task_id}",
        event_type="task_started",
        run_id=run_id,
        task_id=task_id,
        sample_id=sample_id,
        preset=preset,
        extra={"input_path": input_path},
    )


def make_task_completed(run_id: str, task_id: str, sample_id: str, preset: str,
                        elapsed_s: float, exit_code: int, mrs_delta: Optional[float] = None) -> RuntimeEvent:
    return RuntimeEvent(
        event_id=f"tc_{run_id}_{task_id}",
        event_type="task_completed",
        run_id=run_id,
        task_id=task_id,
        sample_id=sample_id,
        preset=preset,
        extra={"elapsed_s": round(elapsed_s, 2), "exit_code": exit_code, "mrs_delta": mrs_delta},
    )


def make_task_failed(run_id: str, task_id: str, sample_id: str, preset: str,
                     error: str, exit_code: int, attempt: int) -> RuntimeEvent:
    return RuntimeEvent(
        event_id=f"tf_{run_id}_{task_id}",
        event_type="task_failed",
        run_id=run_id,
        task_id=task_id,
        sample_id=sample_id,
        preset=preset,
        extra={"error": error[:500], "exit_code": exit_code, "attempt": attempt},
    )


def make_heartbeat(run_id: str, active_tasks: int, completed: int, failed: int,
                   uptime_s: float, free_disk_gb: float) -> RuntimeEvent:
    return RuntimeEvent(
        event_id=f"hb_{run_id}_{int(uptime_s)}",
        event_type="heartbeat",
        run_id=run_id,
        extra={"active_tasks": active_tasks, "completed": completed,
               "failed": failed, "uptime_s": round(uptime_s, 1),
               "free_disk_gb": round(free_disk_gb, 1)},
    )


def make_run_summary(run_id: str, total: int, success: int, failed: int,
                     elapsed_s: float, exit_reason: str = "complete") -> RuntimeEvent:
    return RuntimeEvent(
        event_id=f"rs_{run_id}",
        event_type="run_summary",
        run_id=run_id,
        extra={"total_tasks": total, "success": success, "failed": failed,
               "elapsed_s": round(elapsed_s, 1), "exit_reason": exit_reason},
    )
