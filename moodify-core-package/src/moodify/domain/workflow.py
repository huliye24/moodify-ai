"""Durable project workflow state machine for Moodify Workspace v2."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


WORKFLOW_SCHEMA_VERSION = "project_workflow.v1"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class WorkflowStage(str, Enum):
    INTAKE = "INTAKE"
    BRIEF = "BRIEF"
    DIAGNOSIS = "DIAGNOSIS"
    DESIGN = "DESIGN"
    PROCESS = "PROCESS"
    JUDGE = "JUDGE"
    APPROVAL = "APPROVAL"
    FINAL = "FINAL"
    PAUSED = "PAUSED"
    FAILED = "FAILED"


class WorkflowAction(str, Enum):
    ADVANCE = "ADVANCE"
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    FAIL = "FAIL"


WORKFLOW_SEQUENCE = (
    WorkflowStage.INTAKE,
    WorkflowStage.BRIEF,
    WorkflowStage.DIAGNOSIS,
    WorkflowStage.DESIGN,
    WorkflowStage.PROCESS,
    WorkflowStage.JUDGE,
    WorkflowStage.APPROVAL,
    WorkflowStage.FINAL,
)


class WorkflowEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    action: WorkflowAction
    from_stage: WorkflowStage
    to_stage: WorkflowStage
    at: datetime
    reason: str | None = None

    @field_validator("at")
    @classmethod
    def timestamp_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("workflow event timestamps must be timezone-aware")
        return value


class ProjectWorkflow(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    schema_version: Literal["project_workflow.v1"] = WORKFLOW_SCHEMA_VERSION
    project_id: str = Field(min_length=1)
    stage: WorkflowStage = WorkflowStage.INTAKE
    paused_from: WorkflowStage | None = None
    failure_reason: str | None = None
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)
    history: tuple[WorkflowEvent, ...] = ()

    @field_validator("created_at", "updated_at")
    @classmethod
    def timestamps_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("workflow timestamps must be timezone-aware")
        return value

    @model_validator(mode="after")
    def validate_state(self) -> "ProjectWorkflow":
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must not precede created_at")
        if self.stage is WorkflowStage.PAUSED:
            if self.paused_from not in WORKFLOW_SEQUENCE[:-1]:
                raise ValueError("PAUSED workflow requires a resumable paused_from stage")
        elif self.paused_from is not None:
            raise ValueError("paused_from is only valid while PAUSED")
        if self.stage is WorkflowStage.FAILED:
            if not self.failure_reason:
                raise ValueError("FAILED workflow requires failure_reason")
        elif self.failure_reason is not None:
            raise ValueError("failure_reason is only valid while FAILED")
        if not self.history and self.stage is not WorkflowStage.INTAKE:
            raise ValueError("workflow without history must start at INTAKE")
        if self.history:
            if self.history[-1].to_stage is not self.stage:
                raise ValueError("last workflow event must end at current stage")
            if self.history[-1].at != self.updated_at:
                raise ValueError("last workflow event must match updated_at")
        return self

    def _transition(
        self,
        to_stage: WorkflowStage,
        action: WorkflowAction,
        *,
        at: datetime | None,
        reason: str | None = None,
        paused_from: WorkflowStage | None = None,
        failure_reason: str | None = None,
    ) -> "ProjectWorkflow":
        transition_at = at or _utc_now()
        if transition_at.tzinfo is None or transition_at.utcoffset() is None:
            raise ValueError("transition timestamp must be timezone-aware")
        if transition_at < self.updated_at:
            raise ValueError("transition timestamp must not precede updated_at")
        event = WorkflowEvent(
            action=action,
            from_stage=self.stage,
            to_stage=to_stage,
            at=transition_at,
            reason=reason,
        )
        data = self.model_dump()
        data.update(
            {
                "stage": to_stage,
                "paused_from": paused_from,
                "failure_reason": failure_reason,
                "updated_at": transition_at,
                "history": (*self.history, event),
            }
        )
        return ProjectWorkflow.model_validate(data)

    def advance(
        self, *, at: datetime | None = None, reason: str | None = None
    ) -> "ProjectWorkflow":
        if self.stage not in WORKFLOW_SEQUENCE[:-1]:
            raise ValueError(f"{self.stage.value} workflow cannot advance")
        next_stage = WORKFLOW_SEQUENCE[WORKFLOW_SEQUENCE.index(self.stage) + 1]
        return self._transition(
            next_stage, WorkflowAction.ADVANCE, at=at, reason=reason
        )

    def pause(
        self, *, at: datetime | None = None, reason: str | None = None
    ) -> "ProjectWorkflow":
        if self.stage not in WORKFLOW_SEQUENCE[:-1]:
            raise ValueError(f"{self.stage.value} workflow cannot be paused")
        return self._transition(
            WorkflowStage.PAUSED,
            WorkflowAction.PAUSE,
            at=at,
            reason=reason,
            paused_from=self.stage,
        )

    def resume(
        self, *, at: datetime | None = None, reason: str | None = None
    ) -> "ProjectWorkflow":
        if self.stage is not WorkflowStage.PAUSED or self.paused_from is None:
            raise ValueError("only a PAUSED workflow can resume")
        return self._transition(
            self.paused_from,
            WorkflowAction.RESUME,
            at=at,
            reason=reason,
        )

    def fail(
        self, reason: str, *, at: datetime | None = None
    ) -> "ProjectWorkflow":
        if self.stage in {WorkflowStage.FINAL, WorkflowStage.FAILED}:
            raise ValueError(f"{self.stage.value} workflow cannot fail")
        return self._transition(
            WorkflowStage.FAILED,
            WorkflowAction.FAIL,
            at=at,
            reason=reason,
            failure_reason=reason,
        )
