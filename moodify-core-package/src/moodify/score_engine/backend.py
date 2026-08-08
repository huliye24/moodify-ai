"""ScoreBackend protocol, capability bits and registry.

Backends render MoodifyScore through explicit capabilities. Unimplemented
backends only declare capability bits; they must never pretend to be usable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from moodify.score_engine.model import MoodifyScore


@dataclass(frozen=True)
class BackendCapabilities:
    musicxml_import: bool = False
    pdf_export: bool = False
    svg_export: bool = False
    png_export: bool = False
    audio_playback: bool = False
    human_editing: bool = False

    def to_dict(self) -> dict:
        return {
            "musicxml_import": self.musicxml_import,
            "pdf_export": self.pdf_export,
            "svg_export": self.svg_export,
            "png_export": self.png_export,
            "audio_playback": self.audio_playback,
            "human_editing": self.human_editing,
        }


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExportResult:
    status: str  # "success" | "failure" | "unavailable"
    artifacts: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    evidence: dict = field(default_factory=dict)


class ScoreBackend(Protocol):
    backend_id: str
    display_name: str
    license_label: str
    capabilities: BackendCapabilities

    def available(self) -> bool: ...

    def version(self) -> str | None: ...

    def validate(self, score: MoodifyScore) -> ValidationResult: ...

    def export(self, score: MoodifyScore, out_dir: Path) -> ExportResult: ...


# Unimplemented backends: capability bits only. `available()` is always False.
# They exist so the capability matrix and CLI listing are honest.
_UNIMPLEMENTED = {
    "verovio": BackendCapabilities(musicxml_import=True, svg_export=True),
    "lilypond": BackendCapabilities(musicxml_import=True, pdf_export=True),
    "osmd": BackendCapabilities(musicxml_import=True, svg_export=True),
}


@dataclass(frozen=True)
class BackendInfo:
    backend_id: str
    display_name: str
    license_label: str
    capabilities: BackendCapabilities
    implemented: bool
    available: bool = False
    version: str | None = None
    binary_path: str | None = None

    def to_dict(self) -> dict:
        return {
            "backend_id": self.backend_id,
            "display_name": self.display_name,
            "license_label": self.license_label,
            "capabilities": self.capabilities.to_dict(),
            "implemented": self.implemented,
            "available": self.available,
            "version": self.version,
            "binary_path": self.binary_path,
        }
