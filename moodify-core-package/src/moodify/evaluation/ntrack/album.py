"""Album-aware re-ranking (DSK-MFY-NTRACK-RANKER-001).

Raw track strength answers "which track is individually strongest".
Album selection asks "which tracks best form this specific set" —
redundant near-identical top tracks should not monopolize an album.
Every factor is evidence-linked to canonical scan metrics and
individually toggleable via the ranking policy.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from moodify.evaluation.ntrack.models import (
    AlbumAwareRanking,
    GlobalRankingEstimate,
    RankedCandidateResult,
)
from moodify.evaluation.ntrack.policy import RankingPolicy

REDUNDANCY_EVIDENCE_REFS = ("band_ratios", "spectral_centroid_hz", "integrated_lufs", "dynamic_range")
DIVERSITY_EVIDENCE_REFS = ("band_ratios", "spectral_centroid_hz", "integrated_lufs")


def _metric(metrics: dict[str, Any], key: str, default: float = 0.0) -> float:
    entry = metrics.get(key)
    if isinstance(entry, dict):
        entry = entry.get("value")
    try:
        value = float(entry)
        return value if value == value else default  # reject NaN
    except (TypeError, ValueError):
        return default


_BAND_KEYS = (
    "band_energy_sub_20_60_hz", "band_energy_bass_60_120_hz",
    "band_energy_low_mid_120_250_hz", "band_energy_mid_250_500_hz",
    "band_energy_core_mid_500_2000_hz", "band_energy_presence_2000_5000_hz",
    "band_energy_brilliance_5000_10000_hz", "band_energy_air_10000_16000_hz",
)


def _band_ratios(metrics: dict[str, Any]) -> list[float]:
    values = [_metric(metrics, key) for key in _BAND_KEYS]
    total = sum(values) or 1.0
    return [round(v / total, 6) for v in values]


def candidate_feature_vector(metrics: dict[str, Any]) -> list[float]:
    """Small evidence-linked feature vector for redundancy/diversity.

    Uses only metrics the canonical scan actually produces; missing
    features degrade gracefully to zeros so the vector stays stable.
    """
    bands = _band_ratios(metrics)
    if len(bands) < 4:
        bands = [0.0, 0.0, 0.0, 0.0]
    centroid = _metric(metrics, "spectral_centroid_hz")
    lufs = _metric(metrics, "integrated_lufs")
    dynamic = _metric(metrics, "dynamic_range")
    return [bands[0], bands[1], bands[2], bands[3], centroid / 1000.0, (lufs + 14.0) / 20.0, dynamic / 40.0]


def _distance(a: list[float], b: list[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def album_rerank(
    ranking_case_id: str,
    estimate: GlobalRankingEstimate,
    feature_vectors: dict[str, list[float]],
    policy: RankingPolicy,
    top_k: int | None = None,
) -> AlbumAwareRanking:
    """Greedy album selection preserving quality floor.

    Album Utility = strength + diversity contribution - redundancy,
    where every term is evidence-linked and weighted by policy.
    """
    ordered = list(estimate.ordered_candidates)
    if not ordered:
        return AlbumAwareRanking(
            album_ranking_id=f"alb-{uuid4().hex[:12]}",
            ranking_case_id=ranking_case_id,
            base_ranking_estimate_id=estimate.ranking_estimate_id,
            policy_version=policy.version,
        )

    strengths: dict[str, float] = {c.candidate_id: c.score or 0.0 for c in ordered}
    selected: list[RankedCandidateResult] = []
    remaining = list(ordered)
    penalties: dict[str, float] = {}
    contributions: dict[str, float] = {}
    explanations: list[str] = []

    def _vector(cid: str) -> list[float]:
        return feature_vectors.get(cid, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    limit = top_k if top_k and top_k > 0 else len(ordered)
    for _ in range(limit):
        if not remaining:
            break
        best = None
        best_utility = float("-inf")
        best_penalty = 0.0
        best_diversity = 0.0
        for candidate in remaining:
            cid = candidate.candidate_id
            strength = strengths.get(cid, 0.0)
            if selected:
                distances = [_distance(_vector(cid), _vector(s.candidate_id)) for s in selected]
                min_distance = min(distances)
                # Similarity-based penalty: identical profiles (distance 0)
                # receive the full penalty; distinct profiles approach zero.
                redundancy = 1.0 / (1.0 + min_distance) if policy.redundancy_penalty_enabled else 0.0
                # Complementary contribution grows with distance, saturating at 1.
                diversity = min_distance / (1.0 + min_distance) if policy.diversity_bonus_enabled else 0.0
            else:
                redundancy = 0.0
                diversity = 0.0
            utility = (
                strength
                - policy.redundancy_penalty_weight * redundancy
                + policy.diversity_bonus_weight * diversity
            )
            if best is None or utility > best_utility:
                best, best_utility = candidate, utility
                best_penalty = redundancy
                best_diversity = diversity
        if best is None:
            break
        cid = best.candidate_id
        selected.append(best)
        penalties[cid] = round(best_penalty, 4)
        contributions[cid] = round(best_diversity, 4)
        remaining = [c for c in remaining if c.candidate_id != cid]
        if best_penalty > 0.0:
            explanations.append(
                f"{cid}: redundancy penalty {best_penalty:.3f} "
                f"(similar spectral/energy profile to selected tracks)"
            )
        if best_diversity > 0.0:
            explanations.append(f"{cid}: diversity contribution {best_diversity:.3f}")

    reranked = [
        RankedCandidateResult(
            candidate_id=c.candidate_id,
            rank=i,
            rank_band="",
            score=c.score,
            confidence=c.confidence,
            top_k_membership=i <= (top_k or len(selected)),
            reasons=c.reasons,
            evidence_refs=c.evidence_refs,
        )
        for i, c in enumerate(selected, start=1)
    ]

    displaced = [c.candidate_id for c in ordered if c.candidate_id not in {r.candidate_id for r in reranked}]
    if displaced:
        explanations.append(f"displaced from top selection: {', '.join(displaced)}")

    return AlbumAwareRanking(
        album_ranking_id=f"alb-{uuid4().hex[:12]}",
        ranking_case_id=ranking_case_id,
        base_ranking_estimate_id=estimate.ranking_estimate_id,
        policy_version=policy.version,
        selected_candidate_ids=tuple(r.candidate_id for r in reranked),
        reranked_candidates=tuple(reranked),
        redundancy_penalties=penalties,
        diversity_contributions=contributions,
        explanations=tuple(explanations),
    )
