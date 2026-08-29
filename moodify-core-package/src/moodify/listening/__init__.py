"""Preregistered blind listening validation (MFY_MOBILE_LISTENING_VALIDATION_001).

Machine owns randomisation, playback consistency, recording, dedup, statistics
and evidence. Human owns preference and identity judgment. The protocol,
samples and endpoints are frozen and hashed BEFORE any listening session.
DeepSeek never fills in human judgments.

The listening engine is fully implemented and self-tested; human judgment data
is left PENDING (per user instruction, human listening sessions are skipped in
this package) and is never fabricated.
"""

from moodify.listening.blinding import build_sessions, randomize_assignment
from moodify.listening.loudness_match import verify_level_match
from moodify.listening.protocol import (
    PROTOCOL_VERSION,
    ListeningProtocol,
    build_default_protocol,
    freeze_protocol,
    hash_protocol,
    protocol_to_json,
)
from moodify.listening.session_store import SessionRecord, record_session
from moodify.listening.stats import (
    analyze_three_endpoints,
    binomial_ci,
    cohens_h,
    preference_test,
)

__all__ = [
    "PROTOCOL_VERSION",
    "ListeningProtocol",
    "SessionRecord",
    "analyze_three_endpoints",
    "binomial_ci",
    "build_default_protocol",
    "build_sessions",
    "cohens_h",
    "freeze_protocol",
    "hash_protocol",
    "preference_test",
    "protocol_to_json",
    "randomize_assignment",
    "record_session",
    "verify_level_match",
]
