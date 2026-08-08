"""Per-stem transcription profiles."""
from __future__ import annotations

from dataclasses import dataclass

from .stems import StemKind


@dataclass(frozen=True)
class StemProfile:
    kind: StemKind
    min_frequency_hz: float | None = None
    max_frequency_hz: float | None = None
    onset_threshold: float = 0.5
    frame_threshold: float = 0.3
    minimum_note_length_ms: float = 127.7
    multiple_pitch_bends: bool = False
    melodia_trick: bool = True
    description: str = ""


PROFILES: dict[StemKind, StemProfile] = {
    StemKind.VOCALS: StemProfile(
        kind=StemKind.VOCALS,
        min_frequency_hz=80.0,
        max_frequency_hz=1200.0,
        onset_threshold=0.5,
        frame_threshold=0.25,
        minimum_note_length_ms=80.0,
        multiple_pitch_bends=True,
        melodia_trick=False,
        description="Melody-focused vocal profile with pitch bend support.",
    ),
    StemKind.BASS: StemProfile(
        kind=StemKind.BASS,
        min_frequency_hz=30.0,
        max_frequency_hz=500.0,
        onset_threshold=0.6,
        frame_threshold=0.35,
        minimum_note_length_ms=60.0,
        multiple_pitch_bends=False,
        melodia_trick=True,
        description="Bass profile: sub-bass to low-mid, tighter onset for pluck detection.",
    ),
    StemKind.PIANO: StemProfile(
        kind=StemKind.PIANO,
        min_frequency_hz=27.5,
        max_frequency_hz=4200.0,
        onset_threshold=0.45,
        frame_threshold=0.3,
        minimum_note_length_ms=40.0,
        multiple_pitch_bends=False,
        melodia_trick=True,
        description="Wide-range polyphonic piano profile.",
    ),
    StemKind.GUITAR: StemProfile(
        kind=StemKind.GUITAR,
        min_frequency_hz=60.0,
        max_frequency_hz=2500.0,
        onset_threshold=0.5,
        frame_threshold=0.3,
        minimum_note_length_ms=50.0,
        multiple_pitch_bends=False,
        melodia_trick=True,
        description="Guitar profile: mid-frequency focus, polyphonic.",
    ),
    StemKind.OTHER: StemProfile(
        kind=StemKind.OTHER,
        onset_threshold=0.5,
        frame_threshold=0.3,
        minimum_note_length_ms=127.7,
        multiple_pitch_bends=False,
        melodia_trick=True,
        description="Neutral profile for unknown/other instruments. No range constraints.",
    ),
}


def get_profile(kind: StemKind) -> StemProfile:
    """Return the profile for a given stem kind. Unknown kinds get the OTHER profile."""
    return PROFILES.get(kind, PROFILES[StemKind.OTHER])
