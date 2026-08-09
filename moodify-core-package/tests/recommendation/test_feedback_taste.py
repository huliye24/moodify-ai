"""Feedback events, derived signals, and taste updates."""

from __future__ import annotations

from moodify.recommendation.feedback import derive_signal, new_event
from moodify.recommendation.policy import RecommendationPolicy
from moodify.recommendation.taste import apply_signal


def _policy() -> RecommendationPolicy:
    return RecommendationPolicy.from_yaml()


def test_derive_hard_skip_by_time():
    assert derive_signal("SKIP", elapsed_ms=2_000) == "SKIP_HARD"


def test_derive_hard_skip_by_fraction():
    assert derive_signal("SKIP", elapsed_ms=20_000, duration_ms=100_000) == "SKIP_HARD"


def test_derive_soft_skip():
    assert derive_signal("SKIP", elapsed_ms=60_000, duration_ms=100_000) == "SKIP_SOFT"


def test_derive_completion_passthrough():
    assert derive_signal("COMPLETION") == "COMPLETION"
    assert derive_signal("REPLAY") == "REPLAY"
    assert derive_signal("SAVE") == "SAVE"


def test_new_event_rejects_unknown_type():
    import pytest

    with pytest.raises(ValueError):
        new_event("u1", "t1", "NOT_A_TYPE")


def test_positive_signal_moves_taste_toward_track():
    from moodify.recommendation.models import UserTasteProfile

    profile = UserTasteProfile(user_id="u1")
    updated = apply_signal(profile, "COMPLETION", (0.5, 0.25, 0.1), _policy())
    assert updated.long_term_vector[0] > 0.0
    assert updated.long_term_vector[1] > 0.0
    assert updated.long_term_vector[0] < 0.5  # alpha-scaled, not full jump


def test_negative_signal_moves_taste_away():
    from moodify.recommendation.models import UserTasteProfile

    profile = UserTasteProfile(user_id="u1")
    updated = apply_signal(profile, "SKIP_HARD", (0.5, 0.25, 0.1), _policy())
    assert updated.long_term_vector[0] < 0.0


def test_hard_skip_raises_novelty_tolerance():
    from moodify.recommendation.models import UserTasteProfile

    policy = _policy()
    profile = UserTasteProfile(user_id="u1", novelty_tolerance=0.20)
    updated = apply_signal(profile, "SKIP_HARD", (0.1,), policy)
    assert updated.novelty_tolerance == 0.25


def test_completion_lowers_novelty_tolerance():
    from moodify.recommendation.models import UserTasteProfile

    policy = _policy()
    profile = UserTasteProfile(user_id="u1", novelty_tolerance=0.30)
    updated = apply_signal(profile, "COMPLETION", (0.1,), policy)
    assert updated.novelty_tolerance == 0.25  # one step down, floored at start value
