"""Canonical operational knowledge rule contract."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field, field_validator, model_validator

from .base import CanonicalModel, ensure_json_safe, freeze_json_value
from .ids import validate_id


class RuleStatus(StrEnum):
    DRAFT = "DRAFT"
    EXPERIMENTAL = "EXPERIMENTAL"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    RETIRED = "RETIRED"


class Rule(CanonicalModel):
    rule_id: str
    name: str
    version: str
    status: RuleStatus
    scope: str
    description: str
    provenance_evidence_ids: tuple[str, ...] = ()
    conditions: dict[str, Any] = Field(default_factory=dict)
    action: dict[str, Any] = Field(default_factory=dict)
    limitations: tuple[str, ...] = ()
    supersedes_rule_id: str | None = None

    @field_validator("rule_id")
    @classmethod
    def require_rule_id(cls, value: str) -> str:
        return validate_id(value, "rule")

    @field_validator("name", "version", "scope", "description")
    @classmethod
    def require_non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("field must be non-empty")
        return value

    @field_validator("provenance_evidence_ids")
    @classmethod
    def require_evidence_ids(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        checked = tuple(validate_id(value, "evid") for value in values)
        if len(set(checked)) != len(checked):
            raise ValueError("duplicate evidence IDs")
        return checked

    @field_validator("conditions", "action")
    @classmethod
    def require_json_safe(cls, value: dict[str, Any]) -> dict[str, Any]:
        ensure_json_safe(value)
        return freeze_json_value(value)

    @field_validator("limitations")
    @classmethod
    def require_limitations(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if any(not value.strip() for value in values):
            raise ValueError("limitations must be non-empty")
        return values

    @model_validator(mode="after")
    def require_authority_invariants(self) -> "Rule":
        if self.status == RuleStatus.ACTIVE and not self.provenance_evidence_ids:
            raise ValueError("ACTIVE rule requires evidence provenance")
        if self.supersedes_rule_id is not None:
            validate_id(self.supersedes_rule_id, "rule")
            if self.supersedes_rule_id == self.rule_id:
                raise ValueError("rule cannot supersede itself")
        return self
