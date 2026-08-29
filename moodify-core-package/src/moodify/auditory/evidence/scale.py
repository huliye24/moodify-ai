"""Evidence temporal-scale taxonomy (DSK-MFY-CH02-PHASE1-001, Chapter II §6).

A finding must know whether it arose from a 12 ms event, a 500 ms window,
an 8 s segment or a whole-track statistic. "The track is dynamically
dense" and "a 12 ms clip occurred at 01:43.822" are claims at different
evidential granularity and must not share one.

The chapter table overlaps (short-term 0.1-3 s vs musical unit 1-15 s);
this module resolves the overlap with a deterministic partition.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

EVIDENCE_SCALES = frozenset({
    "WAVEFORM_FINE",
    "MICRO_TRANSIENT",
    "PERCEPTUAL_FRAME",
    "SHORT_TERM",
    "MUSICAL_UNIT",
    "LONG_FORM",
    "WHOLE_TRACK",
})


@dataclass(frozen=True)
class EvidenceScale:
    scale: str

    def __post_init__(self) -> None:
        if self.scale not in EVIDENCE_SCALES:
            raise ValueError(f"unknown evidence scale: {self.scale}")

    def to_dict(self) -> dict[str, Any]:
        return {"scale": self.scale}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvidenceScale":
        return cls(scale=data["scale"])


def scale_for_duration_ms(duration_ms: float) -> str:
    """Map an event/window duration to its evidence scale.

    Deterministic partition of the chapter's overlapping table:
    <1ms waveform fine structure; 1-20ms micro-transient; 20-100ms
    perceptual frame; 0.1-1s short-term; 1-15s musical unit; >=15s
    long form. WHOLE_TRACK is applied to global summaries, not durations.
    """
    if duration_ms < 1.0:
        return "WAVEFORM_FINE"
    if duration_ms < 20.0:
        return "MICRO_TRANSIENT"
    if duration_ms < 100.0:
        return "PERCEPTUAL_FRAME"
    if duration_ms < 1000.0:
        return "SHORT_TERM"
    if duration_ms < 15000.0:
        return "MUSICAL_UNIT"
    return "LONG_FORM"
