"""Shared producer and method provenance."""

from pydantic import BaseModel, ConfigDict, field_validator

from .hashing import validate_sha256


class Provenance(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    producer: str
    producer_version: str
    method: str
    method_version: str
    parameters_hash: str

    @field_validator("producer", "producer_version", "method", "method_version")
    @classmethod
    def require_non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("provenance fields must be non-empty")
        return value

    @field_validator("parameters_hash")
    @classmethod
    def require_digest(cls, value: str) -> str:
        return validate_sha256(value)
