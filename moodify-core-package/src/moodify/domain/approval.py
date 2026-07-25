"""Immutable human approval evidence for Moodify Workspace v2."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .thread import ThreadType


APPROVAL_SCHEMA_VERSION = "approval_decision.v1"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ApprovalOutcome(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    RETURNED = "RETURNED"


class ApprovalActorType(str, Enum):
    HUMAN = "HUMAN"
    SYSTEM = "SYSTEM"


class ApprovalDecision(BaseModel):
    """Append-only decision evidence bound to one exact audio version."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
        use_enum_values=False,
    )

    schema_version: Literal["approval_decision.v1"] = APPROVAL_SCHEMA_VERSION
    decision_id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    version_id: str = Field(min_length=1)
    outcome: ApprovalOutcome
    reason: str = Field(min_length=1)
    operator: str = Field(min_length=1)
    actor_type: ApprovalActorType = ApprovalActorType.HUMAN
    return_to_thread: ThreadType | None = None
    supersedes_decision_id: str | None = None
    decided_at: datetime = Field(default_factory=_utc_now)

    @field_validator("decided_at")
    @classmethod
    def decided_at_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("approval timestamp must be timezone-aware")
        return value

    @model_validator(mode="after")
    def validate_decision_semantics(self) -> "ApprovalDecision":
        if self.outcome is ApprovalOutcome.RETURNED:
            if self.return_to_thread is None:
                raise ValueError("RETURNED decisions require return_to_thread")
        elif self.return_to_thread is not None:
            raise ValueError(
                "return_to_thread is only valid for RETURNED decisions"
            )
        if (
            self.outcome is ApprovalOutcome.APPROVED
            and self.actor_type is not ApprovalActorType.HUMAN
        ):
            raise ValueError("final approval must be made by a human")
        if self.supersedes_decision_id == self.decision_id:
            raise ValueError("a decision cannot supersede itself")
        return self
