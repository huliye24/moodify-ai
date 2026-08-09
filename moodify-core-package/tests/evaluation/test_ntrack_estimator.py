"""Global rank estimator: determinism, tie bands, INCONCLUSIVE handling,
cycle tolerance, and Top-K boundary confidence."""

from __future__ import annotations

from moodify.evaluation.ntrack.estimator import estimate_global_ranking, plan_pairs
from moodify.evaluation.ntrack.models import PairwiseRankingEdge
from moodify.evaluation.ntrack.policy import RankingPolicy


def _edge(case_id: str, a: str, b: str, outcome: str, confidence: str = "HIGH",
          weight: float = 1.0) -> PairwiseRankingEdge:
    return PairwiseRankingEdge(
        edge_id=f"e-{a}-{b}", ranking_case_id=case_id,
        candidate_a_id=a, candidate_b_id=b,
        outcome=outcome, confidence=confidence, evidence_weight=weight,
    )


def test_clear_chain_orders_correctly():
    policy = RankingPolicy()
    edges = [
        _edge("RK-1", "a", "b", "A_WINS"),
        _edge("RK-1", "b", "c", "A_WINS"),
        _edge("RK-1", "c", "d", "A_WINS"),
    ]
    estimate = estimate_global_ranking("RK-1", edges, policy)
    assert [c.candidate_id for c in estimate.ordered_candidates] == ["a", "b", "c", "d"]
    assert estimate.pairwise_edge_count == 3


def test_inconclusive_edges_never_move_scores():
    policy = RankingPolicy()
    inconclusive = _edge("RK-1", "a", "b", "INCONCLUSIVE")
    estimate = estimate_global_ranking("RK-1", [inconclusive], policy)
    scores = estimate.latent_scores
    assert scores["a"] == scores["b"] == policy.elo_initial_score
    assert estimate.ordered_candidates[0].confidence == "LOW"  # no decisive evidence


def test_cycle_tolerated_without_crash():
    policy = RankingPolicy()
    edges = [
        _edge("RK-1", "a", "b", "A_WINS"),
        _edge("RK-1", "b", "c", "A_WINS"),
        _edge("RK-1", "c", "a", "A_WINS"),
    ]
    estimate = estimate_global_ranking("RK-1", edges, policy)
    assert len(estimate.ordered_candidates) == 3
    assert estimate.tie_bands or all(c.rank for c in estimate.ordered_candidates)


def test_deterministic_given_same_edges():
    policy = RankingPolicy()
    edges = [
        _edge("RK-1", "a", "b", "A_WINS", "MEDIUM"),
        _edge("RK-1", "b", "c", "B_WINS", "LOW", 0.5),
        _edge("RK-1", "c", "d", "A_WINS", "HIGH", 1.2),
    ]
    first = estimate_global_ranking("RK-1", edges, policy)
    second = estimate_global_ranking("RK-1", edges, policy)
    assert [c.candidate_id for c in first.ordered_candidates] == [
        c.candidate_id for c in second.ordered_candidates
    ]
    assert first.latent_scores == second.latent_scores


def test_near_identical_scores_form_tie_band():
    policy = RankingPolicy()
    edges = [
        _edge("RK-1", "a", "b", "A_WINS", "LOW", 0.1),
        _edge("RK-1", "c", "d", "A_WINS", "LOW", 0.1),
    ]
    estimate = estimate_global_ranking("RK-1", edges, policy)
    # a/c both gained tiny weight; b/d unchanged -> two bands of near ties
    assert len(estimate.tie_bands) >= 1


def test_top_k_boundary_low_confidence():
    policy = RankingPolicy()
    edges = [
        _edge("RK-1", "a", "b", "A_WINS", "LOW", 0.2),
        _edge("RK-1", "b", "c", "A_WINS", "LOW", 0.2),
        _edge("RK-1", "c", "d", "A_WINS", "LOW", 0.2),
        _edge("RK-1", "d", "e", "A_WINS", "LOW", 0.2),
    ]
    estimate = estimate_global_ranking("RK-1", edges, policy, top_k=4)
    ordered = estimate.ordered_candidates
    assert ordered[3].top_k_membership is True  # rank 4 = boundary
    assert ordered[4].top_k_membership is False


def test_plan_pairs_small_batch_exhaustive():
    policy = RankingPolicy()
    plan = plan_pairs(["a", "b", "c", "d"], policy)
    assert len(plan.pair_ids) == 6
    assert plan.budget_name == "small_batch_exhaustive"


def test_plan_pairs_medium_batch_respects_budget():
    policy = RankingPolicy()
    candidates = [f"c{i}" for i in range(30)]
    plan = plan_pairs(candidates, policy)
    assert len(plan.pair_ids) <= plan.budget_limit == 120
    assert plan.total_pairs_available == 435


def test_plan_pairs_top_k_covers_boundary_first():
    policy = RankingPolicy()
    candidates = [f"c{i}" for i in range(20)]
    order = list(reversed(candidates))
    plan = plan_pairs(candidates, policy, initial_order=order, top_k=5)
    ids = {cid for pair in plan.pair_ids for cid in pair}
    boundary = set(order[3:7])
    assert ids & boundary  # boundary neighborhood covered
