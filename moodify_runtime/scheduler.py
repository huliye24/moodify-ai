"""MHP-038: Cloud GPU Scheduler — production capacity layer.

Durable models: ComputeRequest, ComputeLease, ComputeRun, CostRecord.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import RuntimeConfig
from .utils import append_jsonl, read_jsonl, utc_now_iso


COMPUTE_CLASSES = {"cpu_standard", "gpu_standard", "gpu_deep", "studio_reserved"}


@dataclass(frozen=True)
class ComputeRequest:
    request_id: str
    job_id: str
    compute_class: str  # cpu_standard, gpu_standard, gpu_deep, studio_reserved
    priority: int = 5
    status: str = "queued"  # queued, leased, running, completed, failed
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ComputeLease:
    lease_id: str
    request_id: str
    job_id: str
    node_id: str
    compute_class: str
    leased_at: str = field(default_factory=utc_now_iso)
    expires_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ComputeRun:
    run_id: str
    lease_id: str
    request_id: str
    job_id: str
    status: str = "running"  # running, completed, failed
    started_at: str = field(default_factory=utc_now_iso)
    finished_at: str = ""
    node_id: str = ""
    exit_code: Optional[int] = None
    error: str = ""
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CostRecord:
    cost_id: str
    run_id: str
    job_id: str
    compute_class: str
    duration_seconds: float = 0.0
    estimated_cost: float = 0.0
    recorded_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ── Helpers ────────────────────────────────────────────────────────

COST_RATES = {
    "cpu_standard": 0.02,
    "gpu_standard": 0.15,
    "gpu_deep": 0.30,
    "studio_reserved": 0.50,
}


def _sid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12].upper()}"


def _sched_path(cfg: RuntimeConfig, entity: str) -> Path:
    cfg = cfg.resolved()
    return cfg.scheduler_data_dir / f"{entity}.jsonl"


# ── Schedule ───────────────────────────────────────────────────────


def schedule_job(
    cfg: RuntimeConfig, job_id: str, compute_class: str = "cpu_standard", priority: int = 5
) -> Dict[str, Any]:
    """Create a compute request for a job.  The request is queued; a lease is
    not automatically created — use allocate_lease to grant one."""
    if compute_class not in COMPUTE_CLASSES:
        raise ValueError(f"unknown compute_class={compute_class!r}; expected one of {sorted(COMPUTE_CLASSES)}")
    req = ComputeRequest(
        request_id=_sid("REQ"), job_id=job_id, compute_class=compute_class, priority=int(priority)
    )
    append_jsonl(_sched_path(cfg, "requests"), req.to_dict())
    return req.to_dict()


def allocate_lease(cfg: RuntimeConfig, request_id: str, node_id: str, ttl_minutes: int = 120) -> Dict[str, Any]:
    """Grant a compute lease for a queued request."""
    rows = read_jsonl(_sched_path(cfg, "requests"))
    req = None
    for r in rows:
        if r.get("request_id") == request_id:
            req = r
            break
    if not req:
        raise KeyError(f"request not found: {request_id}")

    from datetime import datetime, timedelta, timezone

    now = utc_now_iso()
    try:
        expires = (datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)).isoformat()
    except (OSError, ValueError):
        expires = ""

    lease = ComputeLease(
        lease_id=_sid("LSE"), request_id=request_id, job_id=req["job_id"],
        node_id=node_id, compute_class=req["compute_class"],
        leased_at=now, expires_at=expires,
    )
    append_jsonl(_sched_path(cfg, "leases"), lease.to_dict())
    return lease.to_dict()


def record_compute_run(
    cfg: RuntimeConfig, lease_id: str, request_id: str, job_id: str,
    status: str = "completed", exit_code: int = 0, error: str = "",
    node_id: str = "", duration_seconds: float = 0.0,
) -> Dict[str, Any]:
    """Record a completed (or failed) compute run and its cost."""
    run = ComputeRun(
        run_id=_sid("RUN"), lease_id=lease_id, request_id=request_id,
        job_id=job_id, status=status, exit_code=exit_code, error=error,
        node_id=node_id, finished_at=utc_now_iso(),
    )
    append_jsonl(_sched_path(cfg, "runs"), run.to_dict())

    # Locate compute class from parent request
    cc = "cpu_standard"
    for r in read_jsonl(_sched_path(cfg, "requests")):
        if r.get("request_id") == request_id:
            cc = r.get("compute_class", "cpu_standard")
            break

    rate = COST_RATES.get(cc, 0.02)
    cost = CostRecord(
        cost_id=_sid("COST"), run_id=run.run_id, job_id=job_id,
        compute_class=cc, duration_seconds=duration_seconds,
        estimated_cost=round(duration_seconds / 3600 * rate, 4),
    )
    append_jsonl(_sched_path(cfg, "costs"), cost.to_dict())
    return {"run": run.to_dict(), "cost": cost.to_dict()}


def list_scheduler_runs(cfg: RuntimeConfig) -> List[Dict[str, Any]]:
    return read_jsonl(_sched_path(cfg, "runs"))


def list_scheduler_costs(cfg: RuntimeConfig) -> List[Dict[str, Any]]:
    return sorted(read_jsonl(_sched_path(cfg, "costs")), key=lambda r: r.get("recorded_at", ""), reverse=True)
