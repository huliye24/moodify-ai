"""Auditory scan data models (DSK-MFY-AUDITORY-SCAN-001)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class FileProbe:
    filename: str
    absolute_path: str
    sha256: str
    duration_seconds: float
    container: str
    codec: str
    sample_rate: int
    bit_depth: int | None
    channels: int
    channel_layout: str
    file_size_bytes: int


@dataclass
class MetricValue:
    value: float | None
    unit: str
    method: str | None = None
    status: str = "VALID"  # VALID | UNAVAILABLE | WARN
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "unit": self.unit,
            "method": self.method,
            "status": self.status,
            "warnings": self.warnings,
        }


@dataclass
class Candidate:
    case_id: str
    candidate_id: str
    source_case_id: str
    candidate_path: str
    candidate_sha256: str
    created_at: str
    producing_application: str
    producing_application_version: str | None
    processing_operator: str
    processing_method: str
    processing_notes: str
    parent_source_sha256: str

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "candidate_id": self.candidate_id,
            "source_case_id": self.source_case_id,
            "candidate_path": self.candidate_path,
            "candidate_sha256": self.candidate_sha256,
            "created_at": self.created_at,
            "producing_application": self.producing_application,
            "producing_application_version": self.producing_application_version,
            "processing_operator": self.processing_operator,
            "processing_method": self.processing_method,
            "processing_notes": self.processing_notes,
            "parent_source_sha256": self.parent_source_sha256,
        }


@dataclass
class RiskFlag:
    code: str
    severity: str  # INFO | WARNING | BLOCKING
    message: str
    metric: str | None = None
    before: float | None = None
    after: float | None = None
    threshold: float | None = None

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "metric": self.metric,
            "before": self.before,
            "after": self.after,
            "threshold": self.threshold,
        }


@dataclass
class Judgment:
    technical_assessment: str  # IMPROVED | NEUTRAL | DEGRADED | UNCERTAIN | INVALID_COMPARISON
    workflow_decision: str  # PASS_TO_LISTENING | NEEDS_REWORK | REJECT_TECHNICAL | INCONCLUSIVE | INVALID
    reasons: list[str] = field(default_factory=list)
    goals_met: list[str] = field(default_factory=list)
    guardrail_failures: list[str] = field(default_factory=list)
    risk_flags: list[RiskFlag] = field(default_factory=list)
    human_listening_required: bool = True
    artistic_approval_granted: bool = False

    def to_dict(self) -> dict:
        return {
            "technical_assessment": self.technical_assessment,
            "workflow_decision": self.workflow_decision,
            "reasons": self.reasons,
            "goals_met": self.goals_met,
            "guardrail_failures": self.guardrail_failures,
            "risk_flags": [f.to_dict() for f in self.risk_flags],
            "human_listening_required": self.human_listening_required,
            "artistic_approval_granted": self.artistic_approval_granted,
        }
