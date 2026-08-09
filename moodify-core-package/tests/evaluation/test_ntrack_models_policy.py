"""N-track models round-trip and policy budget tests."""

from __future__ import annotations

from moodify.evaluation.ntrack.models import (
    AlbumAwareRanking,
    GlobalRankingEstimate,
    HumanRankingDecision,
    PairwiseRankingEdge,
    QualityGateResult,
    RankedCandidateResult,
    RankingCandidate,
)
from moodify.evaluation.ntrack.policy import RankingPolicy


def _estimate() -> GlobalRankingEstimate:
    return GlobalRankingEstimate(
        ranking_estimate_id="est-1",
        ranking_case_id="RK-1",
        model_version="ntrack_elo_v1",
        ordered_candidates=(
            RankedCandidateResult(candidate_id="c-1", rank=1, confidence="HIGH",
                                  top_k_membership=True, score=1010.0),
            RankedCandidateResult(candidate_id="c-2", rank=2, confidence="LOW",
                                  top_k_membership=True, score=1005.0),
        ),
        tie_bands=(("c-2",),),
        latent_scores={"c-1": 1010.0, "c-2": 1005.0},
        pairwise_edge_count=1,
    )


def test_models_round_trip():
    cases = [
        RankingCandidate(ranking_candidate_id="rc-1", ranking_case_id="RK-1",
                         source_audio_id="a.wav", source_hash="h", original_position=1,
                         quality_gate_state="ELIGIBLE"),
        QualityGateResult(candidate_id="rc-1", state="ELIGIBLE",
                          reasons=("OK",), evidence_refs=("r1",)),
        PairwiseRankingEdge(edge_id="e-1", ranking_case_id="RK-1",
                            candidate_a_id="rc-1", candidate_b_id="rc-2",
                            outcome="A_WINS", confidence="HIGH"),
        _estimate(),
        AlbumAwareRanking(album_ranking_id="alb-1", ranking_case_id="RK-1",
                          base_ranking_estimate_id="est-1", policy_version="ntrack_policy_v1",
                          selected_candidate_ids=("rc-1",)),
        HumanRankingDecision(human_ranking_decision_id="hr-1", ranking_case_id="RK-1",
                             machine_order=("rc-1", "rc-2"), human_order=("rc-2", "rc-1")),
    ]
    for model in cases:
        restored = type(model).from_dict(model.to_dict())
        assert restored == model


def test_policy_from_yaml_matches_example():
    policy = RankingPolicy.from_yaml()
    assert policy.version == "ntrack_policy_v1"
    assert policy.elo_initial_score == 1000.0
    assert policy.confidence_weight["HIGH"] == 1.0
    payload = policy.to_dict()
    assert payload["uncertainty"]["minimum_rank_separation"] == 10.0


def test_budget_small_batch_exhaustive():
    policy = RankingPolicy()
    budget = policy.comparison_budget_for(12)
    assert budget["budget_name"] == "small_batch_exhaustive"
    assert budget["max_pairs"] == 66
    assert budget["fraction_of_all_pairs"] == 1.0


def test_budget_medium_batch_capped():
    policy = RankingPolicy()
    budget = policy.comparison_budget_for(30)
    assert budget["budget_name"] == "medium_batch_capped"
    assert budget["max_pairs"] == 120  # 30 * 4
    assert budget["max_pairs"] < budget["all_pairs"]  # 435


def test_budget_large_batch_capped():
    policy = RankingPolicy()
    budget = policy.comparison_budget_for(200)
    assert budget["budget_name"] == "large_batch_capped"
    assert budget["max_pairs"] == 600  # 200 * 3
    assert budget["fraction_of_all_pairs"] < 0.05
