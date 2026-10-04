"""Canonical Song Project records (``moodify.project/0.1``).

A Song Project is the long-lived working object of a production. It owns its
source audio and reserves a canonical place for every capability that will
attach to it later.

Project Model 0.1 is deliberately narrow: it creates the project, records the
source as a hashed asset, and can reopen and re-verify it. The reserved
sections below carry no schema yet — they exist so later tasks have a defined
home rather than inventing one.
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any, Literal

from pydantic import Field, field_validator, model_validator

from moodify.compat import StrEnum

from ..contracts.base import CanonicalModel, ensure_json_safe, freeze_json_value
from ..contracts.hashing import validate_sha256
from ..contracts.ids import validate_id

#: Persisted project protocol. Distinct from ``schema_version`` (the canonical
#: contract schema, currently ``1.0``): they version different things and must
#: not be conflated.
PROJECT_PROTOCOL = "moodify.project/0.1"

#: Domains reserved for future capabilities. Empty in Project Model 0.1 — this
#: task defines their *place*, not their contents.
RESERVED_SECTIONS = (
    "stems",
    "analysis",
    "transcription",
    "score",
    "edits",
    "session",
    "renders",
    "verification",
    "exports",
    "provenance",
)


class AssetKind(StrEnum):
    """What an asset *is* within a project."""

    SOURCE = "source"


class ProjectAsset(CanonicalModel):
    """A project-owned file, addressed by a project-relative logical path.

    Canonical project records never store absolute paths: a project must stay
    relocatable, and a persisted path must never be able to name a file outside
    the project directory.
    """

    asset_id: str
    kind: AssetKind
    logical_path: str
    original_name: str
    media_type: str
    content_hash: str
    size_bytes: int = Field(ge=0)

    @field_validator("asset_id")
    @classmethod
    def require_asset_id(cls, value: str) -> str:
        return validate_id(value, "asset")

    @field_validator("original_name", "media_type")
    @classmethod
    def require_non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("field must be non-empty")
        return value

    @field_validator("logical_path")
    @classmethod
    def require_project_relative(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("logical_path must be non-empty")
        if "\\" in value:
            raise ValueError("logical_path must use POSIX separators")
        path = PurePosixPath(value)
        if path.is_absolute():
            raise ValueError("logical_path must be project-relative")
        if ".." in path.parts:
            raise ValueError("logical_path must not traverse outside the project")
        return value

    @field_validator("content_hash")
    @classmethod
    def require_digest(cls, value: str) -> str:
        return validate_sha256(value)


class ProjectManifest(CanonicalModel):
    """The canonical ``project.json`` record."""

    protocol: Literal["moodify.project/0.1"] = PROJECT_PROTOCOL
    project_id: str
    display_name: str | None = None
    source: ProjectAsset
    assets: dict[str, str] = Field(default_factory=dict)
    stems: dict[str, Any] = Field(default_factory=dict)
    analysis: dict[str, Any] = Field(default_factory=dict)
    transcription: dict[str, Any] = Field(default_factory=dict)
    score: dict[str, Any] = Field(default_factory=dict)
    edits: dict[str, Any] = Field(default_factory=dict)
    session: dict[str, Any] = Field(default_factory=dict)
    renders: dict[str, Any] = Field(default_factory=dict)
    verification: dict[str, Any] = Field(default_factory=dict)
    exports: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)

    @field_validator("project_id")
    @classmethod
    def require_project_id(cls, value: str) -> str:
        return validate_id(value, "project")

    @field_validator("assets")
    @classmethod
    def require_asset_references(cls, value: dict[str, str]) -> dict[str, Any]:
        ensure_json_safe(value)
        checked = {role: validate_id(asset_id, "asset") for role, asset_id in value.items()}
        return freeze_json_value(checked)

    @field_validator(*RESERVED_SECTIONS)
    @classmethod
    def require_json_safe(cls, value: dict[str, Any]) -> dict[str, Any]:
        ensure_json_safe(value)
        return freeze_json_value(value)

    @model_validator(mode="after")
    def require_source_binding(self) -> "ProjectManifest":
        if self.source.kind is not AssetKind.SOURCE:
            raise ValueError("the project source must be a source-kind asset")
        if self.assets.get("source") != self.source.asset_id:
            raise ValueError("assets['source'] must reference the manifest's source asset")
        return self
