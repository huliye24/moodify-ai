"""GoldenReconstructionRecord (MFY-CR-P06 §20).

An evidence record, not a second ProductionCase authority. It references the
source hash and all versioned components; it never redefines case lifecycle.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

GOLDEN_PENDING = "PENDING_LISTENING"
GOLDEN_STATUSES = (
    "GOLDEN_CONFIRMED",
    "PROMISING_NOT_GOLDEN",
    "SOURCE_WINS",
    "BLOCKED_BY_TECHNICAL_LIMITATION",
    "BLOCKED_BY_LISTENING_EVIDENCE",
    GOLDEN_PENDING,
)


@dataclass
class GoldenReconstructionRecord:
    record_id: str
    source_hash: str
    rights_status: str
    diagnostic_version: str
    objective_version: str
    identity_guard_version: str
    candidate_id: str
    plan_hash: str
    engine_version: str
    technical_result: dict[str, Any]
    human_result: dict[str, Any]
    hardware_observations: list[dict[str, Any]]
    golden_status: str = GOLDEN_PENDING
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "source_hash": self.source_hash,
            "rights_status": self.rights_status,
            "diagnostic_version": self.diagnostic_version,
            "objective_version": self.objective_version,
            "identity_guard_version": self.identity_guard_version,
            "candidate_id": self.candidate_id,
            "plan_hash": self.plan_hash,
            "engine_version": self.engine_version,
            "technical_result": self.technical_result,
            "human_result": self.human_result,
            "hardware_observations": self.hardware_observations,
            "golden_status": self.golden_status,
            "created_at": self.created_at,
        }
