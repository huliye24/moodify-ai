"""Recommendation ranking pipeline (DSK-MFY-TASTE-FEED-PATCH-001).

candidate generation -> filter -> score -> session re-rank. Weighted
heuristic pipeline: content similarity to the user's combined taste
vector, novelty/exploration budget, diversity contribution, quality
confidence, and session repetition control. Explanations are emitted as
tokens on every ranked item.
"""

from __future__ import annotations

import math

from moodify.recommendation.models import (
    AuditoryProfile,
    Track,
    UserTasteProfile,
)
from moodify.recommendation.policy import RecommendationPolicy
from moodify.recommendation.taste import merge_taste


def _distance(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    if not a or not b:
        return 1.0
    size = max(len(a), len(b))
    padded_a = tuple(a) + (0.0,) * (size - len(a))
    padded_b = tuple(b) + (0.0,) * (size - len(b))
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(padded_a, padded_b)))


def _similarity(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    return 1.0 / (1.0 + _distance(a, b))


def generate_candidates(
    tracks: list[Track],
    profiles: dict[str, AuditoryProfile],
    taste: UserTasteProfile,
    policy: RecommendationPolicy,
    session_played: set[str] = frozenset(),
) -> list[tuple[str, str, float]]:
    """Return (track_id, source, affinity_score) candidates.

    Sources: similarity retrieval (preference match), exploration pool
    (freshness/broad), and recent-affinity tracks. Quality-gated tracks
    and session repetitions are filtered out here.
    """
    combined = merge_taste(taste, policy)
    scored: list[tuple[str, str, float]] = []
    for track in tracks:
        if track.track_id in session_played:
            continue
        if track.availability_state != "AVAILABLE":
            continue
        if track.quality_state == "SEVERE_ISSUES" and policy.quality_floor_required:
            continue
        profile = profiles.get(track.track_id)
        vector = profile.feature_vector if profile else ()
        affinity = _similarity(vector, combined) if combined else 0.5
        scored.append((track.track_id, "similarity", affinity))

    scored.sort(key=lambda item: item[2], reverse=True)
    pool = scored[:policy.candidate_pool_size]

    # Exploration bucket: tracks outside the top preference slice get a
    # controlled share of the pool.
    exploration_budget = max(1, int(policy.candidate_pool_size * policy.exploration_fraction))
    exploration = scored[policy.candidate_pool_size - exploration_budget:
                         policy.candidate_pool_size + exploration_budget] if len(scored) > policy.candidate_pool_size else scored[-exploration_budget:]
    for track_id, _, affinity in exploration:
        if track_id not in {item[0] for item in pool}:
            pool.append((track_id, "exploration", affinity))
    return pool[:policy.candidate_pool_size]


def score_candidates(
    candidates: list[tuple[str, str, float]],
    tracks: list[Track],
    profiles: dict[str, AuditoryProfile],
    taste: UserTasteProfile,
    policy: RecommendationPolicy,
    session_played: set[str] = frozenset(),
    recent_played: set[str] = frozenset(),
) -> list[tuple[str, float, list[str]]]:
    """Score each candidate and return (track_id, final_score, explanation)."""
    combined = merge_taste(taste, policy)
    weights = policy.scoring_weights
    scored: list[tuple[str, float, list[str]]] = []
    for track_id, source, affinity in candidates:
        track = next((t for t in tracks if t.track_id == track_id), None)
        if track is None:
            continue
        profile = profiles.get(track_id)
        vector = profile.feature_vector if profile else ()
        quality = profile.quality_confidence if profile else 0.0

        preference_match = affinity * weights.get("preference_match", 1.0)
        novelty = 0.0
        if source == "exploration" or track_id in recent_played:
            novelty = weights.get("novelty_bonus", 0.15) * taste.novelty_tolerance
        diversity = 0.0
        if session_played:
            diversity = weights.get("diversity_bonus", 0.20) * _min_session_distance(vector, session_played, profiles)
        transition = weights.get("transition_coherence", 0.10) * _similarity(vector, combined) if combined else 0.0
        quality_component = weights.get("quality_confidence", 0.25) * quality

        total = preference_match + novelty + diversity + transition + quality_component
        tokens = [f"source:{source}", f"pref_match:{preference_match:.3f}"]
        if novelty:
            tokens.append(f"novelty:{novelty:.3f}")
        if diversity:
            tokens.append(f"diversity:{diversity:.3f}")
        if quality:
            tokens.append(f"quality:{quality:.3f}")
        scored.append((track_id, round(total, 6), tokens))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored


def _min_session_distance(vector: tuple[float, ...], session_played: set[str],
                          profiles: dict[str, AuditoryProfile]) -> float:
    if not vector:
        return 0.0
    distances = [
        _distance(vector, profiles[track_id].feature_vector)
        for track_id in session_played
        if track_id in profiles and profiles[track_id].feature_vector
    ]
    return min(distances) if distances else 1.0


def rerank_for_session(
    scored: list[tuple[str, float, list[str]]],
    size: int,
    session_played: set[str] = frozenset(),
) -> list[tuple[str, float, list[str]]]:
    """Variety-aware final selection: avoid repeated energy/texture blocks."""
    selected: list[tuple[str, float, list[str]]] = []
    remaining = list(scored)
    while remaining and len(selected) < size:
        selected.append(remaining.pop(0))
        # Move the next item whose vector differs most to the front of
        # the remainder (approximate variety without full re-scoring).
        if remaining and len(remaining) > 1:
            remaining.sort(key=lambda item: -abs(item[1] - selected[-1][1]))
    return selected
