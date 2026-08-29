"""Musical-structural evidence context (DSK-MFY-CH02-PHASE1-001, Chapter II §14).

MSE conditions WSE: the same acoustic event means different things at
different musical moments. A sudden energy increase at a chorus entrance
may be expected; the same increase mid-verse may indicate an artifact.

This module defines the structure context type and the annotation path.
It never changes workflow decisions by itself; it records structural
context onto evidence nodes, and falls back gracefully (records an
uncertainty, annotates nothing) when structural confidence is low.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

STRUCTURE_CONFIDENCE_THRESHOLD = 0.8


@dataclass(frozen=True)
class Section:
    label: str
    start_s: float
    end_s: float
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if self.end_s < self.start_s:
            raise ValueError(f"section ends before it starts: {self.label}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"section confidence out of range: {self.label}")


@dataclass(frozen=True)
class StructureContext:
    """Musical-structural evidence available to condition WSE judgments."""

    source: str
    sections: tuple[Section, ...] = ()
    tempo_bpm: float | None = None
    confidence: float | None = None

    def __post_init__(self) -> None:
        bounds = [s for s in self.sections if s.start_s >= 0.0]
        ordered = sorted(bounds, key=lambda s: s.start_s)
        for prev, cur in zip(ordered, ordered[1:]):
            if cur.start_s < prev.end_s:
                raise ValueError("sections overlap; must be non-overlapping")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("structure confidence out of range")

    def section_at(self, t: float) -> Section | None:
        for section in self.sections:
            if section.start_s <= t < section.end_s:
                return section
        return None

    def boundary_within(self, t: float, window_s: float = 0.5) -> bool:
        """True when t lies within window_s of a section boundary."""
        edges = [s.start_s for s in self.sections if s.start_s > 0.0]
        edges += [s.end_s for s in self.sections]
        return any(abs(t - edge) <= window_s for edge in edges)

    @property
    def is_reliable(self) -> bool:
        if self.confidence is not None and self.confidence < STRUCTURE_CONFIDENCE_THRESHOLD:
            return False
        return all(s.confidence >= STRUCTURE_CONFIDENCE_THRESHOLD for s in self.sections)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "sections": [vars(s) for s in self.sections],
            "tempo_bpm": self.tempo_bpm,
            "confidence": self.confidence,
        }


def annotate_event_with_structure(event: Any, structure: StructureContext) -> dict[str, str]:
    """Structural annotation for one event (label + boundary flag + confidence).

    Annotates only when the structure is reliable; the caller decides
    whether the event qualifies for conditioning.
    """
    start_s = getattr(event, "start_ms", 0) / 1000.0
    section = structure.section_at(start_s)
    annotation: dict[str, str] = {"structure_source": structure.source}
    if section is None:
        return annotation
    annotation["structure_label"] = section.label
    annotation["section_confidence"] = f"{section.confidence:.3f}"
    annotation["at_section_boundary"] = "true" if structure.boundary_within(start_s) else "false"
    return annotation
