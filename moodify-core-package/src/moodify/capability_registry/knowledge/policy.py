"""Versioned production policy and rule-change proposals.

Proposals never auto-apply: human confirmation is required, then
policy_version increments and the change is recorded in the policy ledger.
The ledger is part of the geological record: every change references the
superseded rule and its historical source — rules can change but not be
forgotten. Minimum sample threshold (default N>=3) prevents pollution.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

SCHEMA_VERSION = "production-policy/0.1"
DEFAULT_MIN_SAMPLES = 3

ProposalType = Literal[
    "provider_preference", "default_parameter", "validation_threshold", "fallback_order",
]


@dataclass(frozen=True)
class RuleChangeProposal:
    schema_version: str
    proposal_id: str
    case_ids: tuple[str, ...]
    change_type: ProposalType
    target: str  # e.g. capability_id or rule_id
    proposed_value: dict
    rationale: str
    evidence_record_ids: tuple[str, ...]
    negative_knowledge_ids: tuple[str, ...] = ()
    confirmed: bool = False
    confirmed_by: str = ""
    superseded_rule: str | None = None  # geological record: what it replaces
    superseded_rule_source: str | None = None  # and why that rule existed

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "proposal_id": self.proposal_id,
            "case_ids": list(self.case_ids),
            "change_type": self.change_type,
            "target": self.target,
            "proposed_value": self.proposed_value,
            "rationale": self.rationale,
            "evidence_record_ids": list(self.evidence_record_ids),
            "negative_knowledge_ids": list(self.negative_knowledge_ids),
            "confirmed": self.confirmed,
            "confirmed_by": self.confirmed_by,
            "superseded_rule": self.superseded_rule,
            "superseded_rule_source": self.superseded_rule_source,
        }


@dataclass(frozen=True)
class PolicyEntry:
    schema_version: str
    policy_version: str
    change_type: ProposalType
    target: str
    value: dict
    proposal_id: str
    superseded_rule: str | None
    superseded_rule_source: str | None
    effective_at: str = ""

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "policy_version": self.policy_version,
            "change_type": self.change_type,
            "target": self.target,
            "value": self.value,
            "proposal_id": self.proposal_id,
            "superseded_rule": self.superseded_rule,
            "superseded_rule_source": self.superseded_rule_source,
            "effective_at": self.effective_at,
        }


class PolicyLedger:
    """Append-only versioned policy ledger with provenance."""

    def __init__(self, root: Path) -> None:
        self.root = root

    @property
    def _path(self) -> Path:
        return self.root / "policy.jsonl"

    def entries(self) -> list[PolicyEntry]:
        if not self._path.exists():
            return []
        return [PolicyEntry(**json.loads(line)) for line in self._path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def current_version(self) -> str:
        entries = self.entries()
        if not entries:
            return "policy/0.0"
        return entries[-1].policy_version

    def _next_version(self) -> str:
        current = self.current_version()
        try:
            num = int(current.rsplit("/", 1)[1])
        except (ValueError, IndexError):
            num = 0
        return f"policy/{num + 1}"

    def apply(
        self,
        proposal: RuleChangeProposal,
        *,
        confirmed_by: str = "operator",
        effective_at: str = "",
    ) -> PolicyEntry:
        if not proposal.confirmed:
            raise ValueError(f"proposal {proposal.proposal_id} is not confirmed")
        entry = PolicyEntry(
            schema_version=SCHEMA_VERSION,
            policy_version=self._next_version(),
            change_type=proposal.change_type,
            target=proposal.target,
            value=proposal.proposed_value,
            proposal_id=proposal.proposal_id,
            superseded_rule=proposal.superseded_rule,
            superseded_rule_source=proposal.superseded_rule_source,
            effective_at=effective_at,
        )
        self.root.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
        return entry


def propose_rule_change(
    case_ids: tuple[str, ...],
    change_type: ProposalType,
    target: str,
    proposed_value: dict,
    rationale: str,
    evidence_record_ids: tuple[str, ...],
    negative_knowledge_ids: tuple[str, ...] = (),
    superseded_rule: str | None = None,
    superseded_rule_source: str | None = None,
) -> RuleChangeProposal:
    return RuleChangeProposal(
        schema_version=SCHEMA_VERSION,
        proposal_id=f"prop-{uuid.uuid4().hex[:12]}",
        case_ids=case_ids,
        change_type=change_type,
        target=target,
        proposed_value=proposed_value,
        rationale=rationale,
        evidence_record_ids=evidence_record_ids,
        negative_knowledge_ids=negative_knowledge_ids,
        superseded_rule=superseded_rule,
        superseded_rule_source=superseded_rule_source,
    )


def confirm_proposal(proposal: RuleChangeProposal, confirmed_by: str = "operator") -> RuleChangeProposal:
    return RuleChangeProposal(
        schema_version=proposal.schema_version,
        proposal_id=proposal.proposal_id,
        case_ids=proposal.case_ids,
        change_type=proposal.change_type,
        target=proposal.target,
        proposed_value=proposal.proposed_value,
        rationale=proposal.rationale,
        evidence_record_ids=proposal.evidence_record_ids,
        negative_knowledge_ids=proposal.negative_knowledge_ids,
        confirmed=True,
        confirmed_by=confirmed_by,
        superseded_rule=proposal.superseded_rule,
        superseded_rule_source=proposal.superseded_rule_source,
    )


def meets_sample_threshold(measurement_count: int, minimum: int = DEFAULT_MIN_SAMPLES) -> bool:
    """Anti-pollution: single/anomalous cases cannot trigger proposals."""
    return measurement_count >= minimum
