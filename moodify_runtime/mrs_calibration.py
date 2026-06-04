"""MHP-039: MRS Calibration Lab — quality standard and calibration workflow.

Durable models: CalibrationSampleSet, CalibrationReview, GateAudit, ThresholdProposal
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import RuntimeConfig
from .utils import append_jsonl, read_jsonl, atomic_write_json, utc_now_iso


@dataclass(frozen=True)
class CalibrationSampleSet:
    set_id: str
    name: str
    description: str = ""
    sample_count: int = 0
    sample_ids: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


@dataclass(frozen=True)
class CalibrationReview:
    review_id: str
    set_id: str
    candidate_id: str
    human_decision: str = ""          # "better", "worse", "no_change", "unsure"
    gate_decision: str = ""           # what the automated gate said
    notes: str = ""
    reviewer: str = ""
    reviewed_at: str = field(default_factory=utc_now_iso)
    matched: bool = True              # does human agree with gate?

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


@dataclass(frozen=True)
class GateAudit:
    audit_id: str
    set_id: str
    total_reviews: int = 0
    false_positives: int = 0   # gate rejected, human says better
    false_negatives: int = 0   # gate approved, human says worse
    accuracy: float = 0.0
    generated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ThresholdProposal:
    proposal_id: str
    parameter: str            # e.g. "mrs_score_delta", "transient_threshold", "loudness_penalty"
    current_value: float
    proposed_value: float
    justification: str = ""
    status: str = "proposed"  # proposed, accepted, rejected
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ── Helpers ────────────────────────────────────────────────────────


def _sid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12].upper()}"


def _cal_path(cfg: RuntimeConfig, entity: str) -> Path:
    cfg = cfg.resolved()
    return cfg.calibration_data_dir / f"{entity}.jsonl"


# ── Sample Sets ─────────────────────────────────────────────────────


def create_calibration_sample_set(
    cfg: RuntimeConfig, name: str, description: str = "", sample_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    s = CalibrationSampleSet(
        set_id=_sid("CALSET"), name=name, description=description,
        sample_count=len(sample_ids or []), sample_ids=sample_ids or [],
    )
    append_jsonl(_cal_path(cfg, "sample_sets"), s.to_dict())
    return s.to_dict()


# ── Reviews ─────────────────────────────────────────────────────────


def submit_calibration_review(
    cfg: RuntimeConfig,
    set_id: str,
    candidate_id: str,
    human_decision: str,
    gate_decision: str,
    notes: str = "",
    reviewer: str = "operator",
) -> Dict[str, Any]:
    if human_decision not in ("better", "worse", "no_change", "unsure"):
        raise ValueError("human_decision must be one of: better, worse, no_change, unsure")
    matched = (
        (human_decision == "better" and gate_decision == "approve")
        or (human_decision == "worse" and gate_decision in ("reject", "reprocess"))
    )
    r = CalibrationReview(
        review_id=_sid("CALREV"), set_id=set_id, candidate_id=candidate_id,
        human_decision=human_decision, gate_decision=gate_decision,
        notes=notes, reviewer=reviewer, matched=matched,
    )
    append_jsonl(_cal_path(cfg, "reviews"), r.to_dict())
    return r.to_dict()


# ── Gate Audit ──────────────────────────────────────────────────────


def run_gate_audit(cfg: RuntimeConfig, set_id: str) -> Dict[str, Any]:
    """Compare gate decisions against human review for a sample set."""
    reviews = [
        r for r in read_jsonl(_cal_path(cfg, "reviews"))
        if r.get("set_id") == set_id
    ]
    total = len(reviews)
    fp = sum(1 for r in reviews if r.get("human_decision") == "better" and r.get("gate_decision") in ("reject", "reprocess"))
    fn = sum(1 for r in reviews if r.get("human_decision") == "worse" and r.get("gate_decision") == "approve")
    matched = sum(1 for r in reviews if r.get("matched"))

    accuracy = matched / total if total > 0 else 0.0

    audit = GateAudit(
        audit_id=_sid("GAUDIT"), set_id=set_id, total_reviews=total,
        false_positives=fp, false_negatives=fn, accuracy=round(accuracy, 4),
    )
    append_jsonl(_cal_path(cfg, "audits"), audit.to_dict())

    # Write report
    report_dir = cfg.calibration_data_dir / "reports" / audit.audit_id
    report_dir.mkdir(parents=True, exist_ok=True)
    md = [
        f"# Gate Audit Report — {audit.audit_id}",
        f"**Sample Set:** {set_id}",
        f"**Generated:** {audit.generated_at}",
        "",
        f"- Total reviews: {total}",
        f"- False positives (gate rejected, human says better): {fp}",
        f"- False negatives (gate approved, human says worse): {fn}",
        f"- Accuracy: {audit.accuracy:.1%}",
        "",
    ]
    (report_dir / "summary.md").write_text("\n".join(md), encoding="utf-8")
    atomic_write_json(report_dir / "summary.json", audit.to_dict())

    return audit.to_dict()


# ── Threshold Proposals ─────────────────────────────────────────────


def propose_threshold(
    cfg: RuntimeConfig, parameter: str, current_value: float, proposed_value: float, justification: str = ""
) -> Dict[str, Any]:
    t = ThresholdProposal(
        proposal_id=_sid("THR"), parameter=parameter,
        current_value=current_value, proposed_value=proposed_value,
        justification=justification,
    )
    append_jsonl(_cal_path(cfg, "thresholds"), t.to_dict())
    return t.to_dict()


def list_calibration_reviews(cfg: RuntimeConfig, set_id: Optional[str] = None) -> List[Dict[str, Any]]:
    rows = read_jsonl(_cal_path(cfg, "reviews"))
    if set_id:
        rows = [r for r in rows if r.get("set_id") == set_id]
    return rows
