"""Canonical bounded unit of accountable production work."""

from __future__ import annotations

from enum import StrEnum

from pydantic import field_validator, model_validator

from .base import CanonicalModel
from .ids import validate_id


class LifecycleState(StrEnum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    AWAITING_HUMAN = "AWAITING_HUMAN"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AuthorityState(StrEnum):
    SYSTEM = "SYSTEM"
    ALGORITHM = "ALGORITHM"
    HUMAN_REQUIRED = "HUMAN_REQUIRED"
    HUMAN_APPROVED = "HUMAN_APPROVED"
    HUMAN_REJECTED = "HUMAN_REJECTED"


class ProductionCase(CanonicalModel):
    case_id: str
    source_id: str
    objective: str
    lifecycle_state: LifecycleState
    authority_state: AuthorityState
    measurement_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    rule_ids: tuple[str, ...] = ()
    parent_case_id: str | None = None

    @field_validator("case_id")
    @classmethod
    def require_case_id(cls, value: str) -> str:
        return validate_id(value, "case")

    @field_validator("source_id", "objective")
    @classmethod
    def require_non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("field must be non-empty")
        return value

    @field_validator("measurement_ids")
    @classmethod
    def require_measurement_ids(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        return cls._validate_unique_ids(values, "meas")

    @field_validator("evidence_ids")
    @classmethod
    def require_evidence_ids(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        return cls._validate_unique_ids(values, "evid")

    @field_validator("rule_ids")
    @classmethod
    def require_rule_ids(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        return cls._validate_unique_ids(values, "rule")

    @staticmethod
    def _validate_unique_ids(values: tuple[str, ...], kind: str) -> tuple[str, ...]:
        checked = tuple(validate_id(value, kind) for value in values)
        if len(set(checked)) != len(checked):
            raise ValueError(f"duplicate {kind} IDs")
        return checked

    @model_validator(mode="after")
    def require_valid_lineage(self) -> "ProductionCase":
        if self.parent_case_id is not None:
            validate_id(self.parent_case_id, "case")
            if self.parent_case_id == self.case_id:
                raise ValueError("case cannot be its own parent")
        return self
