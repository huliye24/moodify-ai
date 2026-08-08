"""Pairwise decision policy tests (three-way outcome, abstention, bands)."""
from __future__ import annotations

import pytest

from moodify.evaluation.pairwise.models import DimensionResult
from moodify.evaluation.pairwise.policy import DecisionPolicy, decide


def _dims(**overrides) -> list[DimensionResult]:
    base = {
        "signal_integrity": "TIE",
        "loudness": "TIE",
        "dynamics": "TIE",
        "spectral_balance": "TIE",
        "stereo_phase": "TIE",
    }
    base.update(overrides)
    return [
        DimensionResult(name, 0.0, 0.0, verdict, 0.8)
        for name, verdict in base.items()
    ]


def test_clear_a_win():
    dims = _dims(signal_integrity="A_BETTER", dynamics="A_BETTER", spectral_balance="A_BETTER")
    judgment = decide(dims, DecisionPolicy(), "PW-1")
    assert judgment.outcome == "A_WINS"
    assert judgment.confidence_level == "HIGH"


def test_clear_b_win():
    dims = _dims(signal_integrity="B_BETTER", loudness="B_BETTER", stereo_phase="B_BETTER")
    judgment = decide(dims, DecisionPolicy(), "PW-2")
    assert judgment.outcome == "B_WINS"


def test_near_tie_abstains():
    dims = _dims(loudness="A_BETTER")  # single 0.15-weight dimension
    judgment = decide(dims, DecisionPolicy(), "PW-3")
    assert judgment.outcome == "INCONCLUSIVE"
    assert "INSUFFICIENT_WINNER_MARGIN" in judgment.top_reasons


def test_insufficient_coverage_abstains():
    dims = _dims(signal_integrity="A_BETTER", stereo_phase="INSUFFICIENT_EVIDENCE",
                 spectral_balance="INSUFFICIENT_EVIDENCE", loudness="INSUFFICIENT_EVIDENCE",
                 dynamics="INSUFFICIENT_EVIDENCE")
    judgment = decide(dims, DecisionPolicy(), "PW-4")
    assert judgment.outcome == "INCONCLUSIVE"
    assert "INSUFFICIENT_EVIDENCE_COVERAGE" in judgment.top_reasons


def test_analysis_failure_abstains():
    dims = _dims()
    judgment = decide(dims, DecisionPolicy(), "PW-5", analysis_failed=["candidate_a:Error"])
    assert judgment.outcome == "INCONCLUSIVE"
    assert any(r.startswith("ANALYSIS_FAILED") for r in judgment.top_reasons)


def test_dimension_conflict_abstains():
    dims = _dims(signal_integrity="A_BETTER", loudness="B_BETTER")
    judgment = decide(dims, DecisionPolicy(), "PW-6")
    assert judgment.outcome == "INCONCLUSIVE"
    assert "DIMENSION_CONFLICT" in judgment.top_reasons


def test_policy_from_yaml():
    policy = DecisionPolicy.from_yaml("configs/pairwise_policy_v1.yaml")
    assert policy.version == "pairwise_policy_v1"
    assert sum(policy.weights.values()) == pytest.approx(1.0)
    assert policy.min_winner_margin == 0.15


def test_confidence_bands():
    medium = _dims(signal_integrity="A_BETTER")  # margin 0.30 -> MEDIUM
    judgment = decide(medium, DecisionPolicy(), "PW-7")
    assert judgment.outcome == "A_WINS"
    assert judgment.confidence_level == "MEDIUM"
    high = _dims(signal_integrity="A_BETTER", loudness="A_BETTER")  # margin 0.45 -> HIGH
    judgment = decide(high, DecisionPolicy(), "PW-8")
    assert judgment.confidence_level == "HIGH"
    low = _dims(loudness="A_BETTER")  # margin 0.15 -> abstain, LOW
    judgment = decide(low, DecisionPolicy(), "PW-9")
    assert judgment.outcome == "INCONCLUSIVE"
    assert judgment.confidence_level == "LOW"
