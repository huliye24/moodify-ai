"""MHP-096/108/109: Runtime State — heartbeat, lease, and resumable task state machine.

Probe level (MHP-096): File-based heartbeat to detect liveness.
Build level (MHP-108/109): Heartbeat lease model + resumable state machine.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .utils import utc_now_iso


# ═══════════════════════════════════════════════════════════════════════
# MHP-096: Heartbeat Probe
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class Heartbeat:
    """File-based heartbeat for liveness detection.

    Writes a tiny JSON file at regular intervals. An external watcher
    (or restart logic) checks the file's mtime to determine liveness.
    """
    path: Path
    interval: float = 15.0
    last_beat: float = 0.0

    def beat(self) -> float:
        """Write heartbeat file. Returns seconds since last beat."""
        now = time.time()
        elapsed = now - self.last_beat if self.last_beat > 0 else 0.0
        self.last_beat = now
        payload = {
            "timestamp": utc_now_iso(),
            "pid": __import__("os").getpid(),
            "elapsed_since_last": round(elapsed, 2),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload), encoding="utf-8")
        return elapsed

    def age_seconds(self) -> float:
        """How many seconds since the last heartbeat?"""
        if not self.path.exists():
            return float("inf")
        return time.time() - self.path.stat().st_mtime

    def is_alive(self, max_age: float = 60.0) -> bool:
        """True if last heartbeat was within max_age seconds."""
        return self.age_seconds() <= max_age


# ═══════════════════════════════════════════════════════════════════════
# MHP-108: Runtime Lease Model
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class RuntimeLease:
    """Lease model for multi-runner coordination.

    A runner acquires a lease before processing. The lease has a TTL.
    If the runner crashes, the lease expires and another runner can take over.
    """
    lease_id: str
    runner_id: str
    acquired_at: str = field(default_factory=utc_now_iso)
    expires_at: str = ""
    ttl_seconds: float = 300.0
    released: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lease_id": self.lease_id,
            "runner_id": self.runner_id,
            "acquired_at": self.acquired_at,
            "expires_at": self.expires_at,
            "ttl_seconds": self.ttl_seconds,
            "released": self.released,
        }


# ═══════════════════════════════════════════════════════════════════════
# MHP-109: Resumable Task State Machine
# ═══════════════════════════════════════════════════════════════════════

TASK_STATES = ("pending", "claimed", "running", "done", "failed", "abandoned")

VALID_TRANSITIONS = {
    "pending":    {"claimed", "abandoned"},
    "claimed":    {"running", "abandoned"},
    "running":    {"done", "failed"},
    "failed":     {"pending"},   # retry: reset to pending
    "done":       set(),         # terminal
    "abandoned":  {"pending"},   # recycle abandoned tasks
}


def transition_task(task: Dict[str, Any], new_state: str) -> Dict[str, Any]:
    """Validate and apply a state transition. Raises ValueError on invalid transition."""
    current = task.get("status", "pending")
    if current not in TASK_STATES:
        raise ValueError(f"unknown state: {current}")
    if new_state not in VALID_TRANSITIONS.get(current, set()):
        raise ValueError(f"invalid transition: {current} -> {new_state}")
    task["status"] = new_state
    task["status_updated_at"] = utc_now_iso()
    return task


def find_abandoned_tasks(tasks: List[Dict[str, Any]], max_age_minutes: float = 30.0) -> List[Dict[str, Any]]:
    """Find tasks stuck in 'claimed' or 'running' state beyond max_age."""
    abandoned = []
    now = time.time()
    for t in tasks:
        if t.get("status") not in ("claimed", "running"):
            continue
        updated = t.get("status_updated_at", t.get("created_at", ""))
        if not updated:
            continue
        try:
            # Parse ISO timestamp
            from datetime import datetime, timezone
            dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            age_minutes = (datetime.now(timezone.utc) - dt).total_seconds() / 60.0
            if age_minutes > max_age_minutes:
                abandoned.append(t)
        except (ValueError, TypeError):
            pass
    return abandoned


def resume_queue(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Scan queue for abandoned tasks and mark them for retry.

    Returns summary of what was found and action taken.
    """
    abandoned = find_abandoned_tasks(tasks)
    recycled = 0
    for t in abandoned:
        transition_task(t, "abandoned")
        transition_task(t, "pending")
        recycled += 1

    return {
        "total_tasks": len(tasks),
        "abandoned_found": len(abandoned),
        "recycled": recycled,
        "abandoned_ids": [t.get("task_id") for t in abandoned],
    }
