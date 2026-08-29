"""Temporal event models (MFY-PHASE1-DEPTH-002).

A TemporalEvent is a deterministic, evidence-backed time-localized
observation of a narrow set of technical auditory phenomena. It never
claims musical meaning; every event references the measurement windows
and rules that produced it, and carries an honest localization
precision equal to the analysis hop (no fake sub-hop precision).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

P0_EVENT_TYPES = {
    "CLIPPING_CLUSTER",
    "NEAR_CLIPPING_CLUSTER",
    "SILENCE_GAP",
    "NEGATIVE_CORRELATION_REGION",
    "PHASE_RISK_REGION",
    "HIGH_FREQUENCY_DROPOUT",
    "LEVEL_SPIKE",
    "LEVEL_DROP",
}

FORBIDDEN_LABELS = {
    "BAD_CHORUS", "EMOTION_CHANGE", "VOCAL_PROBLEM", "WRONG_MASTERING",
    "BAD_MIX", "DROP_IS_TOO_WEAK", "INTRO_TOO_LONG",
}


@dataclass(frozen=True)
class WindowMeasurement:
    """One windowed observation from a temporal analysis domain."""

    domain: str
    window_index: int
    start_ms: int
    end_ms: int
    values: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WindowMeasurement":
        return cls(**data)


@dataclass(frozen=True)
class EventCandidate:
    """Pre-merge contiguous detection segment."""

    event_type: str
    window_indices: tuple[int, ...]
    domain: str
    peak_magnitude: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["window_indices"] = list(self.window_indices)
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EventCandidate":
        data = dict(data)
        data["window_indices"] = tuple(data.get("window_indices", ()))
        return cls(**data)


@dataclass(frozen=True)
class TemporalEvent:
    event_id: str
    event_type: str
    start_ms: int
    end_ms: int
    confidence: float
    status: str  # DETECTED | ESTIMATOR_DERIVED
    evidence_windows: tuple[int, ...]
    rules: tuple[str, ...]
    profile_id: str
    localization_precision_ms: int
    domain: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["evidence_windows"] = [f"W{w:05d}" for w in self.evidence_windows]
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TemporalEvent":
        data = dict(data)
        data["evidence_windows"] = tuple(
            int(w.replace("W", "")) for w in data.get("evidence_windows", ())
        )
        data["rules"] = tuple(data.get("rules", ()))
        return cls(**data)
