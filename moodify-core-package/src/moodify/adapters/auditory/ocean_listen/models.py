from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class GateIssue:
    code: str
    severity: str
    message: str
    path: str | None = None


@dataclass
class GateResult:
    verdict: str
    issues: list[GateIssue] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "issues": [asdict(issue) for issue in self.issues],
            "metrics": self.metrics,
        }


@dataclass
class OceanExecution:
    run_id: str
    run_dir: str
    report_path: str
    stdout_path: str
    stderr_path: str
    command: list[str]
    return_code: int
    elapsed_seconds: float
    upstream_commit: str | None


@dataclass
class EvidenceArtifact:
    artifact_type: str
    path: str
    sha256: str
    media_type: str
    role: str


@dataclass
class AuditoryObservation:
    schema_version: str
    observation_id: str
    run_id: str
    created_at: str
    source: dict[str, Any]
    analyzer: dict[str, Any]
    classification: dict[str, Any]
    global_features: dict[str, Any]
    stems: dict[str, Any]
    notes: list[dict[str, Any]]
    voice: dict[str, Any]
    lyrics: dict[str, Any]
    timeline: list[dict[str, Any]]
    artifacts: list[dict[str, Any]]
    uncertainty: list[dict[str, Any]]
    provenance: dict[str, Any]
    quality_gate: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
