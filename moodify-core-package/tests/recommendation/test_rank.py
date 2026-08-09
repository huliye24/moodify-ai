"""Candidate generation, scoring, and session re-ranking."""

from __future__ import annotations

from moodify.recommendation.models import AuditoryProfile, Track, UserTasteProfile
from moodify.recommendation.policy import RecommendationPolicy
from moodify.recommendation.rank import generate_candidates, rerank_for_session, score_candidates


def _tracks(count: int = 5) -> list[Track]:
    return [Track(track_id=f"t{i}", source_audio_id=f"src-{i}",
                  quality_state="ELIGIBLE") for i in range(count)]


def _profiles(tracks: list[Track]) -> dict[str, AuditoryProfile]:
    return {
        track.track_id: AuditoryProfile(
            auditory_profile_id=f"aud-{i}",
            track_id=track.track_id,
            feature_vector=(0.1 * i, 0.2 * i, 0.3 * i, 0.4 * i, 0.1, 0.1, 0.1),
            quality_confidence=0.7,
        )
        for i, track in enumerate(tracks)
    }


def _policy() -> RecommendationPolicy:
    return RecommendationPolicy.from_yaml()


def test_candidates_exclude_session_played():
    policy = _policy()
    tracks = _tracks(4)
    profiles = _profiles(tracks)
    taste = UserTasteProfile(user_id="u1")
    candidates = generate_candidates(tracks, profiles, taste, policy, session_played={"t0"})
    assert all(track_id != "t0" for track_id, _, _ in candidates)


def test_candidates_exclude_unavailable_and_bad_quality():
    policy = _policy()
    tracks = _tracks(4)
    tracks[1] = Track(track_id="t1", source_audio_id="s1", availability_state="UNAVAILABLE")
    tracks[2] = Track(track_id="t2", source_audio_id="s2", quality_state="SEVERE_ISSUES")
    profiles = _profiles(tracks)
    taste = UserTasteProfile(user_id="u1")
    candidates = generate_candidates(tracks, profiles, taste, policy)
    ids = {c[0] for c in candidates}
    assert "t1" not in ids and "t2" not in ids


def test_scoring_ranks_by_preference_match():
    policy = _policy()
    tracks = _tracks(4)
    profiles = _profiles(tracks)
    # User's combined taste equals t3's profile exactly.
    taste = UserTasteProfile(
        user_id="u1",
        long_term_vector=(0.3, 0.6, 0.9, 1.2, 0.1, 0.1, 0.1),
        short_term_vector=(0.3, 0.6, 0.9, 1.2, 0.1, 0.1, 0.1),
    )
    candidates = generate_candidates(tracks, profiles, taste, policy)
    scored = score_candidates(candidates, tracks, profiles, taste, policy)
    assert scored[0][0] == "t3"


def test_scoring_emits_explanation_tokens():
    policy = _policy()
    tracks = _tracks(3)
    profiles = _profiles(tracks)
    taste = UserTasteProfile(user_id="u1")
    candidates = generate_candidates(tracks, profiles, taste, policy)
    scored = score_candidates(candidates, tracks, profiles, taste, policy)
    track_id, score, tokens = scored[0]
    assert tokens and any(token.startswith("source:") for token in tokens)


def test_rerank_respects_size():
    scored = [
        (f"t{i}", float(10 - i), ["source:similarity"]) for i in range(8)
    ]
    selected = rerank_for_session(scored, size=3)
    assert len(selected) == 3
    assert selected[0][0] == "t0"


def test_exploration_candidates_present_in_pool():
    policy = _policy()
    tracks = _tracks(12)
    profiles = _profiles(tracks)
    taste = UserTasteProfile(user_id="u1", long_term_vector=(0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1))
    candidates = generate_candidates(tracks, profiles, taste, policy)
    sources = {source for _, source, _ in candidates}
    assert sources & {"similarity", "exploration"}
