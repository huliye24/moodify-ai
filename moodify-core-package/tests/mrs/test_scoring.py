"""Tests for the experimental MRS rule-based baseline."""

import pytest

from moodify.mrs import MRSBenchmark, MRSFeatures, RuleBasedMRSScorer


def test_rule_based_score_is_deterministic_and_not_a_listening_claim():
    features = MRSFeatures(1.0, 1.0, 1.0, 1.0, 1.0)

    score = RuleBasedMRSScorer().calculate(features)

    assert score.quality_score == 100.0
    assert score.technical_score == 100.0
    assert score.listening_score is None
    assert score.method == "experimental_rule_based_v1"


def test_features_reject_out_of_range_normalized_input():
    with pytest.raises(ValueError, match="loudness"):
        MRSFeatures(1.1, 0.5, 0.5, 0.5, 0.5)


def test_benchmark_requires_features_before_returning_a_score():
    result = MRSBenchmark().evaluate("sample.wav")

    assert result.status == "FEATURES_REQUIRED"
    assert result.to_dict()["quality_score"] is None


def test_benchmark_returns_the_required_score_fields():
    result = MRSBenchmark().evaluate(
        "sample.wav", MRSFeatures(0.8, 0.7, 0.6, 0.5, 0.9)
    )

    assert result.status == "EXPERIMENTAL_RULE_BASED"
    assert set(result.to_dict()) >= {
        "quality_score",
        "technical_score",
        "listening_score",
    }
