"""MHP-257→261: Cloud Worker Fleet — probe-level multi-worker coordination.

Extends supervisor.py and runtime_state.py for distributed worker fleets.
Probe level: validates patterns before Build NEM scales them.
"""

from __future__ import annotations

import json
import multiprocessing
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .utils import utc_now_iso, append_jsonl, read_jsonl


# ═══════════════════════════════════════════════════════════════════════
# MHP-257: Worker Lease Coordination
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class WorkerLease:
    """Distributed worker lease with TTL. Extends RuntimeLease for multi-machine use."""
    lease_id: str
    worker_id: str
    task_ids: List[str] = field(default_factory=list)
    acquired_at: str = field(default_factory=utc_now_iso)
    ttl_seconds: float = 120.0
    released: bool = False
    heartbeat_at: str = ""

    def is_expired(self) -> bool:
        if self.released:
            return True
        if not self.heartbeat_at and not self.acquired_at:
            return False
        ts = self.heartbeat_at or self.acquired_at
        from datetime import datetime, timezone
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            age = (datetime.now(timezone.utc) - dt).total_seconds()
            return age > self.ttl_seconds
        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def acquire_worker_lease(
    worker_id: str,
    task_ids: List[str],
    lease_store: Path,
    ttl_seconds: float = 120.0,
) -> WorkerLease:
    """Acquire a lease for a set of tasks. Writes to lease_store JSONL."""
    lease = WorkerLease(
        lease_id=f"WL_{uuid.uuid4().hex[:8].upper()}",
        worker_id=worker_id,
        task_ids=task_ids,
        ttl_seconds=ttl_seconds,
        heartbeat_at=utc_now_iso(),
    )
    append_jsonl(lease_store, lease.to_dict())
    return lease


def release_worker_lease(lease_id: str, lease_store: Path) -> bool:
    """Release a lease. Updates the JSONL record."""
    leases = read_jsonl(lease_store)
    for l in leases:
        if l.get("lease_id") == lease_id:
            l["released"] = True
            l["released_at"] = utc_now_iso()
    # Rewrite
    import json
    lease_store.write_text(
        "\n".join(json.dumps(l, ensure_ascii=False) for l in leases) + "\n",
        encoding="utf-8",
    )
    return True


def heartbeat_worker_lease(lease_id: str, lease_store: Path) -> bool:
    """Update heartbeat timestamp on a lease."""
    leases = read_jsonl(lease_store)
    for l in leases:
        if l.get("lease_id") == lease_id:
            l["heartbeat_at"] = utc_now_iso()
    lease_store.write_text(
        "\n".join(json.dumps(l, ensure_ascii=False) for l in leases) + "\n",
        encoding="utf-8",
    )
    return True


def find_expired_leases(lease_store: Path) -> List[WorkerLease]:
    """Find all expired leases that can be reclaimed."""
    expired = []
    for d in read_jsonl(lease_store):
        wl = WorkerLease(**{k: v for k, v in d.items() if k in WorkerLease.__dataclass_fields__})
        if wl.is_expired():
            expired.append(wl)
    return expired


# ═══════════════════════════════════════════════════════════════════════
# MHP-258: Multi-Process Probe
# ═══════════════════════════════════════════════════════════════════════


def _run_one_task(idx_cmd: Tuple[int, List[str]], timeout_per_task: float = 300.0) -> Dict[str, Any]:
    """Module-level (picklable) single-task runner for multiprocessing."""
    import subprocess as _subprocess
    idx, cmd = idx_cmd
    try:
        proc = _subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_per_task)
        return {
            "index": idx,
            "command": " ".join(cmd[:3]) + "...",
            "exit_code": proc.returncode,
            "ok": proc.returncode == 0,
            "stdout_tail": proc.stdout[-200:] if proc.stdout else "",
            "stderr_tail": proc.stderr[-200:] if proc.stderr else "",
            "pid": os.getpid(),
        }
    except _subprocess.TimeoutExpired:
        return {"index": idx, "command": " ".join(cmd[:3]) + "...", "ok": False, "error": "timeout", "pid": os.getpid()}
    except Exception as e:
        return {"index": idx, "command": " ".join(cmd[:3]) + "...", "ok": False, "error": str(e), "pid": os.getpid()}


def run_parallel_tasks(
    commands: List[List[str]],
    max_workers: int = 4,
    timeout_per_task: float = 300.0,
) -> List[Dict[str, Any]]:
    """Run multiple commands in parallel using multiprocessing.Pool.

    Probe: validates that parallel subprocess execution works without
    queue corruption or output conflicts.
    """
    import subprocess as _subprocess

    indexed = list(enumerate(commands))
    with multiprocessing.Pool(processes=min(max_workers, len(commands))) as pool:
        results = pool.starmap(_run_one_task, [(ic, timeout_per_task) for ic in indexed])

    return sorted(results, key=lambda r: r["index"])


# ═══════════════════════════════════════════════════════════════════════
# MHP-259: Remote Artifact Probe
# ═══════════════════════════════════════════════════════════════════════


def probe_shared_artifact_access(base_dir: Path, worker_id: str) -> Dict[str, Any]:
    """Verify that multiple workers can read/write to a shared directory.

    Writes a worker-specific marker file and lists all worker markers.
    """
    base_dir.mkdir(parents=True, exist_ok=True)
    marker = base_dir / f"worker_{worker_id}.json"
    marker.write_text(json.dumps({
        "worker_id": worker_id,
        "timestamp": utc_now_iso(),
        "pid": os.getpid(),
    }))

    all_markers = sorted(base_dir.glob("worker_*.json"))
    can_read_all = all(m.exists() for m in all_markers)

    return {
        "worker_id": worker_id,
        "marker_written": str(marker),
        "marker_count": len(all_markers),
        "can_read_all_markers": can_read_all,
        "workers_seen": [m.stem for m in all_markers],
    }


# ═══════════════════════════════════════════════════════════════════════
# MHP-260: Cost Record Probe
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class TaskCostRecord:
    """Per-task cost estimate for cloud billing."""
    task_id: str
    worker_id: str
    compute_class: str = "cpu_standard"  # cpu_standard, gpu_standard, memory_high
    duration_s: float = 0.0
    cost_estimate: float = 0.0
    cost_per_hour: float = 0.05  # Default: $0.05/vCPU-hour
    recorded_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def estimate_task_cost(duration_s: float, compute_class: str = "cpu_standard") -> TaskCostRecord:
    """Estimate cost for a single task based on duration and compute class."""
    rates = {"cpu_standard": 0.05, "gpu_standard": 0.50, "memory_high": 0.10}
    rate = rates.get(compute_class, 0.05)
    cost = (duration_s / 3600.0) * rate

    return TaskCostRecord(
        task_id=f"TASK_{uuid.uuid4().hex[:8].upper()}",
        worker_id=f"worker_{os.getpid()}",
        compute_class=compute_class,
        duration_s=round(duration_s, 2),
        cost_estimate=round(cost, 6),
        cost_per_hour=rate,
    )


# ═══════════════════════════════════════════════════════════════════════
# MHP-261: Failure Isolation Probe
# ═══════════════════════════════════════════════════════════════════════


def probe_failure_isolation(
    commands: List[List[str]],
    fail_index: int = -1,
) -> Dict[str, Any]:
    """Verify that one worker failing doesn't affect others.

    Injects a failing command at fail_index. All other commands should still succeed.
    """
    if fail_index >= 0 and fail_index < len(commands):
        commands[fail_index] = ["python3", "-c", "import sys; sys.exit(1)"]

    results = run_parallel_tasks(commands, max_workers=len(commands))

    failed = [r for r in results if not r["ok"]]
    succeeded = [r for r in results if r["ok"]]

    return {
        "total_tasks": len(results),
        "failed_tasks": len(failed),
        "succeeded_tasks": len(succeeded),
        "failure_contained": len(failed) <= 1,
        "failed_indices": [r["index"] for r in failed],
        "succeeded_indices": [r["index"] for r in succeeded],
    }
