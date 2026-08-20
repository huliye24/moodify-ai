"""Canonical structured observation contract."""

from typing import Any

from pydantic import Field, field_validator

from .base import CanonicalModel, ensure_json_safe, freeze_json_value
from .ids import validate_id
from .provenance import Provenance


class MeasurementRecord(CanonicalModel):
    measurement_id: str
    case_id: str
    source_id: str
    namespace: str
    name: str
    value: Any
    unit: str
    provenance: Provenance
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    window: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("measurement_id")
    @classmethod
    def require_measurement_id(cls, value: str) -> str:
        return validate_id(value, "meas")

    @field_validator("case_id")
    @classmethod
    def require_case_id(cls, value: str) -> str:
        return validate_id(value, "case")

    @field_validator("source_id", "namespace", "name", "unit")
    @classmethod
    def require_non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("field must be non-empty")
        return value

    @field_validator("value", "window", "metadata")
    @classmethod
    def require_json_safe(cls, value: Any) -> Any:
        ensure_json_safe(value)
        return freeze_json_value(value)
