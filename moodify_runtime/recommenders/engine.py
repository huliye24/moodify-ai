"""Recommendation Engine — orchestrate all four loop recommenders.

MHP-819: Recommendation Engine Tests
MHP-820: Recommendation Gate Report

Usage:
    from moodify_runtime.recommenders import RecommendationEngine

    engine = RecommendationEngine()
    bundle = engine.run(night_metric_record)
    # bundle contains all recommendations + operator gate decision
"""

from __future__ import annotations

from typing import Any

from moodify_runtime.recommenders.base import Recommendation, RecommendationBundle
from moodify_runtime.recommenders.score_disagreement import ScoreDisagreementRecommender
from moodify_runtime.recommenders.penalty_preset import PenaltyPresetRecommender
from moodify_runtime.recommenders.runtime_reliability import RuntimeReliabilityRecommender
from moodify_runtime.recommenders.operator_next_mhp import OperatorNextMhpWriter
from moodify_runtime.utils import utc_now_iso


class RecommendationEngine:
    """Run all four loop recommenders against a NightMetricRecord.

    Usage:
        engine = RecommendationEngine()
        bundle = engine.run(record)
        # Access by loop: bundle.by_loop("scoring_calibration")
        # Access severity: bundle.high_severity
    """

    def __init__(self):
        self._score_rec = ScoreDisagreementRecommender()
        self._penalty_rec = PenaltyPresetRecommender()
        self._runtime_rec = RuntimeReliabilityRecommender()
        self._operator_writer = OperatorNextMhpWriter()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, record: dict[str, Any]) -> RecommendationBundle:
        """Run all recommenders and return the full bundle with operator decision."""
        tasks = record.get("tasks", [])
        runtime_sig = record.get("runtime", {})
        # Embed run_id into runtime_sig for the recommender
        runtime_sig = {**runtime_sig, "run_id": record.get("run_id", "")}

        recommendations: list[Recommendation] = []

        # Loop A: Runtime Reliability
        recommendations.extend(
            self._runtime_rec.analyze(runtime_sig, tasks)
        )

        # Loop B: Scoring Calibration
        recommendations.extend(
            self._score_rec.analyze(tasks)
        )

        # Loop C: Craft/Preset Selection
        recommendations.extend(
            self._penalty_rec.analyze(tasks)
        )

        # Loop D: Operator Report — runs last, wraps everything
        bundle = self._operator_writer.decide(record, recommendations)
        return bundle


# ------------------------------------------------------------------
# Convenience function
# ------------------------------------------------------------------

def generate_recommendations(record: dict[str, Any]) -> RecommendationBundle:
    """One-call convenience: generate recommendations from a NightMetricRecord."""
    engine = RecommendationEngine()
    return engine.run(record)
