"""Reconstruction outcome taxonomy (MFY-CR-P07)."""

from __future__ import annotations

OUTCOME_TAXONOMY = (
    "GOLDEN",              # clear improvement, stable preference, identity safe
    "IMPROVED",            # stable improvement, not yet Golden
    "SUBTLE_IMPROVEMENT",  # change exists but user value weak
    "SOURCE_WINS",         # original is best (a valid, healthy outcome)
    "HUMAN_REQUIRED",      # machine cannot decide safely
    "STEM_RECOMMENDED",    # stereo-first reached capability boundary
    "UNSUPPORTED",         # intervention engine cannot do what is needed
    "FAILED",              # engineering failure
)


def classify_outcome(
    improvement_noticeable: bool,
    human_preferred: bool | None,
    identity_safe: bool | None,
    engineering_ok: bool = True,
    stem_boundary: bool = False,
) -> str:
    """Deterministic outcome classification from machine + human signals.

    None means the signal is missing (e.g. human review skipped) — the
    classifier never guesses a human preference.
    """
    if not engineering_ok:
        return "FAILED"
    if stem_boundary:
        return "STEM_RECOMMENDED"
    if human_preferred is None or identity_safe is None:
        return "HUMAN_REQUIRED"
    if not human_preferred:
        return "SOURCE_WINS"
    if not identity_safe:
        return "HUMAN_REQUIRED"
    if not improvement_noticeable:
        return "SUBTLE_IMPROVEMENT"
    # stable preference across repeated sessions is required for GOLDEN;
    # a single preference without repetition evidence stays IMPROVED
    return "IMPROVED"
