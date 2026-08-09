"""Recommendation policy (DSK-MFY-TASTE-FEED-PATCH-001).

Scoring weights, feedback event weights, exploration budget, quality
gates, and taste update rates all live in one versioned YAML so the
pipeline is experiment-ready.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_POLICY_PATH = Path(__file__).resolve().parents[3] / "configs" / "recommendation_policy_v1.yaml"


@dataclass(frozen=True)
class RecommendationPolicy:
    version: str = "recommendation_policy_v1"
    candidate_pool_size: int = 20
    default_feed_size: int = 10
    exploration_fraction: float = 0.20
    freshness_window_days: int = 30
    session_repetition_limit: int = 1
    scoring_weights: dict[str, float] = field(
        default_factory=lambda: {
            "preference_match": 1.0, "novelty_bonus": 0.15, "diversity_bonus": 0.20,
            "transition_coherence": 0.10, "quality_confidence": 0.25,
        }
    )
    feedback_weights: dict[str, float] = field(
        default_factory=lambda: {
            "IMPRESSION": 0.0, "PLAY_START": 0.10, "COMPLETION": 0.40, "REPLAY": 0.60,
            "LIKE": 0.80, "SAVE": 1.00, "SKIP_HARD": -0.80, "SKIP_SOFT": -0.30,
        }
    )
    long_term_alpha: float = 0.05
    short_term_alpha: float = 0.30
    novelty_tolerance_start: float = 0.20
    novelty_tolerance_step: float = 0.05
    novelty_tolerance_max: float = 0.60
    safe_broad_recommendation: bool = True
    quality_floor_required: bool = True

    @classmethod
    def from_yaml(cls, path: str | Path = DEFAULT_POLICY_PATH) -> "RecommendationPolicy":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        pipeline = data.get("pipeline", {})
        weights = data.get("scoring_weights", {})
        feedback = data.get("feedback_weights", {})
        taste = data.get("taste", {})
        cold = data.get("cold_start", {})
        return cls(
            version=data.get("policy_version", "recommendation_policy_v1"),
            candidate_pool_size=int(pipeline.get("candidate_pool_size", 20)),
            default_feed_size=int(pipeline.get("default_feed_size", 10)),
            exploration_fraction=float(pipeline.get("exploration_fraction", 0.20)),
            freshness_window_days=int(pipeline.get("freshness_window_days", 30)),
            session_repetition_limit=int(pipeline.get("session_repetition_limit", 1)),
            scoring_weights={k: float(v) for k, v in weights.items()},
            feedback_weights={k: float(v) for k, v in feedback.items()},
            long_term_alpha=float(taste.get("long_term_alpha", 0.05)),
            short_term_alpha=float(taste.get("short_term_alpha", 0.30)),
            novelty_tolerance_start=float(taste.get("novelty_tolerance_start", 0.20)),
            novelty_tolerance_step=float(taste.get("novelty_tolerance_step", 0.05)),
            novelty_tolerance_max=float(taste.get("novelty_tolerance_max", 0.60)),
            safe_broad_recommendation=bool(cold.get("safe_broad_recommendation", True)),
            quality_floor_required=bool(cold.get("quality_floor_required", True)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_version": self.version,
            "pipeline": {
                "candidate_pool_size": self.candidate_pool_size,
                "default_feed_size": self.default_feed_size,
                "exploration_fraction": self.exploration_fraction,
                "freshness_window_days": self.freshness_window_days,
                "session_repetition_limit": self.session_repetition_limit,
            },
            "scoring_weights": dict(self.scoring_weights),
            "feedback_weights": dict(self.feedback_weights),
            "taste": {
                "long_term_alpha": self.long_term_alpha,
                "short_term_alpha": self.short_term_alpha,
                "novelty_tolerance_start": self.novelty_tolerance_start,
                "novelty_tolerance_step": self.novelty_tolerance_step,
                "novelty_tolerance_max": self.novelty_tolerance_max,
            },
            "cold_start": {
                "safe_broad_recommendation": self.safe_broad_recommendation,
                "quality_floor_required": self.quality_floor_required,
            },
        }
