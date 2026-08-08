"""MoodifyScore v0.1 internal model — strict typed, versioned schema.

Contract: `docs/tasks/deepseek/DSK-MFY-SCORE-ENGINE-009/MOODIFYSCORE_CONTRACT.md`
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

SCHEMA_VERSION = "moodifyscore/0.1"

EventStatus = Literal["raw", "inferred", "confirmed"]
EventType = Literal["note", "rest"]


@dataclass(frozen=True)
class TempoEntry:
    tick: int
    bpm: float


@dataclass(frozen=True)
class TimeSignatureEntry:
    tick: int
    numerator: int
    denominator: int


@dataclass(frozen=True)
class KeyEntry:
    tick: int
    fifths: int
    mode: Literal["major", "minor"]


@dataclass(frozen=True)
class Timeline:
    tempo_map: tuple[TempoEntry, ...] = ()
    time_signature_map: tuple[TimeSignatureEntry, ...] = ()
    key_map: tuple[KeyEntry, ...] = ()
    tempo_known: bool = False
    time_signature_known: bool = False
    key_known: bool = False


@dataclass(frozen=True)
class SourceAsset:
    kind: str
    path: str
    sha256: str
    role: str


@dataclass(frozen=True)
class ScoreMetadata:
    title: str = ""
    composer: str | None = None
    lyrics: str | None = None
    language: str | None = None
    comments: str | None = None
    source_label: str | None = None


@dataclass(frozen=True)
class Event:
    event_id: str
    event_type: EventType
    tick_start: int
    tick_end: int
    pitch_midi: int | None = None
    velocity: int | None = None
    measure_index: int | None = None
    position_in_measure: int | None = None
    ties: tuple[str, ...] = ()
    source: str = "midi_ingest"
    status: EventStatus = "raw"
    confidence: float | None = None
    inference_notes: tuple[str, ...] = ()

    def duration_ticks(self) -> int:
        return self.tick_end - self.tick_start


@dataclass(frozen=True)
class Voice:
    voice_id: str
    events: tuple[Event, ...]


@dataclass(frozen=True)
class Staff:
    staff_id: str
    clef: str | None = None
    voices: tuple[Voice, ...] = ()


@dataclass(frozen=True)
class Part:
    part_id: str
    name: str
    instrument: str | None = None
    channel: int | None = None
    program: int | None = None
    source_track: int | None = None
    staves: tuple[Staff, ...] = ()


@dataclass(frozen=True)
class MoodifyScore:
    schema_version: str
    score_id: str
    revision: int
    metadata: ScoreMetadata
    source_assets: tuple[SourceAsset, ...]
    timeline: Timeline
    parts: tuple[Part, ...]
    revision_note: str = ""
    lyrics_references: tuple[dict, ...] = ()
    evidence: dict = field(default_factory=dict)
