"""Knowledge records — measurement, judgment and negative knowledge.

All records are append-only (amnesia protection): once persisted they cannot
be deleted or rewritten; corrections append a new version marked superseded.
Records link to ExecutionRecord (019) / validation results (020) by id —
never duplicate stored evidence.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

SCHEMA_VERSION = "knowledge-record/0.1"

Judgment = Literal["approved", "rejected", "revised"]


@dataclass(frozen=True)
class MeasurementRecord:
    """Technical observations of a production case (021 Stage A)."""

    schema_version: str
    record_id: str
    case_id: str
    capability_id: str
    provider_id: str
    execution_record_id: str
    input_features: dict
    parameters: dict
    measurements: dict
    elapsed_s: float = 0.0
    created_at: str = ""
    superseded_by: str | None = None

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "record_id": self.record_id,
            "case_id": self.case_id,
            "capability_id": self.capability_id,
            "provider_id": self.provider_id,
            "execution_record_id": self.execution_record_id,
            "input_features": self.input_features,
            "parameters": self.parameters,
            "measurements": self.measurements,
            "elapsed_s": round(self.elapsed_s, 3),
            "created_at": self.created_at,
            "superseded_by": self.superseded_by,
        }


@dataclass(frozen=True)
class JudgmentRecord:
    """Human or machine decision with structured reason (021 Stage A)."""

    schema_version: str
    record_id: str
    case_id: str
    judgment: Judgment
    reason: str
    reason_structured: dict
    issuer: str = ""
    created_at: str = ""
    superseded_by: str | None = None

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "record_id": self.record_id,
            "case_id": self.case_id,
            "judgment": self.judgment,
            "reason": self.reason,
            "reason_structured": self.reason_structured,
            "issuer": self.issuer,
            "created_at": self.created_at,
            "superseded_by": self.superseded_by,
        }


@dataclass(frozen=True)
class NegativeKnowledgeRecord:
    """Rejected paths are first-class knowledge (POSC-003 / PR-007)."""

    schema_version: str
    record_id: str
    case_id: str
    kind: str  # "rejected_candidate" | "fallback" | "validation_failure" | "rule_source"
    detail: dict
    linked_rule_id: str | None = None
    created_at: str = ""
    superseded_by: str | None = None

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "record_id": self.record_id,
            "case_id": self.case_id,
            "kind": self.kind,
            "detail": self.detail,
            "linked_rule_id": self.linked_rule_id,
            "created_at": self.created_at,
            "superseded_by": self.superseded_by,
        }


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class KnowledgeStore:
    """Append-only JSONL store per record type (amnesia protection enforced)."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def _path(self, kind: str) -> Path:
        return self.root / f"{kind}.jsonl"

    def _append(self, kind: str, record: dict) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        path = self._path(kind)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return path

    def _records(self, kind: str) -> list[dict]:
        return _load_jsonl(self._path(kind))

    # ── write (append-only; no delete/rewrite) ──────────────────────────
    def add_measurement(self, record: MeasurementRecord) -> Path:
        return self._append("measurements", record.to_dict())

    def add_judgment(self, record: JudgmentRecord) -> Path:
        return self._append("judgments", record.to_dict())

    def add_negative(self, record: NegativeKnowledgeRecord) -> Path:
        return self._append("negative", record.to_dict())

    def supersede(self, kind: str, record_id: str, superseded_by: str) -> None:
        """Append a superseded marker — original record is never rewritten."""
        records = self._records(kind)
        original = next((r for r in records if r.get("record_id") == record_id), None)
        if original is None:
            raise ValueError(f"{kind} record not found: {record_id}")
        marker = dict(original)
        marker["superseded_by"] = superseded_by
        marker["record_id"] = f"{original['record_id']}~superseded"
        self._append(kind, marker)

    # ── read (query; history preserved) ─────────────────────────────────
    def measurements(self, case_id: str | None = None) -> list[MeasurementRecord]:
        return [MeasurementRecord(**r) for r in self._records("measurements")
                if case_id is None or r.get("case_id") == case_id]

    def judgments(self, case_id: str | None = None) -> list[JudgmentRecord]:
        return [JudgmentRecord(**r) for r in self._records("judgments")
                if case_id is None or r.get("case_id") == case_id]

    def negative(self, case_id: str | None = None) -> list[NegativeKnowledgeRecord]:
        return [NegativeKnowledgeRecord(**r) for r in self._records("negative")
                if case_id is None or r.get("case_id") == case_id]

    def count(self, kind: str) -> int:
        return len(self._records(kind))


def new_measurement(
    case_id: str,
    capability_id: str,
    provider_id: str,
    execution_record_id: str,
    input_features: dict,
    parameters: dict,
    measurements: dict,
    elapsed_s: float = 0.0,
    created_at: str = "",
) -> MeasurementRecord:
    return MeasurementRecord(
        schema_version=SCHEMA_VERSION,
        record_id=f"m-{uuid.uuid4().hex[:12]}",
        case_id=case_id,
        capability_id=capability_id,
        provider_id=provider_id,
        execution_record_id=execution_record_id,
        input_features=input_features,
        parameters=parameters,
        measurements=measurements,
        elapsed_s=elapsed_s,
        created_at=created_at,
    )


def new_judgment(
    case_id: str,
    judgment: Judgment,
    reason: str,
    reason_structured: dict,
    issuer: str = "",
    created_at: str = "",
) -> JudgmentRecord:
    return JudgmentRecord(
        schema_version=SCHEMA_VERSION,
        record_id=f"j-{uuid.uuid4().hex[:12]}",
        case_id=case_id,
        judgment=judgment,
        reason=reason,
        reason_structured=reason_structured,
        issuer=issuer,
        created_at=created_at,
    )


def new_negative(
    case_id: str,
    kind: str,
    detail: dict,
    linked_rule_id: str | None = None,
    created_at: str = "",
) -> NegativeKnowledgeRecord:
    return NegativeKnowledgeRecord(
        schema_version=SCHEMA_VERSION,
        record_id=f"n-{uuid.uuid4().hex[:12]}",
        case_id=case_id,
        kind=kind,
        detail=detail,
        linked_rule_id=linked_rule_id,
        created_at=created_at,
    )
