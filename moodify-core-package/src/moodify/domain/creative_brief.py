"""Creative intent model for Moodify Studio Workspace v2."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


CREATIVE_BRIEF_SCHEMA_VERSION = "creative_brief.v1"


class CreativeBrief(BaseModel):
    """Structured, user-editable creative direction for an audio project."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    schema_version: Literal["creative_brief.v1"] = CREATIVE_BRIEF_SCHEMA_VERSION
    goal: str = Field(min_length=1)
    preserve: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    platform: str = Field(min_length=1)
    reference: list[str] = Field(default_factory=list)

    @field_validator("preserve", "avoid", "reference")
    @classmethod
    def list_items_must_be_nonblank_and_unique(
        cls, value: list[str]
    ) -> list[str]:
        normalized = [item.strip() for item in value]
        if any(not item for item in normalized):
            raise ValueError("brief lists must not contain blank items")

        comparison_keys = [item.casefold() for item in normalized]
        if len(comparison_keys) != len(set(comparison_keys)):
            raise ValueError("brief lists must not contain duplicate items")
        return normalized

    @model_validator(mode="after")
    def preserve_and_avoid_must_not_conflict(self) -> "CreativeBrief":
        preserve_keys = {item.casefold() for item in self.preserve}
        avoid_keys = {item.casefold() for item in self.avoid}
        conflicts = sorted(preserve_keys & avoid_keys)
        if conflicts:
            raise ValueError(
                "preserve and avoid must not contain the same item: "
                + ", ".join(conflicts)
            )
        return self
