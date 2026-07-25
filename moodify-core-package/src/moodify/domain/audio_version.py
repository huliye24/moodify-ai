"""Immutable audio version nodes for Moodify Studio Workspace v2."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import PurePosixPath
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .approval import ApprovalDecision, ApprovalOutcome


AUDIO_VERSION_SCHEMA_VERSION = "audio_version.v1"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_BRANCH_RE = re.compile(r"^[a-z0-9][a-z0-9._/-]*$")
_AUDIO_EXTENSIONS = {".wav", ".flac", ".aif", ".aiff"}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class VersionStatus(str, Enum):
    DRAFT = "DRAFT"
    REVIEWING = "REVIEWING"
    REJECTED = "REJECTED"
    APPROVED = "APPROVED"
    DELIVERED = "DELIVERED"
    ARCHIVED = "ARCHIVED"


ALLOWED_VERSION_TRANSITIONS: dict[VersionStatus, set[VersionStatus]] = {
    VersionStatus.DRAFT: {VersionStatus.REVIEWING, VersionStatus.ARCHIVED},
    VersionStatus.REVIEWING: {
        VersionStatus.REJECTED,
        VersionStatus.APPROVED,
        VersionStatus.ARCHIVED,
    },
    VersionStatus.REJECTED: {VersionStatus.ARCHIVED},
    VersionStatus.APPROVED: {
        VersionStatus.DELIVERED,
        VersionStatus.ARCHIVED,
    },
    VersionStatus.DELIVERED: {VersionStatus.ARCHIVED},
    VersionStatus.ARCHIVED: set(),
}


class AudioVersion(BaseModel):
    """A version-tree node whose audio identity can never be overwritten."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
        use_enum_values=False,
    )

    schema_version: Literal["audio_version.v1"] = AUDIO_VERSION_SCHEMA_VERSION
    version_id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    parent_version_id: str | None = None
    branch: str = Field(default="main", min_length=1)
    name: str = Field(min_length=1)
    purpose: str = Field(min_length=1)
    audio_path: str = Field(min_length=1)
    audio_sha256: str
    status: VersionStatus = VersionStatus.DRAFT
    treatment_plan_id: str | None = None
    treatment_variant_id: str | None = None
    treatment_record_id: str | None = None
    created_by: str = Field(min_length=1)
    approval: ApprovalDecision | None = None
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)

    @field_validator("branch")
    @classmethod
    def branch_must_be_portable(cls, value: str) -> str:
        if not _BRANCH_RE.fullmatch(value):
            raise ValueError("branch must use lowercase portable path characters")
        if ".." in value.split("/"):
            raise ValueError("branch must not contain parent traversal")
        return value

    @field_validator("audio_path")
    @classmethod
    def audio_path_must_be_relative_version_audio(cls, value: str) -> str:
        normalized = value.replace("\\", "/")
        path = PurePosixPath(normalized)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("audio_path must be a safe project-relative path")
        if not path.parts or path.parts[0] != "versions":
            raise ValueError("audio_path must be stored under versions/")
        if path.suffix.casefold() not in _AUDIO_EXTENSIONS:
            raise ValueError("audio_path must use a supported lossless audio type")
        return path.as_posix()

    @field_validator("audio_sha256")
    @classmethod
    def sha256_must_be_canonical(cls, value: str) -> str:
        normalized = value.casefold()
        if not _SHA256_RE.fullmatch(normalized):
            raise ValueError("audio_sha256 must contain 64 hexadecimal characters")
        return normalized

    @field_validator("created_at", "updated_at")
    @classmethod
    def timestamps_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("version timestamps must be timezone-aware")
        return value

    @model_validator(mode="after")
    def validate_version_invariants(self) -> "AudioVersion":
        if self.parent_version_id == self.version_id:
            raise ValueError("a version cannot be its own parent")
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must not be earlier than created_at")
        if bool(self.treatment_plan_id) != bool(self.treatment_variant_id):
            raise ValueError(
                "treatment_plan_id and treatment_variant_id must appear together"
            )
        if self.status in {VersionStatus.REJECTED, VersionStatus.APPROVED}:
            if self.approval is None:
                raise ValueError(f"{self.status.value} requires approval evidence")
        if self.status is VersionStatus.DELIVERED:
            if self.approval is None:
                raise ValueError(f"{self.status.value} requires approval evidence")
        if self.status is VersionStatus.REJECTED:
            if self.approval.outcome not in {
                ApprovalOutcome.REJECTED,
                ApprovalOutcome.RETURNED,
            }:
                raise ValueError(
                    "REJECTED status requires a rejected or returned decision"
                )
        if self.status in {
            VersionStatus.APPROVED,
            VersionStatus.DELIVERED,
        }:
            if self.approval.outcome is not ApprovalOutcome.APPROVED:
                raise ValueError(
                    f"{self.status.value} requires an approved decision"
                )
        if self.approval is not None and self.approval.decided_at < self.created_at:
            raise ValueError("approval cannot predate version creation")
        if self.approval is not None:
            if self.approval.project_id != self.project_id:
                raise ValueError("approval project_id must match version project_id")
            if self.approval.version_id != self.version_id:
                raise ValueError("approval version_id must match version_id")
        return self

    def transition_to(
        self,
        new_status: VersionStatus,
        *,
        at: datetime | None = None,
        approval: ApprovalDecision | None = None,
    ) -> "AudioVersion":
        """Return a new status snapshot without changing audio identity."""

        if new_status not in ALLOWED_VERSION_TRANSITIONS[self.status]:
            raise ValueError(
                f"illegal version transition: {self.status.value} -> "
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
        if approval is not None:
            data["approval"] = approval
        return AudioVersion.model_validate(data)
