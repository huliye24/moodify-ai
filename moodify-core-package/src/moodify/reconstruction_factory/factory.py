"""Serial reconstruction batch executor (MFY-CR-P07).

Reuses the Data Factory runner discipline: serial (concurrency=1), idempotent,
failure-preserving, deterministic IDs. Correctness > throughput. No automatic
threshold updates — proposals only.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Callable

from moodify.reconstruction_factory.learning_record import (
    ReconstructionLearningRecord,
)
from moodify.reconstruction_factory.rights import RightsRecord, validate_rights

BATCH_VERSION = "reconstruction-batch-v1"


@dataclass(frozen=True)
class FailureRecord:
    failure_code: str
    stage: str
    case_id: str
    source_hash: str
    partial_artifacts: tuple[str, ...]
    retry_status: str  # NOT_RETRIED / RETRIED / PERMANENT
    human_action: str  # REQUIRED / NONE
    detail: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ProposedRuleUpdate:
    proposal_id: str
    target: str
    current_value: str
    proposed_value: str
    evidence_refs: tuple[str, ...]
    status: str = "PENDING_REVIEW"
    # explicitly NOT auto-applied; independent review required

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ReconstructionBatchResult:
    records: tuple[ReconstructionLearningRecord, ...]
    failures: tuple[FailureRecord, ...]
    proposals: tuple[ProposedRuleUpdate, ...]
    metrics: dict[str, object]

    def to_json(self, path: str) -> None:
        payload = {
            "version": BATCH_VERSION,
            "records": [r.to_dict() for r in self.records],
            "failures": [f.to_dict() for f in self.failures],
            "proposals": [p.to_dict() for p in self.proposals],
            "metrics": self.metrics,
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
            fh.write("\n")


def _case_metrics(records: list[ReconstructionLearningRecord]) -> dict[str, object]:
    outcomes = [r.golden_status for r in records]
    return {
        "tracks_total": len(records),
        "golden_count": outcomes.count("GOLDEN"),
        "improved_count": outcomes.count("IMPROVED"),
        "subtle_count": outcomes.count("SUBTLE_IMPROVEMENT"),
        "source_wins": outcomes.count("SOURCE_WINS"),
        "human_required": outcomes.count("HUMAN_REQUIRED"),
        "stem_recommended": outcomes.count("STEM_RECOMMENDED"),
        "unsupported": outcomes.count("UNSUPPORTED"),
        "failed": outcomes.count("FAILED"),
    }


def run_reconstruction_batch(
    cases: list[dict[str, object]],
    process_case: Callable[[dict[str, object]], ReconstructionLearningRecord],
    seen_ids: set[str] | None = None,
) -> ReconstructionBatchResult:
    """Serial batch: process_case per case, idempotent on (case_id, source_hash).

    process_case may raise; the failure is preserved with a code instead of
    aborting the batch. Threshold updates are only PROPOSED, never applied.
    """
    seen = seen_ids if seen_ids is not None else set()
    records: list[ReconstructionLearningRecord] = []
    failures: list[FailureRecord] = []
    proposals: list[ProposedRuleUpdate] = []

    for case in cases:
        case_id = str(case["case_id"])
        source_hash = str(case["source_hash"])
        dedup_key = f"{case_id}:{source_hash}"
        if dedup_key in seen:
            failures.append(
                FailureRecord(
                    failure_code="DUPLICATE_SOURCE",
                    stage="batch",
                    case_id=case_id,
                    source_hash=source_hash,
                    partial_artifacts=(),
                    retry_status="NOT_RETRIED",
                    human_action="NONE",
                    detail="same (case_id, source_hash) already processed; idempotent skip",
                )
            )
            continue
        seen.add(dedup_key)

        rights = case.get("rights")
        if isinstance(rights, dict):
            rights = RightsRecord(**rights)
        if rights is not None:
            ok, reason = validate_rights(rights)
            if not ok:
                failures.append(
                    FailureRecord("RIGHTS_BLOCKED", "rights_gate", case_id, source_hash,
                                  (), "NOT_RETRIED", "REQUIRED", reason)
                )
                continue

        try:
            record = process_case(case)
        except Exception as exc:  # noqa: BLE001 — preserve any failure
            failures.append(
                FailureRecord("ENGINE_FAILURE", "process_case", case_id, source_hash,
                              (), "NOT_RETRIED", "REQUIRED", str(exc))
            )
            continue

        if isinstance(record, ProposedRuleUpdate):
            proposals.append(record)
            continue
        records.append(record)

    return ReconstructionBatchResult(
        records=tuple(records),
        failures=tuple(failures),
        proposals=tuple(proposals),
        metrics=_case_metrics(records),
    )
