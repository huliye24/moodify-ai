from __future__ import annotations

import csv
import hashlib
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import RuntimeConfig
from .utils import append_jsonl, atomic_write_json, atomic_write_jsonl, read_json, read_jsonl, utc_now_iso

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
    run_dir: Optional[str] = None
    report_path: Optional[str] = None
    detail_path: Optional[str] = None
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


def _stable_id(prefix: str, *parts: Any) -> str:
    h = hashlib.sha1()
    for part in parts:
        h.update(str(part).encode("utf-8", errors="ignore"))
        h.update(b"\0")
    return f"{prefix}_{h.hexdigest()[:12].upper()}"


def _operator_jobs_path(cfg: RuntimeConfig) -> Path:
    cfg = cfg.resolved()
    return cfg.operator_jobs_path


def _operator_detail_dir(cfg: RuntimeConfig) -> Path:
    cfg = cfg.resolved()
    return cfg.operator_detail_dir


def _operator_detail_path(cfg: RuntimeConfig, job_id: str) -> Path:
    return _operator_detail_dir(cfg) / f"{job_id}.json"


def _load_jobs(cfg: RuntimeConfig) -> List[Dict[str, Any]]:
    return read_jsonl(_operator_jobs_path(cfg))


def _rewrite_jobs(cfg: RuntimeConfig, rows: List[Dict[str, Any]]) -> None:
    atomic_write_jsonl(_operator_jobs_path(cfg), rows)


def _update_job(cfg: RuntimeConfig, job_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    rows = _load_jobs(cfg)
    for row in rows:
        if row.get("job_id") == job_id:
            row.update(updates)
            row["updated_at"] = utc_now_iso()
            _rewrite_jobs(cfg, rows)
            return row
    raise KeyError(f"operator job not found: {job_id}")


def _read_manifest(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"manifest not found: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _to_float(value: Any) -> Optional[float]:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> Optional[int]:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _flag_set(value: str) -> set[str]:
    return {part.strip() for part in (value or "").split(",") if part.strip()}


def _score_from_manifest(row: Dict[str, str]) -> tuple[Optional[float], Optional[float], Dict[str, Any]]:
    mrs_score = _to_float(row.get("mrs_open_v031_after"))
    mrs_delta = _to_float(row.get("delta_mrs_open_v031"))
    score_family = "mrs_open_v031"
    if mrs_score is None:
        mrs_score = _to_float(row.get("pseudo_mrs_after"))
        mrs_delta = _to_float(row.get("pseudo_delta_mrs"))
        score_family = "pseudo_mrs_v001"
    metrics = {
        "score_family": score_family,
        "pseudo_mrs_before": _to_float(row.get("pseudo_mrs_before")),
        "pseudo_mrs_after": _to_float(row.get("pseudo_mrs_after")),
        "pseudo_delta_mrs": _to_float(row.get("pseudo_delta_mrs")),
        "mrs_open_v031_before": _to_float(row.get("mrs_open_v031_before")),
        "mrs_open_v031_after": _to_float(row.get("mrs_open_v031_after")),
        "delta_mrs_open_v031": _to_float(row.get("delta_mrs_open_v031")),
        "mrs_open_flags": sorted(_flag_set(row.get("mrs_open_flags", ""))),
    }
    return mrs_score, mrs_delta, metrics


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
    rows = _load_jobs(cfg)
    if status:
        rows = [row for row in rows if row.get("status") == status]
    return sorted(rows, key=lambda row: (int(row.get("priority", 5)), row.get("created_at") or ""))


def get_operator_job(cfg: RuntimeConfig, job_id: str) -> Dict[str, Any]:
    for row in _load_jobs(cfg):
        if row.get("job_id") == job_id:
            return row
    raise KeyError(f"operator job not found: {job_id}")


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


def build_operator_detail_from_run(
    cfg: RuntimeConfig,
    job_id: str,
    run_id: str,
    run_dir: Optional[str | Path] = None,
    report_path: Optional[str | Path] = None,
    required_mrs_delta: float = 0.0,
) -> Dict[str, Any]:
    cfg = cfg.resolved()
    run_dir_path = Path(run_dir) if run_dir else cfg.output_root / run_id
    rows = _read_manifest(run_dir_path / "manifest.csv")
    generated_at = utc_now_iso()

    candidates: List[Dict[str, Any]] = []
    scores: List[Dict[str, Any]] = []
    gates: List[Dict[str, Any]] = []
    for row in rows:
        candidate_id = _stable_id(
            "CAND",
            job_id,
            run_id,
            row.get("task_id"),
            row.get("output_dir"),
        )
        lineage = {
            "run_id": run_id,
            "task_id": row.get("task_id"),
            "sample_id": row.get("sample_id"),
            "input_path": row.get("input_path"),
            "template_index": _to_int(row.get("template_index")),
            "return_code": _to_int(row.get("return_code")),
            "elapsed_seconds": _to_float(row.get("elapsed_seconds")),
        }
        candidates.append(
            CandidateVersion(
                candidate_id=candidate_id,
                job_id=job_id,
                output_path=row.get("output_dir", ""),
                preset=row.get("preset", ""),
                processing_chain=row.get("preset", ""),
                created_at=generated_at,
                lineage=lineage,
            ).to_dict()
        )
        mrs_score, mrs_delta, metrics = _score_from_manifest(row)
        flags = _flag_set(row.get("mrs_open_flags", ""))
        scores.append(
            ScoreResult(
                candidate_id=candidate_id,
                job_id=job_id,
                mrs_score=mrs_score,
                mrs_score_delta=mrs_delta,
                over_dark_triggered="over_dark" in flags,
                metrics=metrics,
                measured_at=generated_at,
            ).to_dict()
        )
        runtime_success = row.get("status") == "done" and row.get("return_code") in ("0", 0)
        gates.append(
            decide_candidate_gate(
                candidate_id=candidate_id,
                job_id=job_id,
                runtime_success=runtime_success,
                mrs_score_delta=mrs_delta,
                required_mrs_delta=required_mrs_delta,
                over_dark_triggered="over_dark" in flags,
            )
        )

    report_path_str = str(report_path) if report_path else ""
    if not report_path_str:
        daily_report = cfg.report_dir / f"daily_report_{run_id}.md"
        if daily_report.exists():
            report_path_str = str(daily_report)

    gate_counts: Dict[str, int] = {}
    for gate in gates:
        gate_counts[gate["decision"]] = gate_counts.get(gate["decision"], 0) + 1

    return {
        "job_id": job_id,
        "run_id": run_id,
        "run_dir": str(run_dir_path),
        "report_path": report_path_str,
        "generated_at": generated_at,
        "candidate_versions": candidates,
        "score_results": scores,
        "gate_decisions": gates,
        "summary": {
            "candidate_count": len(candidates),
            "gate_counts": gate_counts,
            "required_mrs_delta": required_mrs_delta,
        },
    }


def attach_run_report_to_job(
    cfg: RuntimeConfig,
    job_id: str,
    run_id: str,
    run_dir: Optional[str | Path] = None,
    report_path: Optional[str | Path] = None,
    required_mrs_delta: float = 0.0,
) -> Dict[str, Any]:
    get_operator_job(cfg, job_id)
    detail = build_operator_detail_from_run(
        cfg,
        job_id=job_id,
        run_id=run_id,
        run_dir=run_dir,
        report_path=report_path,
        required_mrs_delta=required_mrs_delta,
    )
    detail_path = _operator_detail_path(cfg, job_id)
    atomic_write_json(detail_path, detail)
    status = "gate_review"
    if detail["summary"]["gate_counts"].get("reject"):
        status = "failed"
    elif detail["summary"]["gate_counts"].get("reprocess"):
        status = "reprocess"
    _update_job(
        cfg,
        job_id,
        {
            "status": status,
            "current_step": "gate_review",
            "run_id": run_id,
            "run_dir": detail["run_dir"],
            "report_path": detail["report_path"],
            "detail_path": str(detail_path),
            "last_error": None,
        },
    )
    return detail


def get_operator_job_detail(cfg: RuntimeConfig, job_id: str) -> Dict[str, Any]:
    job = get_operator_job(cfg, job_id)
    detail_path = job.get("detail_path")
    detail: Dict[str, Any] = {}
    if detail_path:
        detail = read_json(Path(detail_path), default={}) or {}
    return {
        "job": job,
        "detail": detail,
    }
