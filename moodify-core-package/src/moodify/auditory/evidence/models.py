"""Evidence graph models (MFY-PHASE1-DEPTH-004).

A lightweight, deterministic evidence graph: JUDGMENT -> EVENT/WINDOW ->
MEASUREMENT -> PROFILE -> SOURCE -> RULE. No graph database; the graph
is a resolvable lineage structure. Judgment separates classification
from evidence state from workflow decision; uncertainty reasons are
bounded; coverage states which domains were actually evaluated.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

NODE_KINDS = {"SOURCE", "PROFILE", "MEASUREMENT", "WINDOW", "EVENT", "RULE", "JUDGMENT"}

EVIDENCE_STATES = {
    "SUPPORTED", "PARTIAL", "INSUFFICIENT", "CONFLICTING", "NOT_APPLICABLE", "INVALID",
}

CLASSIFICATIONS = {
    "TECHNICAL_RISK", "LIKELY_ARTIFACT", "INFORMATIONAL", "NO_MEASURED_RISK", "UNCERTAIN",
}

WORKFLOW_DECISIONS = {"PASS_TO_LISTENING", "REJECT_TECHNICAL", "INCONCLUSIVE", "REVIEW_REQUIRED"}

COVERAGE_DOMAINS = ("integrity", "level", "spectrum", "stereo", "global")


@dataclass(frozen=True)
class EvidenceNode:
    node_id: str
    kind: str  # SOURCE | PROFILE | MEASUREMENT | WINDOW | EVENT | RULE | JUDGMENT
    ref: str
    data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.kind not in NODE_KINDS:
            raise ValueError(f"unknown node kind: {self.kind}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvidenceNode":
        return cls(**data)


@dataclass(frozen=True)
class Coverage:
    evaluated_domains: tuple[str, ...]
    unevaluated_domains: tuple[str, ...]
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Coverage":
        return cls(
            evaluated_domains=tuple(data["evaluated_domains"]),
            unevaluated_domains=tuple(data["unevaluated_domains"]),
            notes=data.get("notes", ""),
        )


@dataclass(frozen=True)
class Conflict:
    conflict_type: str  # STATUS | VERSION | SOURCE_LINEAGE | PROFILE | RULE | DUPLICATE_AUTHORITY
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Conflict":
        return cls(**data)


@dataclass(frozen=True)
class JudgmentEvidence:
    judgment_id: str
    classification: str
    evidence_state: str
    workflow_decision: str
    nodes: tuple[EvidenceNode, ...]
    uncertainties: tuple[Any, ...] = ()  # Uncertainty
    conflicts: tuple[Conflict, ...] = ()
    coverage: Coverage | None = None
    rule_versions: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from moodify.auditory.uncertainty import Uncertainty

        return {
            "judgment_id": self.judgment_id,
            "classification": self.classification,
            "evidence_state": self.evidence_state,
            "workflow_decision": self.workflow_decision,
            "nodes": [node.to_dict() for node in self.nodes],
            "uncertainties": [
                u.to_dict() if isinstance(u, Uncertainty) else dict(u)
                for u in self.uncertainties
            ],
            "conflicts": [conflict.to_dict() for conflict in self.conflicts],
            "coverage": self.coverage.to_dict() if self.coverage else None,
            "rule_versions": dict(self.rule_versions),
        }
