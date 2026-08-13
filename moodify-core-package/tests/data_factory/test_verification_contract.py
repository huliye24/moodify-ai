"""Machine judge / controlled verification contract tests.

MFY_EAR_MACHINE_JUDGE_AND_CONTROLLED_VERIFY_001: allowed hypothesis mapping,
objective verification enums, human-review triggers.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from moodify.contracts.machine_finding import FindingType, FORBIDDEN_CONCLUSIONS
from moodify.data_factory.verification_contract import (
    VerificationOutcome,
    allowed_hypothesis,
    verify_intervention,
)
from moodify.data_factory.verification_contract import Hypothesis

PLAN = {
    "plan_id": "plan_test_1",
    "technical_goals": [
        {"goal_id": "LOUDNESS_TARGET", "metric": "integrated_lufs",
         "desired_direction": "INCREASE", "minimum_meaningful_change": 1.0},
    ],
    "guardrails": [
        {"guardrail_id": "NO_NEW_CLIPPING", "metric": "clipping_sample_ratio",
         "comparator": "BASELINE_DELTA_LE", "threshold": 0.0, "severity": "BLOCKING"},
    ],
}


def _delta(lufs: float, clipping: float = 0.0) -> dict:
    return {
        "integrated_lufs": {"absolute_delta": lufs, "before": -20.0, "after": -20.0 + lufs},
        "clipping_sample_ratio": {"absolute_delta": clipping, "before": 0.0, "after": clipping},
    }


def test_goal_met_pass():
    r = verify_intervention(
        case_id="case_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        plan=PLAN,
        metric_delta=_delta(2.5),
        before_metrics={}, after_metrics={},
    )
    assert r.outcome == VerificationOutcome.PASS
    assert r.goals_met == ("LOUDNESS_TARGET",)


def test_guardrail_failure_requires_human_review():
    r = verify_intervention(
        case_id="case_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        plan=PLAN,
        metric_delta=_delta(2.5, clipping=0.002),
        before_metrics={}, after_metrics={},
    )
    assert r.outcome == VerificationOutcome.HUMAN_REVIEW_RECOMMENDED
    assert r.requires_human_review is True
    assert "NO_NEW_CLIPPING" in r.guardrail_failures


def test_low_confidence_finding_triggers_human_review():
    r = verify_intervention(
        case_id="case_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        plan=PLAN,
        metric_delta=_delta(2.5),
        before_metrics={}, after_metrics={},
        findings=[{"finding_type": FindingType.ENERGY_CHANGE, "confidence": 0.3, "metric": "x", "value": 1.0, "domain": "wse"}],
    )
    assert r.outcome == VerificationOutcome.HUMAN_REVIEW_RECOMMENDED


def test_out_of_domain_finding_triggers_human_review():
    r = verify_intervention(
        case_id="case_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        plan=PLAN,
        metric_delta=_delta(2.5),
        before_metrics={}, after_metrics={},
        findings=[{"finding_type": FindingType.OUT_OF_DOMAIN, "confidence": 0.9, "metric": "x", "value": 1.0, "domain": "wse"}],
    )
    assert r.requires_human_review is True


def test_goal_not_met_fails():
    r = verify_intervention(
        case_id="case_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        plan=PLAN,
        metric_delta=_delta(0.2),
        before_metrics={}, after_metrics={},
    )
    assert r.outcome == VerificationOutcome.FAIL


def test_hypothesis_mapping_allowed_and_forbidden():
    assert allowed_hypothesis("NO_NEW_CLIPPING", FindingType.CLIPPING_EVENT)
    assert not allowed_hypothesis("SOUNDS_BETTER", FindingType.CLIPPING_EVENT)
    h = Hypothesis(
        hypothesis_id="hyp_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        finding_type=FindingType.CLIPPING_EVENT,
        proposed_plan_goal="NO_NEW_CLIPPING",
        domain="wse",
    )
    h.validate()  # allowed
    bad = Hypothesis(
        hypothesis_id="hyp_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        finding_type=FindingType.CLIPPING_EVENT,
        proposed_plan_goal="SOUNDS_BETTER",
        domain="wse",
    )
    with pytest.raises(ValueError):
        bad.validate()


def test_no_aesthetic_conclusions_in_contract():
    # the contract surface must never expose forbidden conclusions
    import moodify.data_factory.verification_contract as vc

    for name in FORBIDDEN_CONCLUSIONS:
        assert name not in vc.__dict__
        assert name not in VerificationOutcome.__members__
