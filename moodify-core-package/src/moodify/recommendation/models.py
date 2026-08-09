"""Recommendation-layer domain models (DSK-MFY-TASTE-FEED-PATCH-001).

The feed layer consumes auditory representations and user feedback; it
never replaces the auditory core. Every feed request is traceable via
request_id + ranking_version, and every feedback event can link back to
the request and track.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class Track:
    track_id: str
    source_audio_id: str
    availability_state: str = "AVAILABLE"  # AVAILABLE | UNAVAILABLE | BLOCKED
    creator_id: str | None = None
    release_state: str = "RELEASED"
    metadata: dict[str, Any] = field(default_factory=dict)
    auditory_profile_id: str = ""
    quality_state: str = "UNVERIFIED"  # UNVERIFIED | ELIGIBLE | SEVERE_ISSUES

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Track":
        return cls(**data)


@dataclass(frozen=True)
class AuditoryProfile:
    auditory_profile_id: str
    track_id: str
    feature_vector: tuple[float, ...] = ()
    quality_confidence: float = 0.0
    derived_labels: tuple[str, ...] = ()
    version: str = "1.0"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["feature_vector"] = list(self.feature_vector)
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AuditoryProfile":
        data = dict(data)
        data["feature_vector"] = tuple(data.get("feature_vector", ()))
        data["derived_labels"] = tuple(data.get("derived_labels", ()))
        return cls(**data)


@dataclass(frozen=True)
class UserTasteProfile:
    user_id: str
    long_term_vector: tuple[float, ...] = ()
    short_term_vector: tuple[float, ...] = ()
    novelty_tolerance: float = 0.20
    model_version: str = "taste_v1"
    last_updated_at: str = field(default_factory=_iso_now)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["long_term_vector"] = list(self.long_term_vector)
        payload["short_term_vector"] = list(self.short_term_vector)
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserTasteProfile":
        data = dict(data)
        data["long_term_vector"] = tuple(data.get("long_term_vector", ()))
        data["short_term_vector"] = tuple(data.get("short_term_vector", ()))
        return cls(**data)


@dataclass(frozen=True)
class RecommendationRequest:
    request_id: str
    user_id: str
    surface: str = "for_you"
    ranking_version: str = "rec_v1"
    candidate_pool_size: int = 20
    context: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_iso_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RecommendationRequest":
        return cls(**data)


@dataclass(frozen=True)
class RecommendationCandidate:
    request_id: str
    track_id: str
    candidate_source: str = "similarity"
    final_rank: int = 0
    final_score: float = 0.0
    explanation_tokens: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["explanation_tokens"] = list(self.explanation_tokens)
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RecommendationCandidate":
        data = dict(data)
        data["explanation_tokens"] = tuple(data.get("explanation_tokens", ()))
        return cls(**data)


@dataclass(frozen=True)
class PlaybackSession:
    playback_session_id: str
    user_id: str
    request_id: str = ""
    session_start_at: str = field(default_factory=_iso_now)
    session_end_at: str | None = None
    device: str = ""
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PlaybackSession":
        return cls(**data)


@dataclass(frozen=True)
class FeedbackEvent:
    event_id: str
    user_id: str
    track_id: str
    event_type: str  # IMPRESSION | PLAY_START | PROGRESS | COMPLETION | SKIP | REPLAY | LIKE | SAVE | SESSION_END
    request_id: str = ""
    playback_session_id: str = ""
    rank_position: int | None = None
    elapsed_ms: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    occurred_at: str = field(default_factory=_iso_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FeedbackEvent":
        return cls(**data)


@dataclass(frozen=True)
class RecommendationOutcome:
    request_id: str
    user_id: str
    completion: bool = False
    skip: bool = False
    replay: bool = False
    save: bool = False
    session_depth_delta: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RecommendationOutcome":
        return cls(**data)
