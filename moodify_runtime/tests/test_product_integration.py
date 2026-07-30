"""MHP-837: Product Integration Smoke.

Tests:
  - Operator Dashboard Learning View (MHP-833)
  - Craft Library Learning Feed (MHP-834)
  - MRS Calibration Review Feed (MHP-835)
  - Release Candidate Learning Gate (MHP-836)
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from moodify_runtime.collectors import collect_night_metrics
from moodify_runtime.recommenders import RecommendationEngine
from moodify_runtime.product_integration import (
    build_learning_dashboard,
    LearningDashboard,
    LearningDashboardCard,
    LearningGateResult,
    write_craft_learning_feed,
    write_calibration_review_feed,
    check_release_learning_gate,
)


@pytest.fixture
def clean_run_data(tmp_path):
    """Create a clean run with no errors, high agreement."""
    summary = {
        "run_id": "clean_run_001",
        "started_at": "2026-06-05T00:01:41Z",
        "success": 4, "failed": 0, "total_selected": 4,
        "dry_run": False, "fatal_error": None,
        "tasks": [
            {"task_id": "T1", "sample_id": "S1", "preset": "warm_vocal",
             "status": "done", "pseudo_delta_mrs": 5.0,
             "delta_mrs_open_v031": 4.0, "mrs_open_flags": "",
             "score_direction_disagreement": False},
            {"task_id": "T2", "sample_id": "S2", "preset": "bright_master",
             "status": "done", "pseudo_delta_mrs": 3.0,
             "delta_mrs_open_v031": 2.5, "mrs_open_flags": "",
             "score_direction_disagreement": False},
        ],
    }
    path = tmp_path / "clean_summary.json"
    path.write_text(json.dumps(summary, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


@pytest.fixture
def real_live_data(tmp_path):
    """Build reproducible adverse-run data without relying on ignored artifacts."""
    summary = {
        "run_id": "adverse_run_001", "started_at": "2026-06-05T00:01:41Z",
        "success": 3, "failed": 1, "total_selected": 4, "dry_run": False,
        "fatal_error": "worker heartbeat lost",
        "tasks": [
            {"task_id": "T1", "sample_id": "S1", "preset": "warm_vocal", "status": "done",
             "pseudo_delta_mrs": -20.0, "delta_mrs_open_v031": 84.0, "mrs_open_flags": ""},
            {"task_id": "T2", "sample_id": "S2", "preset": "clean_master", "status": "done",
             "pseudo_delta_mrs": 2.0, "delta_mrs_open_v031": -1.0, "mrs_open_flags": "over_dark"},
            {"task_id": "T3", "sample_id": "S3", "preset": "wide_space", "status": "done",
             "pseudo_delta_mrs": -18.0, "delta_mrs_open_v031": 82.0, "mrs_open_flags": "over_dark"},
            {"task_id": "T4", "sample_id": "S4", "preset": "warm_vocal", "status": "failed",
             "pseudo_delta_mrs": None, "delta_mrs_open_v031": None, "mrs_open_flags": ""},
        ],
    }
    summary_path = tmp_path / "adverse_summary.json"
    summary_path.write_text(json.dumps(summary), encoding="utf-8")
    queue_path = tmp_path / "tidal_queue.jsonl"
    queue_path.write_text("", encoding="utf-8")
    record = collect_night_metrics(
        summary_path=summary_path,
        queue_path=queue_path,
    )
    engine = RecommendationEngine()
    bundle = engine.run(record)
    return record, bundle.to_dict()


# ═══════════════════════════════════════════════════════════════════════
# MHP-833: Operator Dashboard Learning View
# ═══════════════════════════════════════════════════════════════════════


class TestLearningDashboard:

    def test_dashboard_has_required_cards(self, real_live_data):
        record, bundle = real_live_data
        dash = build_learning_dashboard(record, bundle)

        card_types = {c.card_type for c in dash.cards}
        assert "metric" in card_types
        assert "action" in card_types
        assert "trend" in card_types
        # Fatal error present → alert card should exist
        assert "alert" in card_types

    def test_dashboard_decision_matches_bundle(self, real_live_data):
        record, bundle = real_live_data
        dash = build_learning_dashboard(record, bundle)

        assert dash.operator_decision == bundle["summary"]["decision"]

    def test_dashboard_summary_counts(self, real_live_data):
        record, bundle = real_live_data
        dash = build_learning_dashboard(record, bundle)

        assert "total_recommendations" in dash.summary_counts
        assert dash.summary_counts["total_recommendations"] == len(bundle["recommendations"])

    def test_dashboard_to_dict_serializable(self, real_live_data):
        record, bundle = real_live_data
        dash = build_learning_dashboard(record, bundle)
        json.dumps(dash.to_dict())  # must not raise

    def test_dashboard_cards_have_severity(self, real_live_data):
        record, bundle = real_live_data
        dash = build_learning_dashboard(record, bundle)

        for card in dash.cards:
            assert card.severity in ("info", "warn", "critical")

    def test_dashboard_no_fatal_means_no_alert_card(self, clean_run_data):
        record = collect_night_metrics(summary_path=clean_run_data)
        engine = RecommendationEngine()
        bundle = engine.run(record)

        dash = build_learning_dashboard(record, bundle.to_dict())
        card_types = {c.card_type for c in dash.cards}
        assert "alert" not in card_types  # no fatal error → no alert


# ═══════════════════════════════════════════════════════════════════════
# MHP-834: Craft Library Learning Feed
# ═══════════════════════════════════════════════════════════════════════


class TestCraftLearningFeed:

    def test_feed_writes_entries(self, real_live_data, tmp_path):
        _, bundle = real_live_data
        craft_dir = tmp_path / "craft_memory"
        n = write_craft_learning_feed(bundle, craft_dir)

        assert n == 2  # 2 over_dark flagged tasks
        proposals_dir = craft_dir / "proposals"
        files = list(proposals_dir.glob("proposal_*.json"))
        assert len(files) == 2  # one per entry

    def test_feed_entry_has_required_fields(self, real_live_data, tmp_path):
        _, bundle = real_live_data
        craft_dir = tmp_path / "craft_memory"
        write_craft_learning_feed(bundle, craft_dir)

        proposals_dir = craft_dir / "proposals"
        files = list(proposals_dir.glob("proposal_*.json"))
        for fpath in files:
            proposal = json.loads(fpath.read_text(encoding="utf-8"))
            assert "proposal_id" in proposal
            assert proposal["proposal_id"].startswith("PROP_")
            assert proposal["status"] == "proposal"
            assert proposal["source"] == "data_loop_feed"
            assert "source_run_id" in proposal
            assert "craft_data" in proposal
            assert proposal["promotion_evidence"] is None

    def test_no_craft_recs_returns_zero(self, tmp_path):
        bundle = {"run_id": "test", "recommendations": []}
        n = write_craft_learning_feed(bundle, tmp_path / "craft")
        assert n == 0


# ═══════════════════════════════════════════════════════════════════════
# MHP-835: MRS Calibration Review Feed
# ═══════════════════════════════════════════════════════════════════════


class TestCalibrationReviewFeed:

    def test_feed_writes_proposals(self, real_live_data, tmp_path):
        record, bundle = real_live_data
        out = tmp_path / "cal_feed"
        n = write_calibration_review_feed(bundle, record, out)

        assert n == 3  # 3 scoring disagreements
        files = list(out.glob("calibration_review_feed_*.json"))
        assert len(files) == 1

    def test_proposal_links_to_task_data(self, real_live_data, tmp_path):
        record, bundle = real_live_data
        out = tmp_path / "cal_feed"
        write_calibration_review_feed(bundle, record, out)

        files = list(out.glob("*.json"))
        proposals = json.loads(files[0].read_text(encoding="utf-8"))
        for p in proposals:
            assert "proposal_id" in p
            assert "preset" in p
            assert "pseudo_delta_mrs" in p
            assert "delta_mrs_open_v031" in p
            assert "severity" in p
            assert p["status"] == "open"

    def test_no_score_recs_returns_zero(self, tmp_path):
        bundle = {"run_id": "test", "recommendations": []}
        record = {"tasks": []}
        n = write_calibration_review_feed(bundle, record, tmp_path / "cal")
        assert n == 0


# ═══════════════════════════════════════════════════════════════════════
# MHP-836: Release Candidate Learning Gate
# ═══════════════════════════════════════════════════════════════════════


class TestReleaseLearningGate:

    def test_gate_blocks_fatal_error(self, real_live_data):
        record, bundle = real_live_data
        gate = check_release_learning_gate(record, bundle)

        assert gate.passed is False
        assert any("Fatal error" in b for b in gate.blocking_issues)

    def test_gate_passes_clean_run(self, clean_run_data):
        record = collect_night_metrics(summary_path=clean_run_data)
        engine = RecommendationEngine()
        bundle = engine.run(record)

        gate = check_release_learning_gate(record, bundle.to_dict())
        assert gate.passed is True
        assert len(gate.blocking_issues) == 0

    def test_gate_has_four_checks(self, real_live_data):
        record, bundle = real_live_data
        gate = check_release_learning_gate(record, bundle)

        check_names = {c["check"] for c in gate.checks}
        assert "no_fatal_errors" in check_names
        assert "success_rate_95pct" in check_names
        assert "scoring_agreement_70pct" in check_names
        assert "operator_decision_pass" in check_names

    def test_gate_result_to_dict(self, real_live_data):
        record, bundle = real_live_data
        gate = check_release_learning_gate(record, bundle)

        d = gate.to_dict()
        assert isinstance(d["passed"], bool)
        assert isinstance(d["checks"], list)

    def test_gate_success_rate_check(self, clean_run_data):
        record = collect_night_metrics(summary_path=clean_run_data)
        engine = RecommendationEngine()
        bundle = engine.run(record)

        gate = check_release_learning_gate(record, bundle.to_dict())
        sr_check = next(c for c in gate.checks if c["check"] == "success_rate_95pct")
        assert sr_check["passed"] is True

    def test_low_agreement_blocks_gate(self, tmp_path):
        """Create a run where the only task has scoring disagreement."""
        summary = {
            "run_id": "low_agreement", "started_at": "",
            "success": 1, "failed": 0, "total_selected": 1,
            "dry_run": False, "fatal_error": None,
            "tasks": [
                {"task_id": "T1", "sample_id": "S1", "preset": "warm_vocal",
                 "status": "done", "pseudo_delta_mrs": -20.0,
                 "delta_mrs_open_v031": 80.0, "mrs_open_flags": "",
                 "score_direction_disagreement": True},
            ],
        }
        path = tmp_path / "low_agreement.json"
        path.write_text(json.dumps(summary, ensure_ascii=False) + "\n", encoding="utf-8")

        record = collect_night_metrics(summary_path=path)
        engine = RecommendationEngine()
        bundle = engine.run(record)

        gate = check_release_learning_gate(record, bundle.to_dict())
        assert gate.passed is False
        assert any("agreement" in b.lower() for b in gate.blocking_issues)
