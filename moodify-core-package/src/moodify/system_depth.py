"""Operational memory for Moodify's hidden system depth.

The module turns encountered difficulty into append-only, reviewable records.
It deliberately stores *why* a boundary exists alongside the mechanism that
protects it, so future changes can evolve without historical amnesia.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "moodify.system-depth/0.1"


class KnowledgeKind(StrEnum):
    FAILURE_BOUNDARY = "failure_boundary"
    REJECTED_PATH = "rejected_path"
    TRAINED_JUDGMENT = "trained_judgment"
    INTERFACE_UNCERTAINTY = "interface_uncertainty"


class KnowledgeStatus(StrEnum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    RETIRED = "retired"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _non_blank(value: str, name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{name} must not be blank")
    return normalized


@dataclass(frozen=True)
class DepthRecord:
    """One learned distinction that should survive its original discoverer."""

    kind: KnowledgeKind
    scope: str
    lesson: str
    rationale: str
    record_id: str = ""
    status: KnowledgeStatus = KnowledgeStatus.ACTIVE
    evidence_refs: tuple[str, ...] = ()
    guard_refs: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    supersedes: tuple[str, ...] = ()
    observed_at: str = ""
    recorded_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    schema: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "scope", _non_blank(self.scope, "scope"))
        object.__setattr__(self, "lesson", _non_blank(self.lesson, "lesson"))
        object.__setattr__(self, "rationale", _non_blank(self.rationale, "rationale"))
        if self.schema != SCHEMA_VERSION:
            raise ValueError(f"unsupported system-depth schema: {self.schema}")
        recorded_at = self.recorded_at or _utc_now()
        object.__setattr__(self, "recorded_at", recorded_at)
        if not self.record_id:
            identity = json.dumps(
                {
                    "kind": self.kind.value,
                    "scope": self.scope,
                    "lesson": self.lesson,
                    "rationale": self.rationale,
                    "observed_at": self.observed_at,
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
            object.__setattr__(self, "record_id", f"depth-{digest}")

    @property
    def operationalized(self) -> bool:
        """Whether the lesson has become a guard, test, or enforceable contract."""

        return bool(self.guard_refs)

    @property
    def inheritable(self) -> bool:
        """Whether another builder can inspect the reason and its evidence."""

        return bool(self.rationale and self.evidence_refs)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["kind"] = self.kind.value
        result["status"] = self.status.value
        return result

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "DepthRecord":
        allowed = set(cls.__dataclass_fields__)
        unknown = set(value) - allowed
        if unknown:
            raise ValueError(f"unknown system-depth fields: {sorted(unknown)}")
        data = dict(value)
        data["kind"] = KnowledgeKind(data["kind"])
        data["status"] = KnowledgeStatus(data.get("status", "active"))
        for name in ("evidence_refs", "guard_refs", "limitations", "supersedes"):
            data[name] = tuple(data.get(name, ()))
        return cls(**data)


def read_depth_ledger(path: Path) -> list[DepthRecord]:
    if not path.exists():
        return []
    records: list[DepthRecord] = []
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                records.append(DepthRecord.from_dict(json.loads(line)))
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                raise ValueError(f"invalid depth ledger line {line_number}: {exc}") from exc
    return records


def append_depth_record(path: Path, record: DepthRecord) -> str:
    """Append new knowledge without rewriting history.

    Exact replays are idempotent. Reusing an ID for different content is a hard
    error because silent mutation would destroy the ledger's historical meaning.
    """

    existing = {item.record_id: item for item in read_depth_ledger(path)}
    if record.record_id in existing:
        if existing[record.record_id].to_dict() == record.to_dict():
            return "skipped"
        raise ValueError(f"record_id conflict: {record.record_id}")
    known_ids = set(existing)
    missing = set(record.supersedes) - known_ids
    if missing:
        raise ValueError(f"supersedes unknown records: {sorted(missing)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
    return "stored"


def active_depth(records: Iterable[DepthRecord], scope: str | None = None) -> list[DepthRecord]:
    items = list(records)
    superseded_ids = {old_id for item in items for old_id in item.supersedes}
    return [
        item
        for item in items
        if item.status is KnowledgeStatus.ACTIVE
        and item.record_id not in superseded_ids
        and (scope is None or item.scope == scope or item.scope.startswith(f"{scope}."))
    ]


def assess_depth(records: Iterable[DepthRecord]) -> dict[str, Any]:
    """Return a truthful audit, including gaps rather than a vanity score."""

    active = active_depth(records)
    operationalized = [item for item in active if item.operationalized]
    inheritable = [item for item in active if item.inheritable]
    interface_records = [
        item for item in active if item.kind is KnowledgeKind.INTERFACE_UNCERTAINTY
    ]
    concealed_uncertainty = [item.record_id for item in interface_records if not item.limitations]
    gaps: list[dict[str, str]] = []
    for item in active:
        if not item.operationalized:
            gaps.append({"record_id": item.record_id, "gap": "missing_guard"})
        if not item.evidence_refs:
            gaps.append({"record_id": item.record_id, "gap": "missing_evidence"})
    gaps.extend(
        {"record_id": record_id, "gap": "uncertainty_not_exposed"}
        for record_id in concealed_uncertainty
    )
    return {
        "schema": SCHEMA_VERSION,
        "active_records": len(active),
        "operationalized_records": len(operationalized),
        "inheritable_records": len(inheritable),
        "truthful_interface": not concealed_uncertainty,
        "ready": bool(active) and not gaps,
        "gaps": gaps,
    }
