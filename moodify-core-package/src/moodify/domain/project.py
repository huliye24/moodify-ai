"""Project aggregate models for Moodify Studio Workspace v2."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .creative_brief import CreativeBrief


AUDIO_PROJECT_SCHEMA_VERSION = "audio_project.v1"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ProjectStatus(str, Enum):
    """Persisted lifecycle states for an audio craft project."""

    CREATED = "CREATED"
    BRIEFING = "BRIEFING"
    ANALYZING = "ANALYZING"
    DESIGNING = "DESIGNING"
    PROCESSING = "PROCESSING"
    REVIEWING = "REVIEWING"
    AWAITING_USER = "AWAITING_USER"
    APPROVED = "APPROVED"
    DELIVERED = "DELIVERED"
    ARCHIVED = "ARCHIVED"
    FAILED = "FAILED"


class LegacyReference(BaseModel):
    """Traceability pointer to a source record that remains read-only."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    source_type: str = Field(min_length=1)
    legacy_id: str = Field(min_length=1)
    source_path: str | None = None
    source_hash: str | None = None

    @property
    def migration_key(self) -> str:
        """Stable, human-auditable input for an idempotent migration key."""

        return ":".join(
            (self.source_type, self.legacy_id, self.source_hash or "unhashed")
        )


class AudioProject(BaseModel):
    """Top-level aggregate for one song and its complete craft history."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=False,
    )

    schema_version: Literal["audio_project.v1"] = AUDIO_PROJECT_SCHEMA_VERSION
    project_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    status: ProjectStatus = ProjectStatus.CREATED
    source_audio_ids: list[str] = Field(min_length=1)
    creative_brief: CreativeBrief | None = None
    active_version_id: str | None = None
    approved_version_id: str | None = None
    delivered_version_id: str | None = None
    commercial_project_id: str | None = None
    legacy_refs: list[LegacyReference] = Field(default_factory=list)
    privacy_policy: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)

    @field_validator("source_audio_ids")
    @classmethod
    def source_audio_ids_must_be_unique(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value]
        if any(not item for item in normalized):
            raise ValueError("source_audio_ids must not contain blank identifiers")
        if len(normalized) != len(set(normalized)):
            raise ValueError("source_audio_ids must be unique")
        return normalized

    @field_validator("created_at", "updated_at")
    @classmethod
    def timestamps_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("project timestamps must be timezone-aware")
        return value

    @model_validator(mode="after")
    def validate_project_invariants(self) -> "AudioProject":
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must not be earlier than created_at")

        if self.status in {
            ProjectStatus.APPROVED,
            ProjectStatus.DELIVERED,
            ProjectStatus.ARCHIVED,
        } and not self.approved_version_id:
            raise ValueError(
                f"{self.status.value} projects require approved_version_id"
            )

        if self.status is ProjectStatus.DELIVERED:
            if not self.delivered_version_id:
                raise ValueError("DELIVERED projects require delivered_version_id")
            if self.delivered_version_id != self.approved_version_id:
                raise ValueError(
                    "delivered_version_id must equal approved_version_id"
                )

        return self
