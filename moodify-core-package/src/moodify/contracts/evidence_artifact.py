"""Canonical durable evidence artifact contract."""

from typing import Any

from pydantic import Field, field_validator

from .base import CanonicalModel, ensure_json_safe, freeze_json_value
from .hashing import validate_sha256
from .ids import validate_id
from .provenance import Provenance


class EvidenceArtifact(CanonicalModel):
    evidence_id: str
    case_id: str
    source_id: str | None = None
    artifact_type: str
    media_type: str
    content_hash: str
    size_bytes: int | None = Field(default=None, ge=0)
    provenance: Provenance
    uri: str | None = None
    logical_path: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("evidence_id")
    @classmethod
    def require_evidence_id(cls, value: str) -> str:
        return validate_id(value, "evid")

    @field_validator("case_id")
    @classmethod
    def require_case_id(cls, value: str) -> str:
        return validate_id(value, "case")

    @field_validator("artifact_type", "media_type")
    @classmethod
    def require_non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("field must be non-empty")
        return value

    @field_validator("content_hash")
    @classmethod
    def require_digest(cls, value: str) -> str:
        return validate_sha256(value)

    @field_validator("metadata")
    @classmethod
    def require_json_safe(cls, value: dict[str, Any]) -> dict[str, Any]:
        ensure_json_safe(value)
        return freeze_json_value(value)
