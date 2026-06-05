"""Collect tidal cycle events from tidal_events.jsonl and tidal_heartbeat.json.

MHP-811: Implement Tidal Event Collector.
Extracts cycle counts, phase completion, and event rates from the tidal loop.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from moodify_runtime.utils import utc_now_iso


@dataclass
class TidalSignal:
    """Tidal cycle summary for the NightMetricRecord."""
    cycle_count: int = 0
    events_since_last: int = 0
    last_cycle_phases: list[str] = field(default_factory=list)
    last_heartbeat_at: str | None = None
    # Aggregate cycle stats
    total_tasks_processed: int = 0
    total_tasks_succeeded: int = 0
    total_tasks_failed: int = 0
    total_gate_approve: int = 0
    total_gate_reprocess: int = 0
    total_gate_reject: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TidalEventCollector:
    """Collect tidal cycle signals from tidal artifacts.

    Usage:
        collector = TidalEventCollector(events_path, heartbeat_path)
        signal = collector.collect()
    """

    def __init__(
        self,
        events_path: Path | None = None,
        heartbeat_path: Path | None = None,
    ):
        self._events_path = events_path
        self._heartbeat_path = heartbeat_path

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def collect(self) -> dict[str, Any]:
        """Collect tidal signals and return a dict suitable for NightMetricRecord."""
        events = self._load_events()
        heartbeat = self._load_heartbeat()
        return self._build_signal(events, heartbeat).to_dict()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _load_events(self) -> list[dict[str, Any]]:
        if not self._events_path or not self._events_path.exists():
            return []
        records: list[dict[str, Any]] = []
        with self._events_path.open("r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    records.append(json.loads(stripped))
                except json.JSONDecodeError:
                    continue
        return records

    def _load_heartbeat(self) -> dict[str, Any]:
        if not self._heartbeat_path or not self._heartbeat_path.exists():
            return {}
        with self._heartbeat_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _build_signal(
        self,
        events: list[dict[str, Any]],
        heartbeat: dict[str, Any],
    ) -> TidalSignal:
        cycles_seen: set[int] = set()
        phases: list[str] = []
        total_processed = 0
        total_succeeded = 0
        total_failed = 0
        gate_approve = 0
        gate_reprocess = 0
        gate_reject = 0

        for ev in events:
            cn = ev.get("cycle_number")
            if isinstance(cn, int):
                cycles_seen.add(cn)
            # Track phases from the most recent cycle
            phase = ev.get("phase", "")
            if phase and phase != "sleep":
                phases.append(phase)

            total_processed += ev.get("tasks_processed", 0)
            total_succeeded += ev.get("tasks_succeeded", 0)
            total_failed += ev.get("tasks_failed", 0)
            gate_approve += ev.get("gate_approve", 0)
            gate_reprocess += ev.get("gate_reprocess", 0)
            gate_reject += ev.get("gate_reject", 0)

        # Deduplicate phases keeping insertion order
        seen_phases: set[str] = set()
        unique_phases: list[str] = []
        for p in phases:
            if p not in seen_phases:
                seen_phases.add(p)
                unique_phases.append(p)

        return TidalSignal(
            cycle_count=len(cycles_seen),
            events_since_last=len(events),
            last_cycle_phases=unique_phases,
            last_heartbeat_at=heartbeat.get("last_heartbeat_at"),
            total_tasks_processed=total_processed,
            total_tasks_succeeded=total_succeeded,
            total_tasks_failed=total_failed,
            total_gate_approve=gate_approve,
            total_gate_reprocess=gate_reprocess,
            total_gate_reject=gate_reject,
        )
