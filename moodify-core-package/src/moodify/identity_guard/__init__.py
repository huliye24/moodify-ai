"""Identity Guard v0.1 (MFY-CR-P05).

Answers one question per reconstruction candidate:

    does the candidate drift beyond the allowed identity boundary of the source?

It is multi-dimensional protection (no single identity score), with veto
semantics for critical dimensions, explicit PROXY vs MEASURABLE honesty, and
human review escalation. It never claims machine understanding of artistic
personality.
"""

from __future__ import annotations

from moodify.identity_guard.contract import (
    GuardState,
    IdentityDelta,
    IdentityDimension,
    IdentityVerdict,
    dimension_name,
)
from moodify.identity_guard.guard import guard_candidate
from moodify.identity_guard.ranking import CandidateRank, rank_candidates
from moodify.identity_guard.thresholds import IDENTITY_GUARD_POLICY_V1

__all__ = [
    "GuardState",
    "IdentityDelta",
    "IdentityDimension",
    "IdentityVerdict",
    "CandidateRank",
    "IDENTITY_GUARD_POLICY_V1",
    "dimension_name",
    "guard_candidate",
    "rank_candidates",
]

IDENTITY_GUARD_VERSION = "identity-guard-v0.1"
