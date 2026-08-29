"""Repository-level checks for the experimental MRS contract."""

from moodify.mrs import MRSBenchmark, MRSFeatures, RuleBasedMRSScorer


def test_mrs_score_and_benchmark_result_shape():
    features = MRSFeatures(0.8, 0.7, 0.6, 0.5, 0.9)
    score = RuleBasedMRSScorer().calculate(features)
    result = MRSBenchmark().evaluate("fixture.wav", features).to_dict()

    assert 0.0 <= score.quality_score <= 100.0
    assert score.listening_score is None
    assert result["quality_score"] == score.quality_score
    assert {"quality_score", "technical_score", "listening_score"} <= set(result)
