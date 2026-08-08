"""Pairwise Auditory Judge domain models (DSK-MFY-PAIRWISE-JUDGE-001).

A pairwise judgment compares two candidates under a shared context and
produces exactly one of A_WINS / B_WINS / INCONCLUSIVE, with confidence
bands, evidence-backed dimension results, and a human-decision overlay.
Machine-only judgments are never treated as ground truth.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class PairwiseCandidate:
    candidate_id: str
    pairwise_case_id: str
    label: str  # A | B
    source_audio_id: str
    source_hash: str
    analysis_run_id: str = ""
    analysis_dir: str = ""
    external_provider: str | None = None
    external_generation_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PairwiseCandidate":
        return cls(**data)


@dataclass(frozen=True)
class DimensionResult:
    dimension: str
    candidate_a_value: float | None
    candidate_b_value: float | None
    relative_result: str  # A_BETTER | B_BETTER | TIE | INSUFFICIENT_EVIDENCE
    confidence: float
    evidence_refs: tuple[str, ...] = ()
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DimensionResult":
        data = dict(data)
        data["evidence_refs"] = tuple(data.get("evidence_refs", ()))
        return cls(**data)


@dataclass(frozen=True)
class PairwiseComparison:
    comparison_id: str
    pairwise_case_id: str
    comparison_version: str
    dimension_results: tuple[DimensionResult, ...] = ()
    evidence_coverage: float = 0.0
    analysis_versions: dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=_iso_now)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["dimension_results"] = [d.to_dict() for d in self.dimension_results]
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PairwiseComparison":
        data = dict(data)
        data["dimension_results"] = tuple(
            DimensionResult.from_dict(d) for d in data.get("dimension_results", [])
        )
        return cls(**data)


@dataclass(frozen=True)
class PairwiseJudgment:
    judgment_id: str
    pairwise_case_id: str
    policy_version: str
    outcome: str  # A_WINS | B_WINS | INCONCLUSIVE
    confidence_level: str  # LOW | MEDIUM | HIGH
    winner_margin: float = 0.0
    evidence_coverage: float = 0.0
    top_reasons: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    created_at: str = field(default_factory=_iso_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PairwiseJudgment":
        data = dict(data)
        for key in ("top_reasons", "evidence_refs", "limitations"):
            data[key] = tuple(data.get(key, ()))
        return cls(**data)


@dataclass(frozen=True)
class HumanPairwiseDecision:
    human_decision_id: str
    pairwise_case_id: str
    decision: str  # CONFIRM_MODEL | CHOOSE_A | CHOOSE_B | UNDECIDED
    machine_outcome: str
    override_reason: str = ""
    created_at: str = field(default_factory=_iso_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HumanPairwiseDecision":
        return cls(**data)


@dataclass(frozen=True)
class PreferenceRecord:
    preference_record_id: str
    pairwise_case_id: str
    preferred_candidate: str | None  # A | B | None(undecided)
    label_source: str  # MACHINE_ONLY | HUMAN_CONFIRMED | HUMAN_OVERRIDE
    machine_outcome: str
    machine_confidence: str
    eligible_for_training: bool = False
    created_at: str = field(default_factory=_iso_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PreferenceRecord":
        return cls(**data)
