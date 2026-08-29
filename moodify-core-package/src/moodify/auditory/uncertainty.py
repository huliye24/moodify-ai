"""Uncertainty taxonomy (MFY-PHASE1-DEPTH-004).

A bounded machine-readable vocabulary explaining WHY a conclusion is
uncertain. No uncertainty reason outside this set may appear in
authoritative output.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

UNCERTAINTY_REASONS = {
    "MEASUREMENT_UNCERTAINTY",
    "TEMPORAL_UNCERTAINTY",
    "PROFILE_UNCERTAINTY",
    "EVIDENCE_INCOMPLETE",
    "CONFLICTING_EVIDENCE",
    "OUT_OF_SCOPE",
    "VALIDATION_LIMIT",
}


@dataclass(frozen=True)
class Uncertainty:
    reason: str
    detail: str = ""

    def __post_init__(self) -> None:
        if self.reason not in UNCERTAINTY_REASONS:
            raise ValueError(f"unknown uncertainty reason: {self.reason}")

    def to_dict(self) -> dict[str, Any]:
        return {"reason": self.reason, "detail": self.detail}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Uncertainty":
        return cls(reason=data["reason"], detail=data.get("detail", ""))
