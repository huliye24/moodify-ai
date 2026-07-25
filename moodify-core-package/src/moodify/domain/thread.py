"""Persistent workflow thread model for Moodify Studio Workspace v2."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


THREAD_SCHEMA_VERSION = "project_thread.v1"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ThreadRole(str, Enum):
    PRODUCER = "PRODUCER"
    ANALYST = "ANALYST"
    DESIGNER = "DESIGNER"
    WORKER = "WORKER"
    JUDGE = "JUDGE"
    ARCHIVE = "ARCHIVE"


class ThreadType(str, Enum):
    BRIEF = "BRIEF"
    DIAGNOSIS = "DIAGNOSIS"
    DESIGN = "DESIGN"
    VOCAL = "VOCAL"
    SPECTRUM = "SPECTRUM"
    DYNAMICS = "DYNAMICS"
    SPACE = "SPACE"
    LOUDNESS = "LOUDNESS"
    EXPORT = "EXPORT"
    JUDGE = "JUDGE"
    ARCHIVE = "ARCHIVE"


class ThreadStatus(str, Enum):
    PLANNED = "PLANNED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    AWAITING_USER = "AWAITING_USER"
    PASSED = "PASSED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


ROLE_BY_THREAD_TYPE: dict[ThreadType, ThreadRole] = {
    ThreadType.BRIEF: ThreadRole.PRODUCER,
    ThreadType.DIAGNOSIS: ThreadRole.ANALYST,
    ThreadType.DESIGN: ThreadRole.DESIGNER,
    ThreadType.VOCAL: ThreadRole.WORKER,
    ThreadType.SPECTRUM: ThreadRole.WORKER,
    ThreadType.DYNAMICS: ThreadRole.WORKER,
    ThreadType.SPACE: ThreadRole.WORKER,
    ThreadType.LOUDNESS: ThreadRole.WORKER,
    ThreadType.EXPORT: ThreadRole.WORKER,
    ThreadType.JUDGE: ThreadRole.JUDGE,
    ThreadType.ARCHIVE: ThreadRole.ARCHIVE,
}


ALLOWED_TRANSITIONS: dict[ThreadStatus, set[ThreadStatus]] = {
    ThreadStatus.PLANNED: {ThreadStatus.QUEUED, ThreadStatus.CANCELED},
    ThreadStatus.QUEUED: {
        ThreadStatus.RUNNING,
        ThreadStatus.FAILED,
        ThreadStatus.CANCELED,
    },
    ThreadStatus.RUNNING: {
        ThreadStatus.AWAITING_USER,
        ThreadStatus.PASSED,
        ThreadStatus.REJECTED,
        ThreadStatus.FAILED,
        ThreadStatus.CANCELED,
    },
    ThreadStatus.AWAITING_USER: {
        ThreadStatus.QUEUED,
        ThreadStatus.RUNNING,
        ThreadStatus.PASSED,
        ThreadStatus.REJECTED,
        ThreadStatus.CANCELED,
    },
    ThreadStatus.PASSED: set(),
    ThreadStatus.REJECTED: set(),
    ThreadStatus.FAILED: set(),
    ThreadStatus.CANCELED: set(),
}


class ProjectThread(BaseModel):
    """A durable professional workflow node, not a chat or OS thread."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
        use_enum_values=False,
    )

    schema_version: Literal["project_thread.v1"] = THREAD_SCHEMA_VERSION
    thread_id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    thread_type: ThreadType
    role: ThreadRole
    status: ThreadStatus = ThreadStatus.PLANNED
    current_task_id: str | None = None
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    retry_count: int = Field(default=0, ge=0)
    max_retries: int = Field(default=2, ge=0)
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)
    started_at: datetime | None = None
    finished_at: datetime | None = None

    @field_validator("created_at", "updated_at", "started_at", "finished_at")
    @classmethod
    def timestamps_must_be_timezone_aware(
        cls, value: datetime | None
    ) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("thread timestamps must be timezone-aware")
        return value

    @model_validator(mode="after")
    def validate_thread_invariants(self) -> "ProjectThread":
        expected_role = ROLE_BY_THREAD_TYPE[self.thread_type]
        if self.role is not expected_role:
            raise ValueError(
                f"{self.thread_type.value} threads require role "
                f"{expected_role.value}"
            )
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must not be earlier than created_at")
        if self.retry_count > self.max_retries:
            raise ValueError("retry_count must not exceed max_retries")
        if self.started_at is not None and self.started_at < self.created_at:
            raise ValueError("started_at must not be earlier than created_at")
        if self.finished_at is not None:
            if self.started_at is None:
                raise ValueError("finished_at requires started_at")
            if self.finished_at < self.started_at:
                raise ValueError("finished_at must not be earlier than started_at")
        if self.status is ThreadStatus.RUNNING and self.started_at is None:
            raise ValueError("RUNNING threads require started_at")
        if self.status in {
            ThreadStatus.PASSED,
            ThreadStatus.REJECTED,
            ThreadStatus.FAILED,
            ThreadStatus.CANCELED,
        } and self.finished_at is None:
            raise ValueError(f"{self.status.value} threads require finished_at")
        if self.status is ThreadStatus.FAILED and not self.error:
            raise ValueError("FAILED threads require an error")
        return self

    def transition_to(
        self,
        new_status: ThreadStatus,
        *,
        at: datetime | None = None,
        error: str | None = None,
        outputs: dict[str, Any] | None = None,
    ) -> "ProjectThread":
        """Return a validated copy after one legal lifecycle transition."""

        if new_status not in ALLOWED_TRANSITIONS[self.status]:
            raise ValueError(
                f"illegal thread transition: {self.status.value} -> "
                f"{new_status.value}"
            )
        transition_at = at or _utc_now()
        if transition_at.tzinfo is None or transition_at.utcoffset() is None:
            raise ValueError("transition timestamp must be timezone-aware")
        if transition_at < self.updated_at:
            raise ValueError("transition timestamp must not precede updated_at")

        data = self.model_dump()
        data["status"] = new_status
        data["updated_at"] = transition_at
        if new_status is ThreadStatus.RUNNING and data["started_at"] is None:
            data["started_at"] = transition_at
        if outputs is not None:
            data["outputs"] = outputs
        if new_status is ThreadStatus.FAILED:
            data["error"] = error or self.error
        elif new_status in {ThreadStatus.PASSED, ThreadStatus.REJECTED}:
            data["error"] = error
        if new_status in {
            ThreadStatus.PASSED,
            ThreadStatus.REJECTED,
            ThreadStatus.FAILED,
            ThreadStatus.CANCELED,
        }:
            if data["started_at"] is None:
                data["started_at"] = transition_at
            data["finished_at"] = transition_at
        return ProjectThread.model_validate(data)

    def queue_retry(
        self, *, at: datetime | None = None, task_id: str | None = None
    ) -> "ProjectThread":
        """Requeue a rejected or failed thread without mutating its history."""

        if self.status not in {ThreadStatus.REJECTED, ThreadStatus.FAILED}:
            raise ValueError("only REJECTED or FAILED threads can be retried")
        if self.retry_count >= self.max_retries:
            raise ValueError("thread retry limit reached")
        retry_at = at or _utc_now()
        if retry_at.tzinfo is None or retry_at.utcoffset() is None:
            raise ValueError("retry timestamp must be timezone-aware")
        if retry_at < self.updated_at:
            raise ValueError("retry timestamp must not precede updated_at")

        data = self.model_dump()
        data.update(
            {
                "status": ThreadStatus.QUEUED,
                "current_task_id": task_id,
                "error": None,
                "retry_count": self.retry_count + 1,
                "updated_at": retry_at,
                "started_at": None,
                "finished_at": None,
            }
        )
        return ProjectThread.model_validate(data)
