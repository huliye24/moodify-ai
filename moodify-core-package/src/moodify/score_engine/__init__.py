"""Moodify Score Engine — internal score model and backend adapters.

MoodifyScore is the internal source of truth for score semantics, provenance,
confidence, revision and backend evidence. External engines only render.
"""

from moodify.score_engine.model import (
    Event,
    KeyEntry,
    MoodifyScore,
    Part,
    ScoreMetadata,
    SourceAsset,
    Staff,
    TempoEntry,
    TimeSignatureEntry,
    Timeline,
    Voice,
)

__all__ = [
    "Event",
    "KeyEntry",
    "MoodifyScore",
    "Part",
    "ScoreMetadata",
    "SourceAsset",
    "Staff",
    "TempoEntry",
    "TimeSignatureEntry",
    "Timeline",
    "Voice",
]
