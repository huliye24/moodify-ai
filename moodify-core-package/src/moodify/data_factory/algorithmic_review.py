"""Deterministic algorithmic review replacing human blind ranking.

Moodify is the ear of AI (decision 2026-08-11): SOURCE/A/B/C are ranked by a
frozen scoring function over the comparison judgments already produced by
moodify.auditory.judgment. No human listening is required anywhere in the
loop. The formula is versioned; changing it invalidates prior reviews.
"""

from __future__ import annotations

import json
from datetime import timezone
from pathlib import Path

from moodify.contracts.base import utc_now

from .human_review import ALLOWED_ITEMS

ALGORITHMIC_REVIEWER_ID = "algorithm:MFY-ALGORITHMIC-REVIEW-001"
REVIEW_FORMULA_VERSION = "MFY-ALGO-REVIEW-FORMULA-001"

# Scoring weights frozen in REVIEW_FORMULA_VERSION.
GOAL_MET_POINTS = 1.0
BLOCKING_GUARDRAIL_PENALTY = 100.0
WARNING_RISK_PENALTY = 0.5

# Tie-break order keeps the case structure stable: baseline first, then A/B/C.
_TIE_BREAK = {item: idx for idx, item in enumerate(ALLOWED_ITEMS)}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _candidate_score(comparison_report: dict) -> tuple[float, dict]:
    """Score one candidate from its frozen comparison judgment.

    Returns (score, detail) where detail is the machine-readable breakdown
    written next to the review record.
    """
    judgment = comparison_report.get("judgment") or {}
    goals_met = list(judgment.get("goals_met", []))
    guardrail_failures = list(judgment.get("guardrail_failures", []))
    risk_flags = list(judgment.get("risk_flags", []))
    warnings = [f for f in risk_flags if f.get("severity") == "WARNING"]

    score = GOAL_MET_POINTS * len(goals_met)
    score -= BLOCKING_GUARDRAIL_PENALTY * len(guardrail_failures)
    score -= WARNING_RISK_PENALTY * len(warnings)

    detail = {
        "technical_assessment": judgment.get("technical_assessment"),
        "workflow_decision": judgment.get("workflow_decision"),
        "goals_met": goals_met,
        "guardrail_failures": guardrail_failures,
        "warning_count": len(warnings),
        "score": round(score, 4),
    }
    return score, detail


def generate_algorithmic_review(case_dir: Path, case_id: str | None = None) -> dict:
    """Rank SOURCE/A/B/C deterministically for one completed case.

    SOURCE is the no-intervention baseline with score 0; candidates with a
    blocking guardrail failure are scored far below it and listed as
    rejected, mirroring the fail-closed authority of the judgment module.
    """
    case_dir = Path(case_dir)
    if case_id is None:
        case_id = _load_json(case_dir / "case_manifest.json")["case_id"]
    scores: dict[str, float] = {"SOURCE": 0.0}
    details: dict[str, dict] = {
        "SOURCE": {
            "technical_assessment": "BASELINE",
            "workflow_decision": "NO_INTERVENTION",
            "goals_met": [],
            "guardrail_failures": [],
            "warning_count": 0,
            "score": 0.0,
        }
    }
    for label in ("A", "B", "C"):
        report_path = case_dir / "05_comparison" / f"source_vs_{label}" / "comparison_report.json"
        if not report_path.is_file():
            raise FileNotFoundError(f"missing comparison report for candidate {label}: {report_path}")
        score, detail = _candidate_score(_load_json(report_path))
        scores[label] = score
        details[label] = detail

    ranking = sorted(scores, key=lambda item: (-scores[item], _TIE_BREAK[item]))
    rejected = [label for label in ("A", "B", "C") if scores[label] < 0]
    completed_at = utc_now()

    payload = {
        "schema_version": "1.0",
        "case_id": case_id,
        "instructions": "Deterministic ranking from comparison judgments. "
        "No human listening is part of the loop (decision 2026-08-11).",
        "allowed_items": list(ALLOWED_ITEMS),
        "ranking": ranking,
        "rejected": rejected,
        "reviewer_id": ALGORITHMIC_REVIEWER_ID,
        "notes": json.dumps(details, ensure_ascii=False, sort_keys=True),
        "completed_at": completed_at.astimezone(timezone.utc).isoformat(),
    }
    return payload


def write_algorithmic_review(case_dir: Path, case_id: str | None = None) -> Path:
    """Persist review.json (schema v1.0 compatible) + machine-readable scores."""
    case_dir = Path(case_dir)
    review = generate_algorithmic_review(case_dir, case_id=case_id)
    review_path = case_dir / "06_human_review" / "review.json"
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")

    scores = json.loads(review["notes"])
    scores_path = case_dir / "06_human_review" / "algorithmic_scores.json"
    scores_path.write_text(
        json.dumps(
            {
                "reviewer_id": ALGORITHMIC_REVIEWER_ID,
                "formula_version": REVIEW_FORMULA_VERSION,
                "completed_at": review["completed_at"],
                "scores": scores,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return review_path
