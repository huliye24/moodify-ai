"""MHP-819: Recommendation Engine Tests.

Covers:
  - ScoreDisagreementRecommender: severity classification, action generation
  - PenaltyPresetRecommender: flag parsing, preset policy actions
  - RuntimeReliabilityRecommender: fatal error pattern matching, failure analysis
  - OperatorNextMhpWriter: PASS/HOLD/REWORK decisions, bundle construction
  - RecommendationEngine: end-to-end orchestration, integration
"""

from __future__ import annotations

import pytest

from moodify_runtime.recommenders.base import Recommendation, RecommendationBundle
from moodify_runtime.recommenders.score_disagreement import ScoreDisagreementRecommender
from moodify_runtime.recommenders.penalty_preset import PenaltyPresetRecommender
from moodify_runtime.recommenders.runtime_reliability import RuntimeReliabilityRecommender
from moodify_runtime.recommenders.operator_next_mhp import OperatorNextMhpWriter
from moodify_runtime.recommenders.engine import RecommendationEngine


# ═══════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def disagreement_tasks():
    return [
        {
            "task_id": "TASK_A_warm_vocal", "sample_id": "SMP_A",
            "preset": "warm_vocal",
            "pseudo_delta_mrs": -20.0, "delta_mrs_open_v031": 83.0,
            "score_direction_disagreement": True, "mrs_open_flags": "",
        },
        {
            "task_id": "TASK_B_clean_master", "sample_id": "SMP_B",
            "preset": "clean_master",
            "pseudo_delta_mrs": 1.7, "delta_mrs_open_v031": -0.1,
            "score_direction_disagreement": True, "mrs_open_flags": "over_dark",
        },
        {
            "task_id": "TASK_C_ok", "sample_id": "SMP_C",
            "preset": "bright_master",
            "pseudo_delta_mrs": 5.0, "delta_mrs_open_v031": 4.5,
            "score_direction_disagreement": False, "mrs_open_flags": "",
        },
    ]


@pytest.fixture
def flagged_tasks():
    return [
        {
            "task_id": "TASK_X", "sample_id": "SMP_X",
            "preset": "wide_space", "delta_mrs_open_v031": -7.4,
            "mrs_open_flags": "over_dark",
        },
        {
            "task_id": "TASK_Y", "sample_id": "SMP_Y",
            "preset": "clean_master", "delta_mrs_open_v031": -0.1,
            "mrs_open_flags": "over_dark",
        },
        {
            "task_id": "TASK_Z_clean", "sample_id": "SMP_Z",
            "preset": "warm_vocal", "delta_mrs_open_v031": 5.0,
            "mrs_open_flags": "",
        },
    ]


@pytest.fixture
def night_metric_record():
    return {
        "run_id": "20260605_test",
        "started_at": "2026-06-05T00:01:41Z",
        "runtime": {
            "success": 4, "failed": 0, "total_selected": 4,
            "fatal_error": None, "missing_artifacts": [],
        },
        "scoring": {
            "task_count": 4, "disagreement_count": 2,
            "agreement_rate": 0.5, "disagreeing_presets": ["warm_vocal", "wide_space"],
        },
        "craft": {
            "task_count": 4, "flagged_count": 2, "flag_rate": 0.5,
            "flag_types": ["over_dark"],
        },
        "tasks": [
            {
                "task_id": "TASK_1", "sample_id": "SMP_1", "preset": "warm_vocal",
                "status": "done", "pseudo_delta_mrs": -20.0,
                "delta_mrs_open_v031": 83.0, "score_direction_disagreement": True,
                "mrs_open_flags": "",
            },
            {
                "task_id": "TASK_2", "sample_id": "SMP_2", "preset": "wide_space",
                "status": "done", "pseudo_delta_mrs": -18.0,
                "delta_mrs_open_v031": 82.0, "score_direction_disagreement": True,
                "mrs_open_flags": "over_dark",
            },
        ],
    }


# ═══════════════════════════════════════════════════════════════════════
# MHP-815: ScoreDisagreementRecommender
# ═══════════════════════════════════════════════════════════════════════


class TestScoreDisagreementRecommender:

    def test_only_disagreeing_tasks_analyzed(self, disagreement_tasks):
        rec = ScoreDisagreementRecommender()
        results = rec.analyze(disagreement_tasks)
        # Only 2 of 3 tasks have disagreement
        assert len(results) == 2

    def test_high_severity_large_disagreement(self, disagreement_tasks):
        rec = ScoreDisagreementRecommender()
        results = rec.analyze(disagreement_tasks)
        # TASK_A: pseudo -20 vs open +83 → high
        r = next(r for r in results if "warm_vocal" in r.task_id)
        assert r.severity == "high"
        assert r.needs_human_review is True

    def test_low_severity_small_disagreement(self, disagreement_tasks):
        rec = ScoreDisagreementRecommender()
        results = rec.analyze(disagreement_tasks)
        # TASK_B: pseudo +1.7 vs open -0.1 → low
        r = next(r for r in results if "clean_master" in r.task_id)
        assert r.severity == "low"

    def test_reason_includes_deltas(self, disagreement_tasks):
        rec = ScoreDisagreementRecommender()
        results = rec.analyze(disagreement_tasks)
        r = results[0]
        assert "+" in r.reason or "-" in r.reason
        assert len(r.reason) <= 180

    def test_next_action_under_limit(self, disagreement_tasks):
        rec = ScoreDisagreementRecommender()
        results = rec.analyze(disagreement_tasks)
        for r in results:
            assert len(r.next_action) <= 220

    def test_no_disagreements_returns_empty(self):
        rec = ScoreDisagreementRecommender()
        results = rec.analyze([{
            "task_id": "T", "sample_id": "S", "preset": "p",
            "pseudo_delta_mrs": 1.0, "delta_mrs_open_v031": 2.0,
            "score_direction_disagreement": False, "mrs_open_flags": "",
        }])
        assert len(results) == 0

    def test_correct_loop_assignment(self, disagreement_tasks):
        rec = ScoreDisagreementRecommender()
        results = rec.analyze(disagreement_tasks)
        for r in results:
            assert r.loop == "scoring_calibration"


# ═══════════════════════════════════════════════════════════════════════
# MHP-816: PenaltyPresetRecommender
# ═══════════════════════════════════════════════════════════════════════


class TestPenaltyPresetRecommender:

    def test_only_flagged_tasks_analyzed(self, flagged_tasks):
        rec = PenaltyPresetRecommender()
        results = rec.analyze(flagged_tasks)
        assert len(results) == 2  # TASK_X, TASK_Y

    def test_over_dark_flag_action(self, flagged_tasks):
        rec = PenaltyPresetRecommender()
        results = rec.analyze(flagged_tasks)
        r = results[0]
        assert r.loop == "craft_preset_selection"
        assert "over_dark" in r.source_signal

    def test_high_severity_negative_delta(self, flagged_tasks):
        rec = PenaltyPresetRecommender()
        results = rec.analyze(flagged_tasks)
        # TASK_X: delta -7.4 with over_dark → high
        r = next(r for r in results if "TASK_X" in r.task_id)
        assert r.severity == "high"

    def test_medium_severity_near_zero(self, flagged_tasks):
        rec = PenaltyPresetRecommender()
        results = rec.analyze(flagged_tasks)
        # TASK_Y: delta -0.1 → medium
        r = next(r for r in results if "TASK_Y" in r.task_id)
        assert r.severity == "medium"

    def test_no_flags_returns_empty(self):
        rec = PenaltyPresetRecommender()
        results = rec.analyze([{
            "task_id": "T", "sample_id": "S", "preset": "p",
            "delta_mrs_open_v031": 1.0, "mrs_open_flags": "",
        }])
        assert len(results) == 0


# ═══════════════════════════════════════════════════════════════════════
# MHP-817: RuntimeReliabilityRecommender
# ═══════════════════════════════════════════════════════════════════════


class TestRuntimeReliabilityRecommender:

    def test_fatal_error_creates_high_recommendation(self):
        rec = RuntimeReliabilityRecommender()
        runtime = {
            "run_id": "test_run", "fatal_error": "FileNotFoundError: daily_run.log",
            "failed": 0,
        }
        results = rec.analyze(runtime)
        assert len(results) == 1
        assert results[0].severity == "high"
        assert results[0].loop == "runtime_reliability"

    def test_fatal_error_pattern_matching(self):
        rec = RuntimeReliabilityRecommender()
        runtime = {
            "run_id": "test_run",
            "fatal_error": "FileNotFoundError: [Errno 2] No such file or directory: '/tmp/daily_run.log'",
            "failed": 0,
        }
        results = rec.analyze(runtime)
        assert "daily_run.log" in results[0].next_action

    def test_no_fatal_no_failures_returns_empty(self):
        rec = RuntimeReliabilityRecommender()
        runtime = {"run_id": "test_run", "fatal_error": None, "failed": 0}
        results = rec.analyze(runtime)
        assert len(results) == 0

    def test_task_failures_without_fatal(self):
        rec = RuntimeReliabilityRecommender()
        runtime = {"run_id": "test_run", "fatal_error": None, "failed": 2}
        tasks = [
            {"task_id": "T1", "preset": "wide_space", "status": "failed"},
            {"task_id": "T2", "preset": "wide_space", "status": "failed"},
            {"task_id": "T3", "preset": "warm_vocal", "status": "done"},
        ]
        results = rec.analyze(runtime, tasks)
        assert len(results) == 1
        assert results[0].severity == "medium"
        assert "wide_space" in results[0].reason

    def test_needs_human_review_false(self):
        rec = RuntimeReliabilityRecommender()
        runtime = {"run_id": "test_run", "fatal_error": "Error", "failed": 0}
        results = rec.analyze(runtime)
        assert results[0].needs_human_review is False


# ═══════════════════════════════════════════════════════════════════════
# MHP-818: OperatorNextMhpWriter
# ═══════════════════════════════════════════════════════════════════════


class TestOperatorNextMhpWriter:

    def test_pass_decision_clean_run(self, night_metric_record):
        writer = OperatorNextMhpWriter()
        # No recommendations → clean run
        bundle = writer.decide(night_metric_record, [])
        assert bundle.summary["decision"] == "PASS"

    def test_hold_decision_with_high_severity(self, night_metric_record):
        writer = OperatorNextMhpWriter()
        recs = [
            Recommendation(
                task_id="t1", loop="runtime_reliability",
                severity="high", reason="fatal error",
                next_action="fix", needs_human_review=True,
                source_signal="fatal_error", owner_subsystem="runtime",
            ),
            Recommendation(
                task_id="t2", loop="scoring_calibration",
                severity="high", reason="big gap",
                next_action="calibrate", needs_human_review=True,
                source_signal="disagreement", owner_subsystem="mrs",
            ),
            Recommendation(
                task_id="t3", loop="scoring_calibration",
                severity="high", reason="another gap",
                next_action="calibrate", needs_human_review=True,
                source_signal="disagreement", owner_subsystem="mrs",
            ),
        ]
        bundle = writer.decide(night_metric_record, recs)
        assert bundle.summary["decision"] == "HOLD"
        assert bundle.summary["high_count"] == 3

    def test_hold_with_fatal_error(self, night_metric_record):
        writer = OperatorNextMhpWriter()
        record = dict(night_metric_record)
        record["runtime"] = {**record["runtime"], "fatal_error": "crash"}
        bundle = writer.decide(record, [])
        assert bundle.summary["decision"] == "HOLD"

    def test_bundle_includes_operator_recommendation(self, night_metric_record):
        writer = OperatorNextMhpWriter()
        bundle = writer.decide(night_metric_record, [])
        op_recs = bundle.by_loop("operator_report")
        assert len(op_recs) == 1
        assert "operator" in op_recs[0].task_id

    def test_next_mhp_direction(self, night_metric_record):
        writer = OperatorNextMhpWriter()
        # Simulate a run with scoring disagreements
        recs = [
            Recommendation(
                task_id="t1", loop="scoring_calibration",
                severity="high", reason="gap",
                next_action="calibrate", needs_human_review=True,
                source_signal="d", owner_subsystem="mrs",
            ),
            Recommendation(
                task_id="t2", loop="scoring_calibration",
                severity="high", reason="gap",
                next_action="calibrate", needs_human_review=True,
                source_signal="d", owner_subsystem="mrs",
            ),
            Recommendation(
                task_id="t3", loop="scoring_calibration",
                severity="high", reason="gap",
                next_action="calibrate", needs_human_review=True,
                source_signal="d", owner_subsystem="mrs",
            ),
        ]
        bundle = writer.decide(night_metric_record, recs)
        assert "scoring calibration" in bundle.summary["next_mhp"].lower()

    def test_bundle_to_dict_serializable(self, night_metric_record):
        writer = OperatorNextMhpWriter()
        bundle = writer.decide(night_metric_record, [])
        import json
        json.dumps(bundle.to_dict())  # must not raise


# ═══════════════════════════════════════════════════════════════════════
# MHP-819: RecommendationEngine Integration
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationEngine:

    def test_engine_produces_all_four_loops(self, night_metric_record):
        engine = RecommendationEngine()
        bundle = engine.run(night_metric_record)
        loops = {r.loop for r in bundle.recommendations}
        # Should include at least scoring_calibration and operator_report;
        # runtime_reliability only if fatal/failures; craft only if flags
        assert "operator_report" in loops
        # Tasks have 2 disagreements → scoring loop should fire
        assert "scoring_calibration" in loops

    def test_engine_bundle_has_summary(self, night_metric_record):
        engine = RecommendationEngine()
        bundle = engine.run(night_metric_record)
        assert "decision" in bundle.summary
        assert bundle.summary["decision"] in ("PASS", "HOLD", "REWORK")

    def test_engine_high_severity_filter(self, night_metric_record):
        engine = RecommendationEngine()
        bundle = engine.run(night_metric_record)
        # TASK_1: pseudo -20 vs open +83 → high
        # TASK_2: pseudo -18 vs open +82 → high, also flagged over_dark → medium
        high_recs = bundle.high_severity
        assert len(high_recs) >= 1

    def test_engine_needs_review_filter(self, night_metric_record):
        engine = RecommendationEngine()
        bundle = engine.run(night_metric_record)
        review = bundle.needs_review
        assert len(review) >= 1

    def test_engine_empty_tasks(self):
        engine = RecommendationEngine()
        record = {
            "run_id": "empty", "started_at": "",
            "runtime": {"success": 0, "failed": 0, "total_selected": 0,
                        "fatal_error": None, "missing_artifacts": []},
            "scoring": {"task_count": 0, "disagreement_count": 0, "disagreeing_presets": []},
            "craft": {"task_count": 0, "flagged_count": 0, "flag_types": []},
            "tasks": [],
        }
        bundle = engine.run(record)
        assert len(bundle.recommendations) == 1  # operator_report only
        assert bundle.summary["decision"] == "PASS"


# ═══════════════════════════════════════════════════════════════════════
# Base types
# ═══════════════════════════════════════════════════════════════════════


class TestRecommendationBundle:

    def test_by_loop_filter(self):
        r1 = Recommendation(task_id="a", loop="scoring_calibration", severity="high",
                            reason="", next_action="", source_signal="", owner_subsystem="")
        r2 = Recommendation(task_id="b", loop="craft_preset_selection", severity="medium",
                            reason="", next_action="", source_signal="", owner_subsystem="")
        bundle = RecommendationBundle(
            run_id="test", generated_at="",
            recommendations=[r1, r2],
        )
        assert len(bundle.by_loop("scoring_calibration")) == 1
        assert len(bundle.by_loop("craft_preset_selection")) == 1
        assert len(bundle.by_loop("runtime_reliability")) == 0

    def test_empty_bundle(self):
        bundle = RecommendationBundle()
        assert len(bundle.high_severity) == 0
        assert len(bundle.needs_review) == 0
