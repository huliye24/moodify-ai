"""EraDiagnosticFinding contract (MFY-CR-P03).

A lightweight, versioned diagnostic object. It does NOT replace or duplicate
the canonical ProductionCase / EvidenceArtifact authority — it references
existing measurements by name and carries no processing authorization.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from moodify.auditory.uncertainty import UNCERTAINTY_REASONS

ERA_DIAGNOSTIC_VERSION = "era-diagnostic-v0.1"


class FindingStatus(str, Enum):
    """Diagnostic states. These describe the diagnosis only; none of them
    grants processing authority."""

    OBSERVED = "OBSERVED"
    POSSIBLE_TECHNICAL_LIMITATION = "POSSIBLE_TECHNICAL_LIMITATION"
    LIKELY_ARTISTIC_CHARACTER = "LIKELY_ARTISTIC_CHARACTER"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_SUPPORTED_IN_V0_1 = "NOT_SUPPORTED_IN_V0_1"


class ConfidenceLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class DiagnosticCategory(str, Enum):
    ED_01_BANDWIDTH_LIMITATION = "ED-01"
    ED_02_PERSISTENT_NOISE = "ED-02"
    ED_03_DYNAMIC_DAMAGE = "ED-03"
    ED_04_STEREO_PHASE_LIMITATION = "ED-04"
    ED_05_SPECTRAL_CONGESTION = "ED-05"
    ED_06_TRANSFER_ENCODING_DEGRADATION = "ED-06"


CATEGORY_DISPLAY_NAMES = {
    DiagnosticCategory.ED_01_BANDWIDTH_LIMITATION: "Bandwidth Limitation",
    DiagnosticCategory.ED_02_PERSISTENT_NOISE: "Persistent Noise Floor",
    DiagnosticCategory.ED_03_DYNAMIC_DAMAGE: "Dynamic Constraint / Damage",
    DiagnosticCategory.ED_04_STEREO_PHASE_LIMITATION: "Stereo / Phase Limitation",
    DiagnosticCategory.ED_05_SPECTRAL_CONGESTION: "Masking / Spectral Congestion",
    DiagnosticCategory.ED_06_TRANSFER_ENCODING_DEGRADATION: "Transfer / Encoding Degradation",
}


def category_name(category: DiagnosticCategory) -> str:
    return CATEGORY_DISPLAY_NAMES[category]


@dataclass(frozen=True)
class EraDiagnosticFinding:
    """One diagnostic conclusion for one category.

    - measurement_refs: names of the metrics that drove the conclusion.
    - evidence_refs: references to canonical Evidence artifacts (empty in v0.1;
      populated when integrated with the ProductionCase evidence flow).
    - known_ambiguities: honest alternatives (artistic interpretation, etc.).
    """

    category: DiagnosticCategory
    status: FindingStatus
    finding_id: str
    reasoning_summary: str
    measurement_refs: tuple[str, ...] = ()
    confidence: ConfidenceLevel | None = None
    known_ambiguities: tuple[str, ...] = ()
    scope: str = "era-diagnostic-v0.1"
    requires_human_review: bool = False
    production_case_id: str | None = None
    evidence_refs: tuple[str, ...] = ()
    uncertainty_reason: str | None = None
    created_at: str = ""
    version: str = ERA_DIAGNOSTIC_VERSION

    def __post_init__(self) -> None:
        if self.confidence is None and self.status in {
            FindingStatus.POSSIBLE_TECHNICAL_LIMITATION,
            FindingStatus.LIKELY_ARTISTIC_CHARACTER,
            FindingStatus.INSUFFICIENT_EVIDENCE,
        }:
            raise ValueError(f"{self.status} requires a confidence level")
        if self.confidence is not None and self.status in {
            FindingStatus.NOT_APPLICABLE,
            FindingStatus.NOT_SUPPORTED_IN_V0_1,
        }:
            raise ValueError(f"{self.status} cannot carry a confidence level")
        if self.uncertainty_reason is not None and self.uncertainty_reason not in UNCERTAINTY_REASONS:
            raise ValueError(f"unknown uncertainty reason: {self.uncertainty_reason!r}")
        if not self.measurement_refs:
            raise ValueError("measurement_refs must not be empty (evidence rule)")

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "production_case_id": self.production_case_id,
            "category": self.category.value,
            "category_name": category_name(self.category),
            "status": self.status.value,
            "confidence": self.confidence.value if self.confidence else None,
            "evidence_refs": list(self.evidence_refs),
            "measurement_refs": list(self.measurement_refs),
            "scope": self.scope,
            "reasoning_summary": self.reasoning_summary,
            "known_ambiguities": list(self.known_ambiguities),
            "requires_human_review": self.requires_human_review,
            "uncertainty_reason": self.uncertainty_reason,
            "created_at": self.created_at,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EraDiagnosticFinding":
        return cls(
            category=DiagnosticCategory(data["category"]),
            status=FindingStatus(data["status"]),
            finding_id=data["finding_id"],
            reasoning_summary=data["reasoning_summary"],
            measurement_refs=tuple(data["measurement_refs"]),
            confidence=ConfidenceLevel(data["confidence"]) if data.get("confidence") else None,
            known_ambiguities=tuple(data["known_ambiguities"]),
            scope=data.get("scope", "era-diagnostic-v0.1"),
            requires_human_review=data.get("requires_human_review", False),
            production_case_id=data.get("production_case_id"),
            evidence_refs=tuple(data.get("evidence_refs") or ()),
            uncertainty_reason=data.get("uncertainty_reason"),
            created_at=data.get("created_at", ""),
            version=data.get("version", ERA_DIAGNOSTIC_VERSION),
        )
