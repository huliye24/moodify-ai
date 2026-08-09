"""N-track ranking policy (DSK-MFY-NTRACK-RANKER-001).

All comparison budgets, quality-gate rules, tie handling, album-aware
weights and estimator parameters live in one versioned YAML so that the
ranking behavior is auditable and testable. The dataclass defaults are a
fallback only; production callers load the YAML.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_POLICY_PATH = Path(__file__).resolve().parents[4] / "configs" / "ntrack_policy_v1.yaml"


@dataclass(frozen=True)
class RankingPolicy:
    version: str = "ntrack_policy_v1"
    small_batch_max: int = 15
    medium_batch_max: int = 100
    small_batch_pairs_ratio: float = 1.0
    medium_batch_pairs_per_candidate: int = 4
    large_batch_pairs_per_candidate: int = 3
    top_k_refinement_pairs_per_boundary_candidate: int = 3
    refinement_boundary_radius: int = 2
    allow_tie_bands: bool = True
    minimum_rank_separation: float = 10.0
    exclude_invalid_source: bool = True
    exclude_analysis_failed: bool = True
    severe_failure_requires_review: bool = True
    review_clipping_ratio_threshold: float = 0.05
    review_silence_ratio_threshold: float = 0.90
    album_rerank_enabled: bool = True
    album_quality_floor_required: bool = True
    redundancy_penalty_enabled: bool = True
    redundancy_penalty_weight: float = 0.25
    diversity_bonus_enabled: bool = True
    diversity_bonus_weight: float = 0.20
    elo_base_k: float = 40.0
    elo_initial_score: float = 1000.0
    confidence_weight: dict[str, float] = field(
        default_factory=lambda: {"LOW": 0.6, "MEDIUM": 0.8, "HIGH": 1.0}
    )

    @classmethod
    def from_yaml(cls, path: str | Path = DEFAULT_POLICY_PATH) -> "RankingPolicy":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        budget = data.get("comparison_budget", {})
        uncertainty = data.get("uncertainty", {})
        gate = data.get("quality_gate", {})
        album = data.get("album_rerank", {})
        estimator = data.get("estimator", {})
        return cls(
            version=data.get("policy_version", "ntrack_policy_v1"),
            small_batch_max=int(data.get("small_batch_max", 15)),
            medium_batch_max=int(data.get("medium_batch_max", 100)),
            small_batch_pairs_ratio=float(budget.get("small_batch_pairs_ratio", 1.0)),
            medium_batch_pairs_per_candidate=int(budget.get("medium_batch_pairs_per_candidate", 4)),
            large_batch_pairs_per_candidate=int(budget.get("large_batch_pairs_per_candidate", 3)),
            top_k_refinement_pairs_per_boundary_candidate=int(
                budget.get("top_k_refinement_pairs_per_boundary_candidate", 3)
            ),
            refinement_boundary_radius=int(budget.get("refinement_boundary_radius", 2)),
            allow_tie_bands=bool(uncertainty.get("allow_tie_bands", True)),
            minimum_rank_separation=float(uncertainty.get("minimum_rank_separation", 10.0)),
            exclude_invalid_source=bool(gate.get("exclude_invalid_source", True)),
            exclude_analysis_failed=bool(gate.get("exclude_analysis_failed", True)),
            severe_failure_requires_review=bool(gate.get("severe_failure_requires_review", True)),
            review_clipping_ratio_threshold=float(gate.get("review_clipping_ratio_threshold", 0.05)),
            review_silence_ratio_threshold=float(gate.get("review_silence_ratio_threshold", 0.90)),
            album_rerank_enabled=bool(album.get("enabled", True)),
            album_quality_floor_required=bool(album.get("quality_floor_required", True)),
            redundancy_penalty_enabled=bool(album.get("redundancy_penalty_enabled", True)),
            redundancy_penalty_weight=float(album.get("redundancy_penalty_weight", 0.25)),
            diversity_bonus_enabled=bool(album.get("diversity_bonus_enabled", True)),
            diversity_bonus_weight=float(album.get("diversity_bonus_weight", 0.20)),
            elo_base_k=float(estimator.get("elo_base_k", 40.0)),
            elo_initial_score=float(estimator.get("elo_initial_score", 1000.0)),
            confidence_weight=dict(estimator.get("confidence_weight", {"LOW": 0.6, "MEDIUM": 0.8, "HIGH": 1.0})),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_version": self.version,
            "small_batch_max": self.small_batch_max,
            "medium_batch_max": self.medium_batch_max,
            "comparison_budget": {
                "small_batch_pairs_ratio": self.small_batch_pairs_ratio,
                "medium_batch_pairs_per_candidate": self.medium_batch_pairs_per_candidate,
                "large_batch_pairs_per_candidate": self.large_batch_pairs_per_candidate,
                "top_k_refinement_pairs_per_boundary_candidate": (
                    self.top_k_refinement_pairs_per_boundary_candidate
                ),
                "refinement_boundary_radius": self.refinement_boundary_radius,
            },
            "uncertainty": {
                "allow_tie_bands": self.allow_tie_bands,
                "minimum_rank_separation": self.minimum_rank_separation,
            },
            "quality_gate": {
                "exclude_invalid_source": self.exclude_invalid_source,
                "exclude_analysis_failed": self.exclude_analysis_failed,
                "severe_failure_requires_review": self.severe_failure_requires_review,
                "review_clipping_ratio_threshold": self.review_clipping_ratio_threshold,
                "review_silence_ratio_threshold": self.review_silence_ratio_threshold,
            },
            "album_rerank": {
                "enabled": self.album_rerank_enabled,
                "quality_floor_required": self.album_quality_floor_required,
                "redundancy_penalty_enabled": self.redundancy_penalty_enabled,
                "redundancy_penalty_weight": self.redundancy_penalty_weight,
                "diversity_bonus_enabled": self.diversity_bonus_enabled,
                "diversity_bonus_weight": self.diversity_bonus_weight,
            },
            "estimator": {
                "elo_base_k": self.elo_base_k,
                "elo_initial_score": self.elo_initial_score,
                "confidence_weight": dict(self.confidence_weight),
            },
        }

    def comparison_budget_for(self, n_candidates: int) -> dict[str, Any]:
        """Staged pair budget: exhaustive for small batches, capped for larger."""
        all_pairs = n_candidates * (n_candidates - 1) // 2
        if n_candidates <= self.small_batch_max:
            pairs = int(all_pairs * self.small_batch_pairs_ratio)
            budget_name = "small_batch_exhaustive"
        elif n_candidates <= self.medium_batch_max:
            pairs = min(all_pairs, n_candidates * self.medium_batch_pairs_per_candidate)
            budget_name = "medium_batch_capped"
        else:
            pairs = min(all_pairs, n_candidates * self.large_batch_pairs_per_candidate)
            budget_name = "large_batch_capped"
        return {
            "budget_name": budget_name,
            "max_pairs": max(pairs, n_candidates),
            "all_pairs": all_pairs,
            "fraction_of_all_pairs": round(pairs / all_pairs, 4) if all_pairs else 0.0,
        }
