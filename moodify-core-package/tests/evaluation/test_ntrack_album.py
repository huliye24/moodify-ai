"""Album-aware re-ranking: redundancy penalty, diversity contribution,
and quality floor preservation."""

from __future__ import annotations

from moodify.evaluation.ntrack.album import album_rerank, candidate_feature_vector
from moodify.evaluation.ntrack.models import GlobalRankingEstimate, RankedCandidateResult
from moodify.evaluation.ntrack.policy import RankingPolicy


def _estimate(candidates: list[tuple[str, float]]) -> GlobalRankingEstimate:
    return GlobalRankingEstimate(
        ranking_estimate_id="est-1",
        ranking_case_id="RK-1",
        model_version="ntrack_elo_v1",
        ordered_candidates=tuple(
            RankedCandidateResult(candidate_id=cid, rank=i, score=score,
                                  confidence="HIGH", top_k_membership=True)
            for i, (cid, score) in enumerate(candidates, start=1)
        ),
        pairwise_edge_count=0,
    )


def _feature(lufs: float, centroid: float = 3000.0, dynamic: float = 20.0) -> list[float]:
    return [0.25, 0.25, 0.25, 0.25, centroid / 1000.0, (lufs + 14.0) / 20.0, dynamic / 40.0]


def test_redundant_top_track_displaced_when_close():
    policy = RankingPolicy()
    estimate = _estimate([
        ("a", 1005.0), ("b", 1003.0), ("c", 1002.9), ("d", 990.0), ("e", 980.0),
    ])
    vectors = {
        "a": _feature(-14.0), "b": _feature(-14.0),  # identical sonic profile to a
        "c": _feature(-13.0, centroid=5500.0), "d": _feature(-12.0, centroid=5500.0),
        "e": _feature(-11.0, centroid=6500.0),
    }
    album = album_rerank("RK-1", estimate, vectors, policy, top_k=3)
    selected = list(album.selected_candidate_ids)
    assert selected[0] == "a"  # strength wins the top slot
    # b (full redundancy penalty) drops below c (diversity bonus): album order
    # differs from raw strength order while quality stays at the top.
    assert selected[1] == "c"
    assert selected[2] == "b"
    assert any("redundancy" in explanation for explanation in album.explanations)


def test_strength_dominates_redundancy():
    """Album mode must not destroy quality: a much stronger track survives."""
    policy = RankingPolicy()
    estimate = _estimate([
        ("a", 1020.0), ("b", 1019.0), ("c", 990.0), ("d", 980.0),
    ])
    vectors = {
        "a": _feature(-14.0), "b": _feature(-14.0),  # redundant with a but much stronger than c
        "c": _feature(-13.0, centroid=4500.0), "d": _feature(-12.0, centroid=5500.0),
    }
    album = album_rerank("RK-1", estimate, vectors, policy, top_k=3)
    selected = list(album.selected_candidate_ids)
    assert "b" in selected  # strength gap outweighs redundancy penalty


def test_diversity_breaks_near_tie():
    policy = RankingPolicy()
    estimate = _estimate([("a", 1005.0), ("b", 1000.0), ("c", 995.0), ("d", 990.0)])
    vectors = {
        "a": _feature(-14.0, centroid=3000.0),
        "b": _feature(-14.0, centroid=3100.0),  # similar to a
        "c": _feature(-14.0, centroid=6000.0),  # distinct
        "d": _feature(-13.0, centroid=3500.0),
    }
    album = album_rerank("RK-1", estimate, vectors, policy, top_k=3)
    selected = list(album.selected_candidate_ids)
    assert "c" in selected  # diversity brings distinct track into top-3


def test_quality_floor_keeps_all_eligible():
    policy = RankingPolicy()
    estimate = _estimate([("a", 1000.0), ("b", 999.0)])
    vectors = {"a": _feature(-14.0), "b": _feature(-13.0)}
    album = album_rerank("RK-1", estimate, vectors, policy, top_k=None)
    assert album.selected_candidate_ids == ("a", "b")


def test_feature_vector_stable_with_missing_metrics():
    metrics = {"integrated_lufs": -14.0}  # no bands/centroid/dynamic
    vector = candidate_feature_vector(metrics)
    assert len(vector) == 7
    assert all(isinstance(v, float) for v in vector)
