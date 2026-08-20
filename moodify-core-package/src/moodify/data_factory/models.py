"""Data-factory-local records for intervention planning and human preference."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


DATA_PROTOCOL_VERSION = "MFY-DATA-PROTOCOL-001"
PLAN_GENERATOR_VERSION = "MFY-ABC-HEURISTIC-001"


@dataclass(frozen=True)
class InterventionPlan:
    case_id: str
    plan_id: str
    candidate_label: str
    candidate_id: str
    strategy: str
    intensity: float
    source_sha256: str
    scan_profile_id: str
    scan_profile_hash: str
    plan_generator_version: str
    params: dict[str, float]
    # Structured goals/guardrails follow the live auditory judgment contract
    # (moodify.auditory.judgment.evaluate_processing_plan).
    technical_goals: tuple[dict[str, Any], ...] = ()
    guardrails: tuple[dict[str, Any], ...] = ()
    # Human-readable summaries kept for review tooling.
    goals: tuple[str, ...] = ()
    rationale: tuple[str, ...] = ()
    human_listening_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class InterventionResult:
    candidate_label: str
    candidate_id: str
    output_path: str
    output_sha256: str
    sample_rate: int
    frames: int
    channels: int
    params: dict[str, float]
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HumanReview:
    case_id: str
    ranking: list[str] = field(default_factory=list)
    rejected: list[str] = field(default_factory=list)
    reviewer_id: str = ""
    notes: str = ""
    completed_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
