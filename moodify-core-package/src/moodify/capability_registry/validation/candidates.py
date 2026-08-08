"""Candidate generation and selection.

Multiple providers or parameter variants produce candidates for the same
capability. Each candidate binds its own approved envelope (019 immutability).
All candidates — including rejected ones with structured reasons — are
retained (negative knowledge). Fallback only follows declared registry paths.
"""

from __future__ import annotations

from dataclasses import dataclass

from moodify.capability_registry.execution.envelope import ApprovedExecutionEnvelope, ExecutionRecord
from moodify.capability_registry.validation.rules import ValidationReport


@dataclass(frozen=True)
class RejectionReason:
    rule_id: str
    measured: object
    expected: object
    message: str

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "measured": self.measured,
            "expected": self.expected,
            "message": self.message,
        }


@dataclass(frozen=True)
class CandidateSpec:
    """A planned candidate: envelope draft + parameter variant description."""

    label: str
    provider_id: str
    parameters: dict
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "provider_id": self.provider_id,
            "parameters": self.parameters,
            "description": self.description,
        }


@dataclass(frozen=True)
class Candidate:
    spec: CandidateSpec
    envelope: ApprovedExecutionEnvelope | None
    record: ExecutionRecord | None
    validation: ValidationReport | None
    reasons: tuple[RejectionReason, ...] = ()

    @property
    def accepted(self) -> bool:
        if self.record is None or self.record.status != "completed":
            return False
        if self.validation is None:
            return True
        return self.validation.passed()

    def to_dict(self) -> dict:
        return {
            "spec": self.spec.to_dict(),
            "accepted": self.accepted,
            "record_status": self.record.status if self.record else None,
            "validation_passed": self.validation.passed() if self.validation else None,
            "reasons": [r.to_dict() for r in self.reasons],
        }


class CandidateRanker:
    """Stable ranking: accepted first (validation errors block), then by score."""

    def __init__(self, weights: dict | None = None) -> None:
        self.weights = weights or {"accepted": 100, "completed": 10}

    def score(self, candidate: Candidate) -> float:
        score = 0.0
        if candidate.accepted:
            score += self.weights.get("accepted", 100)
        elif candidate.record and candidate.record.status == "completed":
            score += self.weights.get("completed", 10)
        return score

    def rank(self, candidates: list[Candidate]) -> list[Candidate]:
        return sorted(candidates, key=self.score, reverse=True)


def reasons_from_validation(report: ValidationReport) -> tuple[RejectionReason, ...]:
    reasons: list[RejectionReason] = []
    for result in report.errors():
        reasons.append(
            RejectionReason(
                rule_id=result.rule_id,
                measured=result.measured,
                expected=result.expected,
                message=result.message,
            )
        )
    return tuple(reasons)
