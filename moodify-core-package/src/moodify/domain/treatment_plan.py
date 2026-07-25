"""Declarative treatment plans for Moodify Studio Workspace v2."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


TREATMENT_PLAN_SCHEMA_VERSION = "treatment_plan.v1"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TreatmentStepType(str, Enum):
    IMPORT = "IMPORT"
    STEM_SEPARATION = "STEM_SEPARATION"
    VOCAL_CORRECTION = "VOCAL_CORRECTION"
    NOISE_REDUCTION = "NOISE_REDUCTION"
    SPECTRAL_BALANCE = "SPECTRAL_BALANCE"
    DYNAMIC_SHAPING = "DYNAMIC_SHAPING"
    TRANSIENT_REPAIR = "TRANSIENT_REPAIR"
    SPACE_DESIGN = "SPACE_DESIGN"
    STEREO_CONTROL = "STEREO_CONTROL"
    STEM_MIX = "STEM_MIX"
    LOUDNESS_NORMALIZATION = "LOUDNESS_NORMALIZATION"
    TRUE_PEAK_LIMITING = "TRUE_PEAK_LIMITING"
    PLATFORM_EXPORT = "PLATFORM_EXPORT"
    QUALITY_REVIEW = "QUALITY_REVIEW"
    MANUAL_ADJUSTMENT = "MANUAL_ADJUSTMENT"
    APPROVAL = "APPROVAL"
    DELIVERY = "DELIVERY"


class TreatmentAction(BaseModel):
    """One ordered, public engineering intent inside a candidate plan."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    action_id: str = Field(min_length=1)
    order: int = Field(ge=1)
    step_type: TreatmentStepType
    public_summary: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    target_metrics: dict[str, float] = Field(default_factory=dict)
    parameter_bounds: dict[str, tuple[float, float]] = Field(default_factory=dict)
    prerequisites: list[str] = Field(default_factory=list)

    @field_validator("target_metrics")
    @classmethod
    def metric_names_must_be_nonblank(
        cls, value: dict[str, float]
    ) -> dict[str, float]:
        if any(not name.strip() for name in value):
            raise ValueError("target metric names must not be blank")
        return {name.strip(): target for name, target in value.items()}

    @field_validator("parameter_bounds")
    @classmethod
    def parameter_bounds_must_be_ordered(
        cls, value: dict[str, tuple[float, float]]
    ) -> dict[str, tuple[float, float]]:
        normalized: dict[str, tuple[float, float]] = {}
        for name, bounds in value.items():
            clean_name = name.strip()
            if not clean_name:
                raise ValueError("parameter boundary names must not be blank")
            if bounds[0] > bounds[1]:
                raise ValueError(
                    f"parameter boundary minimum exceeds maximum: {clean_name}"
                )
            normalized[clean_name] = bounds
        return normalized

    @field_validator("prerequisites")
    @classmethod
    def prerequisites_must_be_unique(
        cls, value: list[str]
    ) -> list[str]:
        normalized = [item.strip() for item in value]
        if any(not item for item in normalized):
            raise ValueError("prerequisites must not contain blank items")
        if len(normalized) != len(set(normalized)):
            raise ValueError("prerequisites must not contain duplicates")
        return normalized


class TreatmentVariant(BaseModel):
    """One independently executable A/B/C candidate."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    variant_id: str = Field(min_length=1)
    label: Literal["A", "B", "C"]
    name: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    problems: list[str] = Field(min_length=1)
    preserve: list[str] = Field(default_factory=list)
    actions: list[TreatmentAction] = Field(min_length=1)
    risks: list[str] = Field(min_length=1)
    expected_output: str = Field(min_length=1)
    target_metrics: dict[str, float] = Field(default_factory=dict)

    @field_validator("problems", "preserve", "risks")
    @classmethod
    def text_lists_must_be_nonblank_and_unique(
        cls, value: list[str]
    ) -> list[str]:
        normalized = [item.strip() for item in value]
        if any(not item for item in normalized):
            raise ValueError("variant lists must not contain blank items")
        comparison_keys = [item.casefold() for item in normalized]
        if len(comparison_keys) != len(set(comparison_keys)):
            raise ValueError("variant lists must not contain duplicate items")
        return normalized

    @model_validator(mode="after")
    def actions_must_have_unique_ids_and_contiguous_order(
        self,
    ) -> "TreatmentVariant":
        action_ids = [action.action_id for action in self.actions]
        if len(action_ids) != len(set(action_ids)):
            raise ValueError("action_id must be unique within a variant")
        orders = sorted(action.order for action in self.actions)
        if orders != list(range(1, len(self.actions) + 1)):
            raise ValueError("action order must be contiguous and start at 1")
        return self


class TreatmentPlan(BaseModel):
    """Persisted Design Thread output containing one to three candidates."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    schema_version: Literal["treatment_plan.v1"] = TREATMENT_PLAN_SCHEMA_VERSION
    plan_id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    brief_revision: int = Field(ge=1)
    diagnosis_id: str = Field(min_length=1)
    variants: list[TreatmentVariant] = Field(min_length=1, max_length=3)
    recommended_variant_id: str | None = None
    recommendation_reason: str | None = None
    created_by_thread_id: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=_utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("created_at")
    @classmethod
    def created_at_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")
        return value

    @model_validator(mode="after")
    def validate_candidate_set(self) -> "TreatmentPlan":
        variant_ids = [variant.variant_id for variant in self.variants]
        labels = [variant.label for variant in self.variants]
        if len(variant_ids) != len(set(variant_ids)):
            raise ValueError("variant_id must be unique within a plan")
        if len(labels) != len(set(labels)):
            raise ValueError("variant labels must be unique within a plan")
        expected_labels = ["A", "B", "C"][: len(labels)]
        if labels != expected_labels:
            raise ValueError("variant labels must be ordered from A")
        if self.recommended_variant_id is not None:
            if self.recommended_variant_id not in variant_ids:
                raise ValueError("recommended_variant_id must reference a variant")
            if not self.recommendation_reason:
                raise ValueError(
                    "a recommended variant requires recommendation_reason"
                )
        elif self.recommendation_reason is not None:
            raise ValueError(
                "recommendation_reason requires recommended_variant_id"
            )
        return self
