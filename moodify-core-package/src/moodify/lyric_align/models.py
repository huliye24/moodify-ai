from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class WordTiming:
    text: str
    start: float
    end: float
    confidence: float
    normalized_text: str | None = None


@dataclass(frozen=True)
class LineTiming:
    index: int
    text: str
    start: float
    end: float
    confidence: float
    words: tuple[WordTiming, ...] = ()
    translation: str | None = None


@dataclass(frozen=True)
class AlignmentResult:
    backend: str
    backend_version: str
    language: str
    audio_path: str
    audio_duration: float
    status: str
    lines: tuple[LineTiming, ...]
    warnings: tuple[str, ...] = ()
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
