"""Pairwise decision policy (DSK-MFY-PAIRWISE-JUDGE-001).

Aggregates dimension results into exactly one outcome with a confidence band.
Abstention is mandatory: analysis failure, insufficient coverage, insufficient
margin, unresolved conflict, or near-tie all yield INCONCLUSIVE. Confidence is
only ever reported in LOW / MEDIUM / HIGH bands — never fake numeric precision.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml

from moodify.evaluation.pairwise.models import (
    DimensionResult,
    PairwiseJudgment,
)

DEFAULT_POLICY_PATH = Path(__file__).resolve().parents[4] / "configs" / "pairwise_policy_v1.yaml"

# dimension -> weight (must sum to 1.0)
DEFAULT_WEIGHTS: dict[str, float] = {
    "signal_integrity": 0.30,
    "loudness": 0.15,
    "dynamics": 0.20,
    "spectral_balance": 0.20,
    "stereo_phase": 0.15,
}


@dataclass(frozen=True)
class DecisionPolicy:
    version: str = "pairwise_policy_v1"
    weights: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))
    min_evidence_coverage: float = 0.5
    min_winner_margin: float = 0.15
    conflict_threshold: float = 0.30
    abstention_confidence_band: str = "LOW"

    @classmethod
    def from_yaml(cls, path: str | Path) -> "DecisionPolicy":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        weights = dict(data.get("dimension_weights", DEFAULT_WEIGHTS))
        return cls(
            version=data.get("policy_version", "pairwise_policy_v1"),
            weights=weights,
            min_evidence_coverage=float(data.get("min_evidence_coverage", 0.5)),
            min_winner_margin=float(data.get("min_winner_margin", 0.15)),
            conflict_threshold=float(data.get("conflict_threshold", 0.30)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_version": self.version,
            "dimension_weights": dict(self.weights),
            "min_evidence_coverage": self.min_evidence_coverage,
            "min_winner_margin": self.min_winner_margin,
            "conflict_threshold": self.conflict_threshold,
        }


def decide(
    dimensions: list[DimensionResult],
    policy: DecisionPolicy,
    pairwise_case_id: str,
    analysis_failed: list[str] | None = None,
) -> PairwiseJudgment:
    """Aggregate dimension results into a judgment with mandatory abstention."""
    failed = list(analysis_failed or [])
    if failed:
        return PairwiseJudgment(
            judgment_id=f"jud-{uuid4().hex[:12]}",
            pairwise_case_id=pairwise_case_id,
            policy_version=policy.version,
            outcome="INCONCLUSIVE",
            confidence_level=policy.abstention_confidence_band,
            winner_margin=0.0,
            evidence_coverage=0.0,
            top_reasons=tuple(f"ANALYSIS_FAILED:{name}" for name in failed),
            limitations=tuple(f"analysis failed for {name}" for name in failed),
        )

    total_weight = sum(policy.weights.get(d.dimension, 0.0) for d in dimensions) or 1.0
    covered_weight = sum(
        policy.weights.get(d.dimension, 0.0)
        for d in dimensions
        if d.relative_result != "INSUFFICIENT_EVIDENCE"
    )
    coverage = round(covered_weight / total_weight, 4)

    score = 0.0
    conflict_weight = 0.0
    for d in dimensions:
        weight = policy.weights.get(d.dimension, 0.0)
        if d.relative_result == "A_BETTER":
            score += weight
        elif d.relative_result == "B_BETTER":
            score -= weight
        elif d.relative_result == "INSUFFICIENT_EVIDENCE":
            continue
        # TIE contributes nothing to score or conflict
    margin = round(abs(score) / total_weight, 4) if total_weight else 0.0

    # Conflict: strong dimensions disagreeing (A and B both above half-weight)
    a_weight = sum(
        policy.weights.get(d.dimension, 0.0) for d in dimensions if d.relative_result == "A_BETTER"
    )
    b_weight = sum(
        policy.weights.get(d.dimension, 0.0) for d in dimensions if d.relative_result == "B_BETTER"
    )
    if a_weight > 0 and b_weight > 0:
        conflict_weight = min(a_weight, b_weight) / max(a_weight, b_weight)

    reasons: list[str] = []
    limitations: list[str] = []
    if coverage < policy.min_evidence_coverage:
        reasons.append("INSUFFICIENT_EVIDENCE_COVERAGE")
    if margin <= policy.min_winner_margin:
        reasons.append("INSUFFICIENT_WINNER_MARGIN")
    if conflict_weight > policy.conflict_threshold:
        reasons.append("DIMENSION_CONFLICT")

    if reasons:
        outcome = "INCONCLUSIVE"
        confidence = policy.abstention_confidence_band
    else:
        outcome = "A_WINS" if score > 0 else "B_WINS"
        if margin >= 0.4 and coverage >= 0.7 and conflict_weight <= policy.conflict_threshold:
            confidence = "HIGH"
        elif margin >= 0.25:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
        reasons.append(f"WINNER_MARGIN={margin:.3f}")

    return PairwiseJudgment(
        judgment_id=f"jud-{uuid4().hex[:12]}",
        pairwise_case_id=pairwise_case_id,
        policy_version=policy.version,
        outcome=outcome,
        confidence_level=confidence,
        winner_margin=round(margin, 4),
        evidence_coverage=round(coverage, 4),
        top_reasons=tuple(reasons),
        evidence_refs=tuple(
            ref
            for d in dimensions
            for ref in d.evidence_refs
            if d.relative_result != "INSUFFICIENT_EVIDENCE"
        ),
        limitations=tuple(limitations),
    )
