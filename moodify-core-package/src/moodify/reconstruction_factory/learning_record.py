"""Reconstruction Learning Record (MFY-CR-P07).

Extends the existing ProductionCase / evidence authority (never a second
authority). One record per track: everything needed to compare 10 / 100
tracks later, with all versions pinned.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field

from moodify.reconstruction_factory.rights import RightsRecord

RECORD_VERSION = "reconstruction-learning-record-v1"


@dataclass(frozen=True)
class ReconstructionLearningRecord:
    record_id: str
    case_id: str
    source_hash: str
    rights: RightsRecord
    source_characteristics: dict[str, object]
    diagnostic_findings: dict[str, object] = field(default_factory=dict)
    diagnostic_confidences: dict[str, float] = field(default_factory=dict)
    objective_ids: tuple[str, ...] = ()
    candidate_plan_hashes: tuple[str, ...] = ()
    candidate_parameter_distance: dict[str, float] = field(default_factory=dict)
    technical_rank: str | None = None
    identity_guard_results: dict[str, object] = field(default_factory=dict)
    human_rank: str | None = None
    identity_preservation_rank: str | None = None
    source_vs_winner_result: str | None = None
    hardware_observations: tuple[dict[str, object], ...] = ()
    stem_escalation_status: str = "NOT_ATTEMPTED"
    golden_status: str = "PENDING"
    failure_or_bypass_reason: str | None = None
    versions: dict[str, str] = field(default_factory=dict)
    training_permission_granted: bool = False
    record_version: str = RECORD_VERSION

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    def to_json_line(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True)


def _deterministic_id(case_id: str, source_hash: str) -> str:
    blob = json.dumps({"case_id": case_id, "source_hash": source_hash},
                      sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def build_learning_record(
    case_id: str,
    source_hash: str,
    rights: RightsRecord,
    source_characteristics: dict[str, object],
    versions: dict[str, str],
    **extra: object,
) -> ReconstructionLearningRecord:
    """Deterministic record construction (same inputs -> same record_id)."""
    return ReconstructionLearningRecord(
        record_id=f"rlr_{_deterministic_id(case_id, source_hash)}",
        case_id=case_id,
        source_hash=source_hash,
        rights=rights,
        source_characteristics=source_characteristics,
        versions=versions,
        **extra,
    )
