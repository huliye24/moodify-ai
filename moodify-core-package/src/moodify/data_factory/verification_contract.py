"""Controlled verification contract — machine judge over intervention output.

MFY_EAR_MACHINE_JUDGE_AND_CONTROLLED_VERIFY_001:
- reuse Intervention Lab (plan_generator/intervention) and auditory judgment;
  no second processing engine.
- every plan is a candidate; execution only after deterministic policy +
  schema validation.
- outcomes are objective verification enums; conflicts / out-of-domain /
  strong side effects / low confidence => HUMAN_REVIEW_RECOMMENDED.
- enabled by default only for synthetic/controlled samples; automatic
  intervention on real works requires separate authorization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from moodify.auditory.judgment import evaluate_processing_plan
from moodify.contracts.machine_finding import FindingType

ALLOWED_HYPOTHESIS_MAPPINGS: dict[FindingType, tuple[str, ...]] = {
    FindingType.CLIPPING_EVENT: ("NO_NEW_CLIPPING", "TRUE_PEAK_SAFE"),
    FindingType.TRUE_PEAK_EVENT: ("TRUE_PEAK_SAFE", "NO_NEW_CLIPPING"),
    FindingType.ENERGY_CHANGE: ("LOUDNESS_TARGET", "SPECTRAL_TARGET"),
    FindingType.BASELINE_DEVIATION: ("LOUDNESS_TARGET", "SPECTRAL_TARGET"),
}

FORBIDDEN_HYPOTHESIS_MAPPINGS: tuple[str, ...] = (
    "SOUNDS_BETTER",
    "PRODUCTION_APPROVED",
    "HIGH_QUALITY_MUSIC",
    "COPYRIGHT_VALID",
)

CONFLICT_FINDINGS = {FindingType.EVIDENCE_CONFLICT, FindingType.OUT_OF_DOMAIN}


class VerificationOutcome(str, Enum):
    PASS = "PASS"
    CONDITIONAL_PASS = "CONDITIONAL_PASS"
    HUMAN_REVIEW_RECOMMENDED = "HUMAN_REVIEW_RECOMMENDED"
    FAIL = "FAIL"


@dataclass(frozen=True)
class Hypothesis:
    hypothesis_id: str
    finding_type: FindingType
    proposed_plan_goal: str  # goal_id from the plan's technical_goals
    domain: str
    note: str = ""

    def validate(self) -> None:
        if self.proposed_plan_goal in FORBIDDEN_HYPOTHESIS_MAPPINGS:
            raise ValueError(f"forbidden hypothesis goal: {self.proposed_plan_goal}")
        allowed = ALLOWED_HYPOTHESIS_MAPPINGS.get(self.finding_type, ())
        if self.proposed_plan_goal not in allowed:
            raise ValueError(
                f"hypothesis goal {self.proposed_plan_goal} not allowed for "
                f"{self.finding_type.value}; allowed={allowed or 'none'}"
            )


@dataclass(frozen=True)
class VerificationResult:
    case_id: str
    outcome: VerificationOutcome
    goals_met: tuple[str, ...] = ()
    guardrail_failures: tuple[str, ...] = ()
    findings: tuple[dict[str, Any], ...] = ()
    reasons: tuple[str, ...] = ()
    requires_human_review: bool = False
    review_note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "outcome": self.outcome.value,
            "goals_met": list(self.goals_met),
            "guardrail_failures": list(self.guardrail_failures),
            "findings": [dict(f) for f in self.findings],
            "reasons": list(self.reasons),
            "requires_human_review": self.requires_human_review,
            "review_note": self.review_note,
        }


def verify_intervention(
    *,
    case_id: str,
    plan: dict[str, Any],
    metric_delta: dict[str, Any],
    before_metrics: dict[str, Any],
    after_metrics: dict[str, Any],
    findings: list[dict[str, Any]] | None = None,
) -> VerificationResult:
    """Objective verification of one intervention against its own plan.

    - goals/guardrails evaluated with the existing judgment contract;
    - any blocking guardrail failure, out-of-domain finding, evidence conflict,
      or very low confidence => HUMAN_REVIEW_RECOMMENDED (never silent PASS).
    """
    findings = findings or []
    goals_met, guardrail_failures = evaluate_processing_plan(
        plan, metric_delta, before_metrics, after_metrics
    )
    reasons: list[str] = []
    human_review = False
    review_notes: list[str] = []

    for f in findings:
        ftype = f.get("finding_type")
        if ftype in CONFLICT_FINDINGS:
            human_review = True
            review_notes.append(f"conflict/out-of-domain finding: {ftype}")
        conf = f.get("confidence")
        if isinstance(conf, (int, float)) and conf < 0.5:
            human_review = True
            review_notes.append(f"low confidence finding: {ftype} ({conf})")

    if guardrail_failures:
        human_review = True
        review_notes.append(f"blocking guardrail failures: {', '.join(guardrail_failures)}")

    if human_review:
        outcome = VerificationOutcome.HUMAN_REVIEW_RECOMMENDED
        reasons = review_notes or ["human review recommended"]
    elif goals_met and not guardrail_failures:
        outcome = VerificationOutcome.PASS
        reasons = ["all technical goals met, no guardrail failures"]
    elif goals_met:
        outcome = VerificationOutcome.CONDITIONAL_PASS
        reasons = ["goals met with non-blocking guardrail warnings"]
    else:
        outcome = VerificationOutcome.FAIL
        reasons = ["technical goals not met"]

    return VerificationResult(
        case_id=case_id,
        outcome=outcome,
        goals_met=tuple(goals_met),
        guardrail_failures=tuple(guardrail_failures),
        findings=tuple(findings),
        reasons=tuple(reasons),
        requires_human_review=human_review,
        review_note=" | ".join(review_notes) if review_notes else "",
    )


def allowed_hypothesis(goal_id: str, finding_type: FindingType) -> bool:
    return goal_id in ALLOWED_HYPOTHESIS_MAPPINGS.get(finding_type, ())
