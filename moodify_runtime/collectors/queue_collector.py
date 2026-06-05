"""Collect queue state from the runtime task queue (JSONL).

MHP-812: Implement Queue Collector.
Reads queue.jsonl and produces a snapshot of queue depth, status distribution,
and abandonment risk.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass
class QueueSignal:
    """Queue state snapshot for the NightMetricRecord."""
    total_tasks: int = 0
    pending: int = 0
    claimed: int = 0
    running: int = 0
    done: int = 0
    failed: int = 0
    abandoned: int = 0
    # Additional metrics
    oldest_pending_minutes: float | None = None
    abandonment_risk_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class QueueCollector:
    """Collect queue state from the runtime task queue.

    Usage:
        collector = QueueCollector(queue_path)
        signal = collector.collect()
    """

    # Tasks that have been claimed or running longer than this threshold
    # (in seconds) are flagged as abandonment risks.
    ABANDONMENT_RISK_SECONDS = 3600  # 1 hour

    def __init__(self, queue_path: Path | None = None):
        self._path = queue_path

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def collect(self) -> dict[str, Any]:
        """Read queue state and return a dict suitable for NightMetricRecord."""
        tasks = self._load_tasks()
        return self._build_signal(tasks).to_dict()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _load_tasks(self) -> list[dict[str, Any]]:
        if not self._path or not self._path.exists():
            return []
        records: list[dict[str, Any]] = []
        with self._path.open("r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    records.append(json.loads(stripped))
                except json.JSONDecodeError:
                    continue
        return records

    def _build_signal(self, tasks: list[dict[str, Any]]) -> QueueSignal:
        status_counts: dict[str, int] = {}
        abandoned_risk = 0
        oldest_pending: float | None = None

        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        for t in tasks:
            status = t.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

            # Check abandonment risk for claimed/running tasks
            if status in ("claimed", "running"):
                started = t.get("started_at")
                if started:
                    try:
                        dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                        elapsed = (now - dt).total_seconds()
                        if elapsed > self.ABANDONMENT_RISK_SECONDS:
                            abandoned_risk += 1
                    except (ValueError, TypeError):
                        pass

            # Track oldest pending task
            if status == "pending":
                created = t.get("created_at")
                if created:
                    try:
                        dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        elapsed = (now - dt).total_seconds() / 60.0
                        if oldest_pending is None or elapsed > oldest_pending:
                            oldest_pending = elapsed
                    except (ValueError, TypeError):
                        pass

        return QueueSignal(
            total_tasks=len(tasks),
            pending=status_counts.get("pending", 0),
            claimed=status_counts.get("claimed", 0),
            running=status_counts.get("running", 0),
            done=status_counts.get("done", 0),
            failed=status_counts.get("failed", 0),
            abandoned=status_counts.get("abandoned", 0),
            oldest_pending_minutes=round(oldest_pending, 1) if oldest_pending else None,
            abandonment_risk_count=abandoned_risk,
        )
