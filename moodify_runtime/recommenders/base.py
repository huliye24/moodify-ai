"""Base types for the recommendation engine.

All recommenders produce Recommendation objects. The RecommendationBundle
collects outputs from all four recommenders into a single actionable list.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Recommendation:
    """One concrete, executable optimization action.

    This is the output type used by all four loop recommenders and matches
    the DeepSeek worker output schema so validated model outputs can be
    fed through the same pipeline.
    """
    task_id: str
    loop: str  # runtime_reliability | scoring_calibration | craft_preset_selection | operator_report
    severity: str  # low | medium | high
    reason: str = ""
    next_action: str = ""
    needs_human_review: bool = False
    # Additional fields for traceability
    source_signal: str = ""          # which signal triggered this recommendation
    owner_subsystem: str = ""        # which subsystem should execute the action
    estimated_effort: str = "S"      # S | M | L | XL

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RecommendationBundle:
    """Collected recommendations from all four loops."""
    run_id: str = ""
    generated_at: str = ""
    recommendations: list[Recommendation] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    @property
    def high_severity(self) -> list[Recommendation]:
        return [r for r in self.recommendations if r.severity == "high"]

    @property
    def needs_review(self) -> list[Recommendation]:
        return [r for r in self.recommendations if r.needs_human_review]

    def by_loop(self, loop: str) -> list[Recommendation]:
        return [r for r in self.recommendations if r.loop == loop]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "generated_at": self.generated_at,
            "recommendations": [r.to_dict() for r in self.recommendations],
            "summary": self.summary,
        }
