"""User taste profile updates (DSK-MFY-TASTE-FEED-PATCH-001).

Long-term taste moves slowly (low alpha); short-term session taste moves
fast (high alpha). Each derived signal nudges the taste vector toward
(or away from) the track's auditory feature vector, weighted by policy.
Novelty tolerance rises after skips and falls after sustained listening.
"""

from __future__ import annotations

from moodify.recommendation.models import UserTasteProfile
from moodify.recommendation.policy import RecommendationPolicy


def _lerp(current: tuple[float, ...], target: tuple[float, ...], alpha: float) -> tuple[float, ...]:
    size = max(len(current), len(target))
    padded_current = tuple(current) + (0.0,) * (size - len(current))
    padded_target = tuple(target) + (0.0,) * (size - len(target))
    return tuple(round(c + alpha * (t - c), 6) for c, t in zip(padded_current, padded_target))


def apply_signal(
    profile: UserTasteProfile,
    signal: str,
    track_vector: tuple[float, ...],
    policy: RecommendationPolicy,
) -> UserTasteProfile:
    """Update taste from one derived feedback signal."""
    weight = policy.feedback_weights.get(signal, 0.0)
    if weight == 0.0:
        return profile
    direction = 1.0 if weight > 0 else -1.0
    magnitude = abs(weight)
    # Strong signals move the vector more; alpha scales with magnitude.
    long_alpha = policy.long_term_alpha * magnitude
    short_alpha = policy.short_term_alpha * magnitude
    target = tuple(v * direction for v in track_vector)
    novelty = profile.novelty_tolerance
    if signal == "SKIP_HARD":
        novelty = min(policy.novelty_tolerance_max,
                      novelty + policy.novelty_tolerance_step)
    elif signal in {"COMPLETION", "REPLAY", "SAVE", "LIKE"}:
        novelty = max(policy.novelty_tolerance_start,
                      novelty - policy.novelty_tolerance_step)
    return UserTasteProfile(
        user_id=profile.user_id,
        long_term_vector=_lerp(profile.long_term_vector, target, long_alpha),
        short_term_vector=_lerp(profile.short_term_vector, target, short_alpha),
        novelty_tolerance=round(novelty, 6),
        model_version=profile.model_version,
    )


def merge_taste(profile: UserTasteProfile, policy: RecommendationPolicy) -> tuple[float, ...]:
    """Combined preference vector used for scoring."""
    long_vector = profile.long_term_vector or ()
    short_vector = profile.short_term_vector or ()
    size = max(len(long_vector), len(short_vector))
    padded_long = long_vector + (0.0,) * (size - len(long_vector))
    padded_short = short_vector + (0.0,) * (size - len(short_vector))
    return tuple(
        round(0.7 * long_part + 0.3 * short_part, 6)
        for long_part, short_part in zip(padded_long, padded_short)
    )
