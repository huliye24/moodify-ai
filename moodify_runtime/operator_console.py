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
    run_started_at: Optional[str] = None
    run_finished_at: Optional[str] = None
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


def _load_genre_thresholds(genre: str = "") -> Dict[str, Any]:
    """Load per-genre gate thresholds from configs/mrs_thresholds.yaml.

    Returns a dict with keys: required_mrs_delta, transient_threshold,
    loudness_penalty_threshold, over_dark_policy.
    Falls back to defaults when genre is unspecified or unknown.
    """
    import yaml as _yaml

    defaults = {
        "required_mrs_delta": 0.0,
        "transient_threshold": 1.0,
        "loudness_penalty_threshold": 1.0,
        "over_dark_policy": "binary",
    }
    try:
        config_path = Path(__file__).resolve().parent.parent / "configs" / "mrs_thresholds.yaml"
        with open(config_path, encoding="utf-8") as fh:
            cfg = _yaml.safe_load(fh) or {}
    except Exception:
        return defaults

    defaults.update(cfg.get("defaults", {}))
    genre_cfg = cfg.get("genres", {}).get(genre, {}) if genre else {}

    result = dict(defaults)
    for key in ("required_mrs_delta", "transient_threshold",
                "loudness_penalty_threshold", "over_dark_policy"):
        if key in genre_cfg:
            result[key] = genre_cfg[key]
    return result


def _over_dark_decision(over_dark_triggered: bool, over_dark_level: str) -> tuple[Optional[str], Optional[str]]:
    """Over-dark gate: graduated level overrides the legacy binary flag.

    Returns (decision_override, reason); both None when no over-dark condition.
    """
    if over_dark_level == "severe":
        return "reject", "over_dark_severe"
    if over_dark_level == "mild":
        return "reprocess", "over_dark_mild"
    if over_dark_triggered:
        return "reprocess", "over_dark_triggered"
    return None, None


def decide_candidate_gate(
    candidate_id: str,
    job_id: str,
    runtime_success: bool,
    mrs_score_delta: Optional[float] = None,
    required_mrs_delta: float = 0.0,
    over_dark_triggered: bool = False,
    over_dark_level: str = "",
    transient_damage: Optional[float] = None,
    transient_threshold: float = 1.0,
    loudness_penalty: Optional[float] = None,
    loudness_penalty_threshold: float = 1.0,
    genre: str = "",
) -> Dict[str, Any]:
    reasons: List[str] = []
    decision = "approve"

    # ── Genre-specific threshold override ──
    if genre:
        t = _load_genre_thresholds(genre)
        # Only override if caller didn't explicitly pass a non-default value
        if required_mrs_delta == 0.0:
            required_mrs_delta = t["required_mrs_delta"]
        if transient_threshold == 1.0:
            transient_threshold = t["transient_threshold"]
        if loudness_penalty_threshold == 1.0:
            loudness_penalty_threshold = t["loudness_penalty_threshold"]

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

    # ── Over-dark: graduated level overrides binary flag ──
    over_dark_decision, over_dark_reason = _over_dark_decision(
        over_dark_triggered, over_dark_level
    )
    if over_dark_reason:
        reasons.append(over_dark_reason)
        if over_dark_decision == "reject":
            decision = "reject"
        elif over_dark_decision == "reprocess" and decision == "approve":
            # Legacy binary flag: conservatively reprocess
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
    genre: str = "",
) -> Dict[str, Any]:
    cfg = cfg.resolved()
    run_dir_path = Path(run_dir) if run_dir else cfg.output_root / run_id
    rows = _read_manifest(run_dir_path / "manifest.csv")
    generated_at = utc_now_iso()

    # ── Genre-specific threshold override ──
    if genre:
        t = _load_genre_thresholds(genre)
        if required_mrs_delta == 0.0:
            required_mrs_delta = t["required_mrs_delta"]

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
                genre=genre,
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
    genre: str = "",
) -> Dict[str, Any]:
    get_operator_job(cfg, job_id)
    detail = build_operator_detail_from_run(
        cfg,
        job_id=job_id,
        run_id=run_id,
        run_dir=run_dir,
        report_path=report_path,
        required_mrs_delta=required_mrs_delta,
        genre=genre,
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


# ── Delivery Records ──────────────────────────────────────────────


def _operator_deliveries_path(cfg: RuntimeConfig) -> Path:
    cfg = cfg.resolved()
    return cfg.operator_deliveries_path


def create_delivery_record(
    cfg: RuntimeConfig,
    job_id: str,
    candidate_id: str,
    operator_decision: str = "approved",
    notes: str = "",
    override: bool = False,
    human_approved: bool = False,
    approved_by: str = "",
) -> Dict[str, Any]:
    """Create a delivery record and update the job to 'delivered'.

    The caller must provide a valid job_id and a candidate_id that exists in
    the job's attached detail.  Delivery cannot silently select a missing
    candidate or a missing report path.  Reprocess/reject candidates require
    an explicit override flag and reason.

    Returns the delivery record dict.
    """
    job = get_operator_job(cfg, job_id)
    detail_dir = _operator_detail_dir(cfg)
    detail_path = detail_dir / f"{job_id}.json"
    detail: Dict[str, Any] = {}
    if detail_path.exists():
        detail = read_json(detail_path, default={}) or {}

    # Validate candidate exists in attached detail
    candidates = detail.get("candidate_versions", [])
    matched = [c for c in candidates if c.get("candidate_id") == candidate_id]
    if not matched:
        raise ValueError(
            f"candidate_id={candidate_id!r} not found in job detail; "
            f"cannot deliver a missing candidate"
        )
    candidate = matched[0]

    # Validate report path
    report_path = detail.get("report_path", "")
    if not report_path or not Path(report_path).exists():
        raise ValueError(
            f"report_path={report_path!r} not found; "
            f"cannot deliver without a report"
        )

    # Validate gate decision allows delivery
    gate_decisions = detail.get("gate_decisions", [])
    gate = next((g for g in gate_decisions if g.get("candidate_id") == candidate_id), None)
    gate_decision = gate.get("decision", "unknown") if gate else "unknown"
    if gate_decision in ("reject", "reprocess") and not override:
        raise ValueError(
            f"candidate gate decision is {gate_decision!r}; "
            f"set override=True with a reason in notes to force delivery"
        )

    from .hardening_gates import mrs_can_release

    human_allowed, human_reason = mrs_can_release(human_approved=human_approved)
    if not human_allowed:
        raise ValueError(human_reason)
    if not approved_by.strip():
        raise ValueError("approved_by is required for human listening approval")
    if not job.get("rights_manifest") or not job.get("rights_asset_id"):
        raise ValueError("job has no verified rights evidence; delivery is blocked")

    # Determine archive path
    archive_path = detail.get("report_path", "")
    if archive_path:
        archive_path = str(Path(archive_path).parent / "deliveries" / f"{job_id}_{candidate_id}")

    final_audio_path = candidate.get("output_path", "")

    record = DeliveryRecord(
        delivery_id=_new_id("DLV"),
        job_id=job_id,
        candidate_id=candidate_id,
        final_audio_path=final_audio_path,
        report_path=detail.get("report_path", ""),
        archive_path=archive_path,
        operator_decision=operator_decision,
        notes=notes,
    )

    record_payload = record.to_dict()
    record_payload.update({
        "human_approved": True,
        "approved_by": approved_by.strip(),
        "rights_manifest": job["rights_manifest"],
        "rights_asset_id": job["rights_asset_id"],
    })
    append_jsonl(_operator_deliveries_path(cfg), record_payload)

    # Update job status
    _update_job(
        cfg,
        job_id,
        {
            "status": "delivered",
            "current_step": "delivered",
            "delivery_path": str(_operator_deliveries_path(cfg)),
        },
    )

    return record_payload


def get_delivery_record(
    cfg: RuntimeConfig, job_id: str
) -> Dict[str, Any]:
    """Return the most recent delivery record for a job, or empty dict."""
    rows = read_jsonl(_operator_deliveries_path(cfg))
    for row in reversed(rows):
        if row.get("job_id") == job_id:
            return row
    return {}


def list_delivery_records(cfg: RuntimeConfig) -> List[Dict[str, Any]]:
    """Return all delivery records sorted by delivered_at."""
    rows = read_jsonl(_operator_deliveries_path(cfg))
    return sorted(rows, key=lambda r: r.get("delivered_at", ""), reverse=True)


# ── MHP-032: Job-to-Runtime Adapter ────────────────────────────────


DEPTH_PRESET_MAP: Dict[str, List[str]] = {
    "quick_scan": ["clean_master"],
    "standard_process": ["warm_vocal", "clean_master", "wide_space"],
    "deep_process": ["warm_vocal", "clean_master", "wide_space"],
    "studio_process": ["warm_vocal", "clean_master", "wide_space"],
}


def plan_operator_runtime(
    cfg: RuntimeConfig,
    job_id: str,
) -> Dict[str, Any]:
    """Create runtime queue tasks from an Operator Job.

    Reads the job's source_audio and processing_depth, registers the audio
    (or discovers files under the directory), then creates queue tasks
    matching the depth's preset strategy.

    Returns a summary of planned tasks.
    """
    from .registry import register_inputs
    from .queue import plan_queue

    cfg = cfg.resolved()
    job = get_operator_job(cfg, job_id)
    depth = job.get("processing_depth", "quick_scan")
    if depth not in DEPTH_PRESET_MAP:
        raise ValueError(
            f"unknown processing_depth={depth!r}; "
            f"expected one of {sorted(DEPTH_PRESET_MAP)}"
        )

    source = Path(job.get("source_audio", ""))
    if not source.exists():
        raise FileNotFoundError(f"source_audio not found: {source}")

    priority = int(job.get("priority", 5))
    project_label = job.get("project_label", "") or "operator_job"

    # Temporarily redirect input_dirs to the source audio
    orig_input_dirs = list(cfg.input_dirs)
    orig_recurse = cfg.recurse

    try:
        if source.is_dir():
            cfg.input_dirs = [source]
            cfg.recurse = True
        else:
            # Single file → place it in a temp input dir
            cfg.input_dirs = [source.parent]
            cfg.recurse = False

        # Register inputs (idempotent)
        reg_result = register_inputs(cfg, source="operator_job", notes=f"job_id={job_id}")

        # Plan queue tasks with depth-appropriate presets
        presets = DEPTH_PRESET_MAP[depth]
        plan_result = plan_queue(
            cfg,
            presets=presets,
            priority=priority,
            reason=f"operator_job:{job_id}:{project_label}",
        )
    finally:
        cfg.input_dirs = orig_input_dirs
        cfg.recurse = orig_recurse

    _update_job(
        cfg,
        job_id,
        {
            "status": "waiting",
            "current_step": "runtime_planned",
        },
    )

    return {
        "job_id": job_id,
        "registry": reg_result,
        "queue": plan_result,
    }


def authorize_operator_job_source(
    cfg: RuntimeConfig,
    job_id: str,
    rights_manifest: str | Path,
    rights_asset_id: str,
) -> Dict[str, Any]:
    """Validate and persist rights evidence for one exact Operator Job source."""
    from .hardening_gates import authorize_audio_source

    job = get_operator_job(cfg, job_id)
    source_path = Path(job["source_audio"])
    if not source_path.is_absolute():
        source_path = cfg.resolved().project_root / source_path
    allowed, reason = authorize_audio_source(
        rights_manifest, rights_asset_id, source_path
    )
    if not allowed:
        raise ValueError(reason)
    evidence = {
        "rights_manifest": str(Path(rights_manifest)),
        "rights_asset_id": rights_asset_id,
        "rights_verified_at": utc_now_iso(),
    }
    _update_job(cfg, job_id, evidence)
    return {"job_id": job_id, **evidence}


def _fail_operator_job(
    cfg: RuntimeConfig,
    job_id: str,
    error: str,
    step: str,
    mark_started_at: bool = False,
) -> None:
    """Record a failed job state. mark_started_at keeps pre-flight failures
    timestamped with run_started_at, matching historical job records."""
    now = utc_now_iso()
    updates: Dict[str, Any] = {
        "status": "failed",
        "current_step": step,
        "run_finished_at": now,
        "last_error": error,
    }
    if mark_started_at:
        updates["run_started_at"] = now
    _update_job(cfg, job_id, updates)


def _preflight_operator_job(
    cfg: RuntimeConfig,
    job_id: str,
    dry_run: bool,
    rights_manifest: str | Path | None,
    rights_asset_id: str,
    job_reason_prefix: str,
) -> Optional[Dict[str, Any]]:
    """Pre-flight gates: queue has pending tasks, explicit rights evidence.

    Returns a failure response dict, or None when all gates pass.
    """
    from .queue import load_queue
    from .runner import select_pending_tasks

    if dry_run:
        return None

    queue_rows = load_queue(cfg)
    pending = select_pending_tasks(queue_rows)
    job_pending = [t for t in pending if str(t.get("reason", "")).startswith(job_reason_prefix)]
    if not job_pending:
        error = f"No pending tasks for this job in queue. Run plan-runtime first."
        _fail_operator_job(cfg, job_id, error, "runtime_failed", mark_started_at=True)
        return {"job_id": job_id, "status": "failed", "error": error, "dry_run": False}

    if not rights_manifest or not rights_asset_id:
        error = "Explicit rights_manifest and rights_asset_id are required for live processing."
        _fail_operator_job(cfg, job_id, error, "rights_gate_blocked", mark_started_at=True)
        return {"job_id": job_id, "status": "failed", "error": error, "dry_run": False}

    try:
        authorize_operator_job_source(cfg, job_id, rights_manifest, rights_asset_id)
    except ValueError as exc:
        error = f"Rights gate blocked processing: {exc}"
        _fail_operator_job(cfg, job_id, error, "rights_gate_blocked", mark_started_at=True)
        return {"job_id": job_id, "status": "failed", "error": error, "dry_run": False}

    return None


def _handle_operator_run_outcome(
    cfg: RuntimeConfig,
    job_id: str,
    result: Dict[str, Any],
    dry_run: bool,
) -> Dict[str, Any]:
    """Post-run handling: dry-run plan return, fatal error, manifest
    verification, and evidence attach-back."""
    if dry_run:
        _update_job(
            cfg, job_id,
            {"status": "waiting", "current_step": "intake", "run_finished_at": utc_now_iso()},
        )
        return {
            "job_id": job_id,
            "status": "dry_run_complete",
            "dry_run": True,
            "run": result,
        }

    run_id = result.get("run_id", "")
    if result.get("fatal_error"):
        _fail_operator_job(cfg, job_id, result.get("fatal_error", "")[-1000:], "runtime_failed")
        return {
            "job_id": job_id,
            "status": "failed",
            "error": result.get("fatal_error"),
            "run": result,
        }

    # Verify manifest exists after a real run
    run_dir = cfg.output_root / run_id
    manifest_path = run_dir / "manifest.csv"
    if not manifest_path.exists():
        error = f"manifest.csv not found at {manifest_path}"
        _fail_operator_job(cfg, job_id, error, "runtime_failed")
        return {"job_id": job_id, "status": "failed", "error": error, "run": result}

    # Attach run evidence back to the job
    detail = attach_run_report_to_job(cfg, job_id=job_id, run_id=run_id)

    _update_job(cfg, job_id, {"run_finished_at": utc_now_iso()})

    return {
        "job_id": job_id,
        "status": "completed",
        "run_id": run_id,
        "detail_summary": detail.get("summary", {}),
    }


def run_operator_job(
    cfg: RuntimeConfig,
    job_id: str,
    dry_run: bool = False,
    rights_manifest: str | Path | None = None,
    rights_asset_id: str = "",
) -> Dict[str, Any]:
    """Execute the runtime for an Operator Job's queued tasks.

    Updates job status to 'running' before execution, then attaches the
    run evidence back to the job via attach_run_report_to_job.

    On failure the job status is set to 'failed' and last_error is recorded.

    Guardrails:
    - Verifies queue has pending tasks before running (real mode only).
    - Verifies manifest.csv exists after a real run.
    - Records run_started_at / run_finished_at timestamps on the job.
    """
    from .runner import run_daily

    cfg = cfg.resolved()
    get_operator_job(cfg, job_id)
    job_reason_prefix = f"operator_job:{job_id}:"

    # Pre-flight: queue + rights gates (real mode only)
    preflight = _preflight_operator_job(
        cfg, job_id, dry_run, rights_manifest, rights_asset_id, job_reason_prefix
    )
    if preflight:
        return preflight

    _update_job(
        cfg,
        job_id,
        {
            "status": "running",
            "current_step": "runtime_executing",
            "run_started_at": utc_now_iso(),
        },
    )

    try:
        result = run_daily(
            cfg,
            dry_run=dry_run,
            rights_manifest=str(rights_manifest) if rights_manifest else None,
            rights_asset_id=rights_asset_id,
            task_filter=lambda t: str(t.get("reason", "")).startswith(job_reason_prefix),
        )
    except Exception as exc:
        _fail_operator_job(cfg, job_id, f"{type(exc).__name__}: {exc}", "runtime_failed")
        return {
            "job_id": job_id,
            "status": "failed",
            "error": str(exc),
            "dry_run": dry_run,
        }

    return _handle_operator_run_outcome(cfg, job_id, result, dry_run)


def show_operator_runtime_plan(
    cfg: RuntimeConfig,
    job_id: str,
) -> Dict[str, Any]:
    """Show what commands would be executed for a job without running them.

    Returns the planned tasks and the rendered command lines for inspection.
    """
    from .queue import load_queue
    from .runner import select_pending_tasks
    from .utils import quote_cmd, render_template_to_argv

    cfg = cfg.resolved()
    plan = plan_operator_runtime(cfg, job_id)

    tasks = load_queue(cfg)
    pending = select_pending_tasks(tasks)

    commands: List[Dict[str, Any]] = []
    for task in pending:
        context = {
            "python": cfg.python,
            "project_root": cfg.project_root,
            "input": task["input_path"],
            "output_dir": cfg.output_root / "planned" / task["task_id"],
            "preset": task["preset"],
            "sample_id": task["sample_id"],
            "task_id": task["task_id"],
            "run_id": "planned",
        }
        for i, template in enumerate(cfg.command_templates):
            try:
                argv = render_template_to_argv(template, context)
                commands.append({
                    "task_id": task["task_id"],
                    "template_index": i,
                    "command": quote_cmd(argv),
                })
            except Exception:
                commands.append({
                    "task_id": task["task_id"],
                    "template_index": i,
                    "command": f"<invalid template: {template!r}>",
                })

    return {
        "job_id": job_id,
        "plan": plan,
        "planned_tasks": len(pending),
        "commands": commands,
    }


# ── MHP-033: Operator Report Bundle ─────────────────────────────────


def _operator_report_dir(cfg: RuntimeConfig, job_id: str) -> Path:
    cfg = cfg.resolved()
    return cfg.operator_report_dir / job_id


def _load_job_detail(job: Dict[str, Any]) -> Dict[str, Any]:
    """Load job detail JSON when present; missing detail yields {}."""
    dp = job.get("detail_path")
    detail_path = Path(dp) if dp else None
    if not (detail_path and detail_path.exists()):
        return {}
    return read_json(detail_path, default={}) or {}


def _build_bundle_summary(job: Dict[str, Any], detail_summary: Dict[str, Any],
                          job_id: str) -> Dict[str, Any]:
    """Machine-readable bundle summary (identical schema to prior output)."""
    return {
        "job_id": job_id,
        "generated_at": utc_now_iso(),
        "processing_depth": job.get("processing_depth"),
        "project_label": job.get("project_label"),
        "candidate_count": detail_summary.get("candidate_count", 0),
        "gate_counts": detail_summary.get("gate_counts", {}),
        "required_mrs_delta": detail_summary.get("required_mrs_delta", 0.0),
    }


def _write_summary_md(report_dir: Path, job_id: str, job: Dict[str, Any],
                      bundle_summary: Dict[str, Any], gates: List[Dict[str, Any]],
                      scores: List[Dict[str, Any]], detail_summary: Dict[str, Any]) -> None:
    """Human-readable summary.md (byte-identical layout to prior output)."""
    gate_counts = detail_summary.get("gate_counts", {})
    md_parts = [
        f"# Operator Report — {job_id}",
        "",
        f"**Project:** {job.get('project_label', '-')}",
        f"**Processing Depth:** {job.get('processing_depth', '-')}",
        f"**Generated:** {bundle_summary['generated_at']}",
        "",
        "## Candidate Summary",
        "",
        f"- Total candidates: {detail_summary.get('candidate_count', 0)}",
        f"- Approved: {gate_counts.get('approve', 0)}",
        f"- Reprocess: {gate_counts.get('reprocess', 0)}",
        f"- Rejected: {gate_counts.get('reject', 0)}",
        f"- Required MRS Δ: {detail_summary.get('required_mrs_delta', 0.0)}",
        "",
        "## Gate Decisions",
        "",
    ]
    for g in gates:
        md_parts.append(f"- **{g.get('candidate_id', '?')}**: {g.get('decision', '?')} — {', '.join(g.get('reasons', []))}")

    md_parts += [
        "",
        "## Scores",
        "",
    ]
    for s in scores:
        md_parts.append(
            f"- **{s.get('candidate_id', '?')}**: "
            f"MRS={s.get('mrs_score', 'N/A')} "
            f"Δ={s.get('mrs_score_delta', 'N/A')} "
            f"over_dark={s.get('over_dark_triggered', False)}"
        )

    md_parts += [
        "",
        "## Delivery",
        "",
        "Not yet delivered." if job.get("status") != "delivered" else f"Delivered at {job.get('updated_at', '-')}",
        "",
        "---",
        "",
        "> Fast code can run today. Living code can evolve tomorrow.",
        "",
    ]
    (report_dir / "summary.md").write_text("\n".join(md_parts), encoding="utf-8")


def _write_delivery_md(cfg: RuntimeConfig, report_dir: Path, job: Dict[str, Any],
                       job_id: str) -> None:
    """delivery.md — delivery record when delivered, placeholder otherwise."""
    delivery_path = report_dir / "delivery.md"
    if job.get("status") != "delivered":
        delivery_path.write_text("# Delivery\n\nNot yet delivered.\n", encoding="utf-8")
        return
    delivery_record = get_delivery_record(cfg, job_id)
    dl_md = [
        "# Delivery Record",
        "",
        f"**Delivery ID:** {delivery_record.get('delivery_id', '-')}",
        f"**Candidate:** {delivery_record.get('candidate_id', '-')}",
        f"**Operator Decision:** {delivery_record.get('operator_decision', '-')}",
        f"**Delivered At:** {delivery_record.get('delivered_at', '-')}",
        f"**Notes:** {delivery_record.get('notes', '-')}",
        f"**Final Audio:** {delivery_record.get('final_audio_path', '-')}",
        f"**Archive Path:** {delivery_record.get('archive_path', '-')}",
        "",
    ]
    delivery_path.write_text("\n".join(dl_md), encoding="utf-8")


def _write_manifest_csv(report_dir: Path, candidates: List[Dict[str, Any]],
                        scores: List[Dict[str, Any]], gates: List[Dict[str, Any]]) -> None:
    """manifest.csv — flat summary of all candidates."""
    import csv

    manifest_fields = [
        "candidate_id", "preset", "output_path", "mrs_score",
        "mrs_score_delta", "over_dark", "gate_decision",
    ]
    manifest_path = report_dir / "manifest.csv"
    with manifest_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=manifest_fields)
        writer.writeheader()
        for i, c in enumerate(candidates):
            s = scores[i] if i < len(scores) else {}
            g = gates[i] if i < len(gates) else {}
            writer.writerow({
                "candidate_id": c.get("candidate_id", ""),
                "preset": c.get("preset", ""),
                "output_path": c.get("output_path", ""),
                "mrs_score": s.get("mrs_score", ""),
                "mrs_score_delta": s.get("mrs_score_delta", ""),
                "over_dark": str(s.get("over_dark_triggered", False)),
                "gate_decision": g.get("decision", ""),
            })


def build_operator_report_bundle(
    cfg: RuntimeConfig,
    job_id: str,
) -> Dict[str, Any]:
    """Build a standard Operator Report Bundle for a completed job.

    Writes the following files under reports/operator_runs/{job_id}/:

        summary.md          — human-readable summary
        summary.json        — machine-readable summary
        candidate_versions.jsonl
        score_results.jsonl
        gate_decisions.jsonl
        delivery.md         — placeholder if not yet delivered
        manifest.csv        — flat summary of all candidates

    Returns a dict with report_path and file listing.
    """
    cfg = cfg.resolved()
    job = get_operator_job(cfg, job_id)
    detail = _load_job_detail(job)

    report_dir = _operator_report_dir(cfg, job_id)
    report_dir.mkdir(parents=True, exist_ok=True)

    candidates = detail.get("candidate_versions", [])
    scores = detail.get("score_results", [])
    gates = detail.get("gate_decisions", [])
    detail_summary = detail.get("summary", {})

    # ── candidate_versions.jsonl / score_results.jsonl / gate_decisions.jsonl ──
    atomic_write_jsonl(report_dir / "candidate_versions.jsonl", candidates)
    atomic_write_jsonl(report_dir / "score_results.jsonl", scores)
    atomic_write_jsonl(report_dir / "gate_decisions.jsonl", gates)

    # ── summary.json + summary.md ──
    bundle_summary = _build_bundle_summary(job, detail_summary, job_id)
    atomic_write_json(report_dir / "summary.json", bundle_summary)
    _write_summary_md(report_dir, job_id, job, bundle_summary, gates, scores, detail_summary)

    # ── delivery.md ──
    _write_delivery_md(cfg, report_dir, job, job_id)

    # ── manifest.csv ──
    _write_manifest_csv(report_dir, candidates, scores, gates)

    # Update job
    _update_job(cfg, job_id, {"report_path": str(report_dir)})

    files_written = sorted(str(p.relative_to(report_dir)) for p in report_dir.glob("*") if p.is_file())

    return {
        "job_id": job_id,
        "report_path": str(report_dir),
        "files": files_written,
        "summary": bundle_summary,
    }


# ═══════════════════════════════════════════════════════════════════════
# Production: Structured Logging
# ═══════════════════════════════════════════════════════════════════════


def _op_log(action: str, job_id: str = "", **kwargs) -> dict:
    """Structured log entry for operator console operations.

    All key functions call this at entry/exit so the operator
    can reconstruct the processing timeline from logs.
    """
    entry = {
        "timestamp": utc_now_iso(),
        "action": action,
    }
    if job_id:
        entry["job_id"] = job_id
    entry.update(kwargs)
    return entry


# ═══════════════════════════════════════════════════════════════════════
# Production: Data Compaction
# ═══════════════════════════════════════════════════════════════════════


def compact_operator_jobs(cfg: RuntimeConfig, keep_last_n: int = 100) -> dict:
    """Remove duplicate job records and prune old entries.

    Keeps the most recent `keep_last_n` jobs. Deduplicates by job_id,
    keeping the latest entry. Returns compaction statistics.
    """
    jobs_path = _operator_jobs_path(cfg)
    if not jobs_path.exists():
        return {"compacted": 0, "kept": 0, "duplicates_removed": 0, "old_pruned": 0}

    jobs = read_jsonl(jobs_path)
    original_count = len(jobs)

    # Deduplicate: keep last occurrence of each job_id
    seen = {}
    for j in jobs:
        seen[j.get("job_id", "")] = j
    deduped = list(seen.values())

    # Sort by updated_at descending if available, keep last N
    deduped.sort(key=lambda j: j.get("updated_at", j.get("created_at", "")), reverse=True)
    kept = deduped[:keep_last_n]

    atomic_write_jsonl(jobs_path, kept)

    return {
        "compacted": original_count - len(kept),
        "kept": len(kept),
        "duplicates_removed": original_count - len(deduped),
        "old_pruned": len(deduped) - len(kept),
    }


# ═══════════════════════════════════════════════════════════════════════
# Production: Health Check Helpers
# ═══════════════════════════════════════════════════════════════════════


def check_storage_health(cfg: RuntimeConfig) -> dict:
    """Verify all data directories exist and are writable.

    Returns a health dict suitable for the /studio-os/status endpoint.
    """
    issues = []
    checks = {}

    dirs = {
        "output_root": cfg.output_root,
        "report_dir": cfg.report_dir,
        "operator_detail_dir": cfg.operator_detail_dir,
        "studio_data_dir": cfg.studio_data_dir,
        "scheduler_data_dir": cfg.scheduler_data_dir,
        "calibration_data_dir": cfg.calibration_data_dir,
        "craft_memory_dir": cfg.craft_memory_dir,
    }

    import os as _os

    for name, d in dirs.items():
        path = Path(d) if not isinstance(d, Path) else d
        path = path if path.is_absolute() else cfg.project_root / path
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"{name}: cannot create {path}: {e}")
            checks[name] = {"path": str(path), "exists": path.exists(), "writable": False}
            continue

        writable = _os.access(str(path), _os.W_OK)
        checks[name] = {
            "path": str(path),
            "exists": path.exists(),
            "writable": writable,
        }
        if not writable:
            issues.append(f"{name}: not writable: {path}")

    return {
        "storage": {
            "healthy": len(issues) == 0,
            "issues": issues,
            "directories": checks,
        }
    }
