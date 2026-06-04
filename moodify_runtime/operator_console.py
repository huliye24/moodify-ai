from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import RuntimeConfig
from .utils import append_jsonl, read_jsonl, utc_now_iso

PROCESSING_DEPTHS = {
    "quick_scan",
    "standard_process",
    "deep_process",
    "studio_process",
}

JOB_STATUSES = {
    "waiting",
    "running",
    "gate_review",
    "reprocess",
    "delivered",
    "failed",
}


@dataclass(frozen=True)
class OperatorJob:
    job_id: str
    source_audio: str
    processing_depth: str
    status: str = "waiting"
    priority: int = 5
    project_label: str = ""
    customer_label: str = ""
    target_notes: str = ""
    delivery_mode: str = "report_bundle"
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    current_step: str = "intake"
    run_id: Optional[str] = None
    report_path: Optional[str] = None
    delivery_path: Optional[str] = None
    last_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CandidateVersion:
    candidate_id: str
    job_id: str
    output_path: str
    preset: str = ""
    processing_chain: str = ""
    created_at: str = field(default_factory=utc_now_iso)
    lineage: Dict[str, Any] = field(default_factory=dict)
    operator_note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ScoreResult:
    candidate_id: str
    job_id: str
    mrs_score: Optional[float] = None
    mrs_score_delta: Optional[float] = None
    over_dark_triggered: bool = False
    transient_damage: Optional[float] = None
    loudness_penalty: Optional[float] = None
    measured_at: str = field(default_factory=utc_now_iso)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GateDecision:
    candidate_id: str
    job_id: str
    decision: str
    reasons: List[str]
    decided_at: str = field(default_factory=utc_now_iso)
    required_mrs_delta: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DeliveryRecord:
    delivery_id: str
    job_id: str
    candidate_id: str
    final_audio_path: str
    report_path: str
    archive_path: str = ""
    operator_decision: str = "approved"
    delivered_at: str = field(default_factory=utc_now_iso)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12].upper()}"


def _operator_jobs_path(cfg: RuntimeConfig) -> Path:
    cfg = cfg.resolved()
    return cfg.operator_jobs_path


def create_operator_job(
    cfg: RuntimeConfig,
    source_audio: str | Path,
    processing_depth: str = "quick_scan",
    project_label: str = "",
    customer_label: str = "",
    target_notes: str = "",
    priority: int = 5,
    delivery_mode: str = "report_bundle",
) -> Dict[str, Any]:
    if processing_depth not in PROCESSING_DEPTHS:
        raise ValueError(
            f"unknown processing_depth={processing_depth!r}; "
            f"expected one of {sorted(PROCESSING_DEPTHS)}"
        )
    job = OperatorJob(
        job_id=_new_id("JOB"),
        source_audio=str(source_audio),
        processing_depth=processing_depth,
        priority=int(priority),
        project_label=project_label,
        customer_label=customer_label,
        target_notes=target_notes,
        delivery_mode=delivery_mode,
    )
    append_jsonl(_operator_jobs_path(cfg), job.to_dict())
    return job.to_dict()


def list_operator_jobs(cfg: RuntimeConfig, status: Optional[str] = None) -> List[Dict[str, Any]]:
    rows = read_jsonl(_operator_jobs_path(cfg))
    if status:
        rows = [row for row in rows if row.get("status") == status]
    return sorted(rows, key=lambda row: (int(row.get("priority", 5)), row.get("created_at") or ""))


def decide_candidate_gate(
    candidate_id: str,
    job_id: str,
    runtime_success: bool,
    mrs_score_delta: Optional[float] = None,
    required_mrs_delta: float = 0.0,
    over_dark_triggered: bool = False,
    transient_damage: Optional[float] = None,
    transient_threshold: float = 1.0,
    loudness_penalty: Optional[float] = None,
    loudness_penalty_threshold: float = 1.0,
) -> Dict[str, Any]:
    reasons: List[str] = []
    decision = "approve"

    if not runtime_success:
        reasons.append("runtime_failed")
        decision = "reject"

    if mrs_score_delta is None:
        reasons.append("mrs_delta_missing")
        if decision == "approve":
            decision = "reprocess"
    elif mrs_score_delta < required_mrs_delta:
        reasons.append("mrs_delta_below_threshold")
        if decision == "approve":
            decision = "reprocess"

    if over_dark_triggered:
        reasons.append("over_dark_triggered")
        if decision == "approve":
            decision = "reprocess"

    if transient_damage is not None and transient_damage > transient_threshold:
        reasons.append("transient_damage_above_threshold")
        decision = "reject"

    if loudness_penalty is not None and loudness_penalty > loudness_penalty_threshold:
        reasons.append("loudness_penalty_above_threshold")
        decision = "reject"

    if not reasons:
        reasons.append("all_gates_passed")

    return GateDecision(
        candidate_id=candidate_id,
        job_id=job_id,
        decision=decision,
        reasons=reasons,
        required_mrs_delta=required_mrs_delta,
    ).to_dict()
