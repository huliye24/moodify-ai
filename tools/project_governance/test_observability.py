"""Tests for the observability layer (025)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from tools.project_governance.observability import Collector
from tools.project_governance.reports import special_report, stage_report, weekly_report
from tools.project_governance.trend_rules import evaluate


class TestCollector:
    def test_partial_marked_on_failure(self) -> None:
        c = Collector()

        def boom():
            raise RuntimeError("collector failed")

        c.collect("x", boom)
        assert c.metrics["x"] is None
        assert len(c.partial) == 1
        assert c.partial[0]["metric"] == "x"

    def test_success_not_partial(self) -> None:
        c = Collector()
        c.collect("y", lambda: 42)
        assert c.metrics["y"] == 42
        assert c.partial == []

    def test_deterministic_metrics(self) -> None:
        from tools.project_governance.observability import collect_all

        r1 = collect_all()
        r2 = collect_all()
        # data body deterministic; run_id/collected_at differ
        assert r1["metrics"] == r2["metrics"]


class TestTrendRules:
    def test_red_line_triggered(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        # feed a fabricated observation with red lines
        obs_dir = tmp_path / "project_analytics" / "observations"
        obs_dir.mkdir(parents=True)
        (obs_dir / "obs-0001.json").write_text(json.dumps({
            "schema": "moodify.analytics.observation/0.1",
            "run_id": "obs-0001",
            "collected_at": "2026-08-02T00:00:00Z",
            "status": "complete",
            "partial": [],
            "metrics": {
                "test_collection": {"errors": 3, "collected": 100},
                "task_state_conflicts": 0,
                "enclosure": {"violations": 0, "baseline_debt": 0},
                "git_concentration": {"core_share_pct": 50.0},
                "architecture_budget": {"cross_area_edges": 10, "cycles": 0},
                "task_states": {},
            },
        }), encoding="utf-8")

        import tools.project_governance.trend_rules as rules

        monkeypatch.setattr(rules, "ROOT", tmp_path)
        result = evaluate()
        assert result["red_lines"]["test_collection_errors"] is True
        assert result["decision"] == "TRIGGER_SPECIAL_ASSESSMENT"

    def test_clean_gives_resume(self) -> None:
        result = evaluate()
        assert result["decision"] in ("RESUME_DEVELOPMENT", "CONTINUE_STABILIZING", "NOT_MEASURED")


class TestReports:
    def test_weekly_not_measured_without_obs(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        import tools.project_governance.reports as reports

        monkeypatch.setattr(reports, "ROOT", tmp_path)
        report = weekly_report()
        assert report["status"] == "NOT_MEASURED"

    def test_special_report_has_trigger(self) -> None:
        report = special_report("architecture-migration")
        assert report["trigger"] == "architecture-migration"
        assert report["recommended_action"]

    def test_stage_honest_not_measured(self) -> None:
        report = stage_report()
        assert report.get("horizontalization_judgment") == "EVIDENCE_INSUFFICIENT"
        assert report.get("rework_drag_pct") == "NOT_MEASURED"
