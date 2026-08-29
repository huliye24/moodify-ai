"""Machine Finding contract — what the Ear may and may not conclude.

MFY_EAR_MEASUREMENT_CONTRACT_001: first-phase conclusions must be observable
phenomena. Aesthetic/product conclusions are explicitly forbidden.

科学边界（37 号审计确认）：
允许：可测量现象（能量/事件/动态/瞬态/相关性/基线偏差/证据冲突/超域/证据不足）。
禁止：SOUNDS_BETTER、PRODUCTION_APPROVED、HIGH_QUALITY_MUSIC、
COPYRIGHT_VALID、单一综合音质分。
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import Field, field_validator

from .base import CanonicalModel, ensure_json_safe, freeze_json_value
from .ids import validate_id


class FindingType(str, Enum):
    ENERGY_CHANGE = "ENERGY_CHANGE"
    CLIPPING_EVENT = "CLIPPING_EVENT"
    TRUE_PEAK_EVENT = "TRUE_PEAK_EVENT"
    DYNAMIC_CHANGE = "DYNAMIC_CHANGE"
    TRANSIENT_CHANGE = "TRANSIENT_CHANGE"
    CORRELATION_CHANGE = "CORRELATION_CHANGE"
    BASELINE_DEVIATION = "BASELINE_DEVIATION"
    EVIDENCE_CONFLICT = "EVIDENCE_CONFLICT"
    OUT_OF_DOMAIN = "OUT_OF_DOMAIN"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


FORBIDDEN_CONCLUSIONS = {
    "SOUNDS_BETTER",
    "PRODUCTION_APPROVED",
    "HIGH_QUALITY_MUSIC",
    "COPYRIGHT_VALID",
    "OVERALL_QUALITY_SCORE",
}


class MachineFinding(CanonicalModel):
    finding_id: str
    case_id: str
    finding_type: FindingType
    measurement_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    domain: str  # e.g. "wse/loudness", "mse/segmentation", "ppe"
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    uncertainty_note: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("finding_id")
    @classmethod
    def require_finding_id(cls, value: str) -> str:
        return validate_id(value, "finding")

    @field_validator("case_id")
    @classmethod
    def require_case_id(cls, value: str) -> str:
        return validate_id(value, "case")

    @field_validator("domain")
    @classmethod
    def require_domain(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("domain must be non-empty")
        return value

    @field_validator("measurement_ids")
    @classmethod
    def require_measurement_ids(cls, value: list[str]) -> list[str]:
        return [validate_id(v, "meas") for v in value]

    @field_validator("evidence_ids")
    @classmethod
    def require_evidence_ids(cls, value: list[str]) -> list[str]:
        return [validate_id(v, "evid") for v in value]

    @field_validator("metadata")
    @classmethod
    def require_json_safe_metadata(cls, value: dict[str, Any]) -> dict[str, Any]:
        ensure_json_safe(value)
        return freeze_json_value(value)
