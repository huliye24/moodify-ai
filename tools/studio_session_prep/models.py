"""Data models for studio session preparation.

All models use Pydantic v2. Units are explicit. Times are UTC ISO-8601.
Schema version is recorded in every serialized output.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator

SCHEMA_VERSION = "1.0.0"
TOOL_VERSION = "0.1.0"


class SampleRate(str, Enum):
    SR_44100 = "44100"
    SR_48000 = "48000"
    SR_96000 = "96000"
    SR_192000 = "192000"


class BitDepth(str, Enum):
    BD_16 = "16"
    BD_24 = "24"
    BD_32 = "32"


class FileFormat(str, Enum):
    WAV = "wav"
    FLAC = "flac"
    AIFF = "aiff"


class AssetRole(str, Enum):
    SOURCE_STEM = "source_stem"
    REFERENCE_MIX = "reference_mix"
    VOCAL_STEM = "vocal_stem"
    INSTRUMENTAL_STEM = "instrumental_stem"
    LYRIC_SHEET = "lyric_sheet"
    MIDI = "midi"
    SCORE = "score"
    SESSION_NOTE = "session_note"
    OTHER = "other"


class AssetKind(str, Enum):
    AUDIO = "audio"
    TEXT = "text"
    MIDI = "midi"
    OTHER = "other"


class SessionBrief(BaseModel, frozen=True):
    """Immutable session brief frozen before recording starts."""

    schema_version: str = Field(default=SCHEMA_VERSION, frozen=True)
    tool_version: str = Field(default=TOOL_VERSION, frozen=True)
    session_id: UUID = Field(default_factory=uuid4, frozen=True)
    project_title: str
    client_name: str
    engineer_name: str
    studio_location: str
    session_date: str  # YYYY-MM-DD
    genre: str = ""
    target_bpm: float | None = None
    target_key: str = ""  # e.g. "C minor"
    notes: str = ""
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        frozen=True,
    )


class RecordingSpec(BaseModel, frozen=True):
    """Technical recording specification."""

    sample_rate: SampleRate = SampleRate.SR_48000
    bit_depth: BitDepth = BitDepth.BD_24
    file_format: FileFormat = FileFormat.WAV
    target_peak_dbfs: float = Field(default=-6.0, ge=-20.0, le=0.0)
    channel_count: int = Field(default=2, ge=1, le=32)
    naming_template: str = "{session_id}_T{take:03d}_{role}.wav"


class BackupTarget(BaseModel, frozen=True):
    """A backup destination path."""

    label: str
    path: str  # absolute or relative to session

    @field_validator("path")
    @classmethod
    def path_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Backup path must not be empty")
        return v


class DeliverableContract(BaseModel, frozen=True):
    """What will be delivered and in what format."""

    deliverables: list[str] = Field(default_factory=lambda: [
        "Raw takes (WAV, as recorded)",
        "Session notes (Markdown)",
        "Technical report (Markdown + HTML)",
    ])
    sample_rate_delivery: SampleRate = SampleRate.SR_48000
    bit_depth_delivery: BitDepth = BitDepth.BD_24
    loudness_target_lufs: float | None = None  # null = no loudness spec
    true_peak_limit_dbtp: float | None = None
    include_wse_report: bool = True
    include_candidate_plans: bool = False
    revision_policy: str = "Changes after contract freeze require written approval."


class AssetEntry(BaseModel):
    """A single asset registered in the session manifest."""

    asset_id: UUID = Field(default_factory=uuid4, frozen=True)
    role: AssetRole
    kind: AssetKind
    filename: str
    local_path: str = ""  # populated at verify time
    sha256: str | None = None
    file_size_bytes: int | None = None
    sample_rate: int | None = None
    channels: int | None = None
    duration_s: float | None = None
    frame_count: int | None = None
    decode_error: str | None = None
    verified_at: str | None = None
    notes: str = ""

    def verified(self) -> bool:
        return self.sha256 is not None and self.decode_error is None

    def to_summary(self) -> dict[str, Any]:
        return {
            "asset_id": str(self.asset_id),
            "role": self.role.value,
            "kind": self.kind.value,
            "filename": self.filename,
            "sha256": self.sha256,
            "file_size_bytes": self.file_size_bytes,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "duration_s": self.duration_s,
            "verified": self.verified(),
            "decode_error": self.decode_error,
        }


class SessionManifest(BaseModel):
    """Top-level session manifest written to session directory."""

    schema_version: str = Field(default=SCHEMA_VERSION, frozen=True)
    tool_version: str = Field(default=TOOL_VERSION, frozen=True)
    manifest_id: UUID = Field(default_factory=uuid4, frozen=True)
    session_brief: SessionBrief
    recording_spec: RecordingSpec
    backup_targets: list[BackupTarget] = Field(default_factory=list)
    deliverable_contract: DeliverableContract = Field(default_factory=DeliverableContract)
    assets: list[AssetEntry] = Field(default_factory=list)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        frozen=True,
    )

    def add_asset(self, entry: AssetEntry) -> None:
        self.assets.append(entry)

    def find_asset(self, filename: str) -> AssetEntry | None:
        for a in self.assets:
            if a.filename == filename:
                return a
        return None
