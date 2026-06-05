"""Optimization recommenders — turn validated data-loop decisions into executable actions.

Part of ECHAIN-MOODIFY-DATA-LOOP-014 / Build NEM-043.

Each recommender analyzes one optimization loop's signals and produces typed,
executable recommendations with severity, owner, and next-action text.
"""

from moodify_runtime.recommenders.base import Recommendation, RecommendationBundle
from moodify_runtime.recommenders.score_disagreement import ScoreDisagreementRecommender
from moodify_runtime.recommenders.penalty_preset import PenaltyPresetRecommender
from moodify_runtime.recommenders.runtime_reliability import RuntimeReliabilityRecommender
from moodify_runtime.recommenders.operator_next_mhp import OperatorNextMhpWriter
from moodify_runtime.recommenders.engine import RecommendationEngine

__all__ = [
    "Recommendation",
    "RecommendationBundle",
    "ScoreDisagreementRecommender",
    "PenaltyPresetRecommender",
    "RuntimeReliabilityRecommender",
    "OperatorNextMhpWriter",
    "RecommendationEngine",
]
