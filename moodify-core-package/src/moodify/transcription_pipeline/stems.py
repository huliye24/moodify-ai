"""Stem kind enumeration and stem manifest."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class StemKind(str, Enum):
    VOCALS = "vocals"
    BASS = "bass"
    PIANO = "piano"
    GUITAR = "guitar"
    OTHER = "other"
    DRUMS = "drums"
    UNKNOWN = "unknown"


TRANSCRIBABLE_KINDS = frozenset({
    StemKind.VOCALS, StemKind.BASS, StemKind.PIANO,
    StemKind.GUITAR, StemKind.OTHER,
})

UNSUPPORTED_KINDS = frozenset({StemKind.DRUMS, StemKind.UNKNOWN})


@dataclass
class StemEntry:
    kind: StemKind
    path: Path
    source_hash: str = ""

    def validate(self) -> None:
        if ".." in self.path.parts:
            raise ValueError(f"Path traversal rejected: {self.path}")
        if not self.path.is_file():
            raise FileNotFoundError(f"Stem file not found: {self.path}")


@dataclass
class StemManifest:
    stems: list[StemEntry] = field(default_factory=list)

    def validate(self) -> None:
        if not self.stems:
            raise ValueError("Stem manifest must contain at least one stem")
        kinds = [s.kind for s in self.stems]
        if len(kinds) != len(set(kinds)):
            raise ValueError("Duplicate stem kinds in manifest")
        for stem in self.stems:
            stem.validate()

    @classmethod
    def from_cli_pairs(cls, pairs: list[tuple[str, str]]) -> StemManifest:
        stems = []
        for kind_str, path_str in pairs:
            try:
                kind = StemKind(kind_str.lower())
            except ValueError:
                raise ValueError(f"Unknown stem kind: {kind_str}")
            stems.append(StemEntry(kind=kind, path=Path(path_str).resolve()))
        return cls(stems=stems)
