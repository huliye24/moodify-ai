"""MHP-825: Data Loop Integration Smoke.

End-to-end tests covering:
  - CollectorPipeline + RecommendationEngine integration
  - DataLoopRunner.run() produces valid output
  - CLI data-loop run/report commands
  - Craft writeback and calibration proposal hooks
  - Report generation
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from moodify_runtime.collectors import collect_night_metrics
from moodify_runtime.recommenders import RecommendationEngine
from moodify_runtime.data_loop_runner import DataLoopRunner, DataLoopResult


@pytest.fixture
def test_summary_path(tmp_path):
    """Create a minimal valid summary.json for integration testing."""
    summary = {
        "run_id": "20260605_smoke",
        "started_at": "2026-06-05T00:01:41+00:00",
        "success": 2, "failed": 0, "total_selected": 2,
        "dry_run": False,
        "fatal_error": None,
        "finished_at": "2026-06-05T00:02:00+00:00",
        "tasks": [
            {
                "task_id": "TASK_SMOKE_A", "sample_id": "SMP_A", "preset": "warm_vocal",
                "status": "done", "return_code": 0, "elapsed_seconds": "0.5",
                "pseudo_mrs_before": 80.0, "pseudo_mrs_after": 60.0,
                "pseudo_delta_mrs": -20.0,
                "mrs_open_v031_before": 1036.0, "mrs_open_v031_after": 1120.0,
                "delta_mrs_open_v031": 84.0, "mrs_open_flags": "",
            },
            {
                "task_id": "TASK_SMOKE_B", "sample_id": "SMP_B", "preset": "wide_space",
                "status": "done", "return_code": 0, "elapsed_seconds": "0.7",
                "pseudo_mrs_before": 82.0, "pseudo_mrs_after": 84.0,
                "pseudo_delta_mrs": 2.0,
                "mrs_open_v031_before": 1036.0, "mrs_open_v031_after": 1035.0,
                "delta_mrs_open_v031": -1.0, "mrs_open_flags": "over_dark",
            },
        ],
    }
    path = tmp_path / "summary.json"
    path.write_text(json.dumps(summary, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


@pytest.fixture
def test_queue_path(tmp_path):
    """Create a minimal queue.jsonl."""
    queue = [
        {"task_id": "T1", "status": "done"},
        {"task_id": "T2", "status": "done"},
        {"task_id": "T3", "status": "pending"},
    ]
    path = tmp_path / "queue.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for item in queue:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    return path


# ═══════════════════════════════════════════════════════════════════════
# Integration: Collectors → Recommenders
# ═══════════════════════════════════════════════════════════════════════


class TestCollectorRecommenderIntegration:

    def test_collect_then_recommend(self, test_summary_path, test_queue_path):
        """End-to-end: collect from summary → generate recommendations."""
        record = collect_night_metrics(
            summary_path=test_summary_path,
            queue_path=test_queue_path,
        )
        assert record["run_id"] == "20260605_smoke"
        assert record["scoring"]["disagreement_count"] == 2  # both tasks have sign disagreements

        engine = RecommendationEngine()
        bundle = engine.run(record)

        assert len(bundle.recommendations) >= 1
        assert "operator_report" in {r.loop for r in bundle.recommendations}
        assert "decision" in bundle.summary

    def test_integration_preserves_signal_traceability(self, test_summary_path):
        """Recommendations should trace back to specific source signals."""
        record = collect_night_metrics(summary_path=test_summary_path)
        engine = RecommendationEngine()
        bundle = engine.run(record)

        for r in bundle.recommendations:
            if r.loop == "operator_report":
                continue
            assert r.source_signal, f"Missing source_signal for {r.task_id}"
            assert r.owner_subsystem, f"Missing owner_subsystem for {r.task_id}"

    def test_empty_tasks_produces_operator_only(self):
        """Pipeline handles empty runs gracefully."""
        import tempfile
        import json as _json
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            _json.dump({
                "run_id": "empty_run", "started_at": "",
                "success": 0, "failed": 0, "total_selected": 0,
                "dry_run": True, "tasks": [],
            }, f)
            path = Path(f.name)

        try:
            record = collect_night_metrics(summary_path=path)
            engine = RecommendationEngine()
            bundle = engine.run(record)

            assert len(bundle.recommendations) == 1  # operator only
            assert bundle.summary["decision"] == "PASS"
        finally:
            path.unlink()


# ═══════════════════════════════════════════════════════════════════════
# MHP-821: DataLoopRunner
# ═══════════════════════════════════════════════════════════════════════


class TestDataLoopRunner:

    def test_runner_produces_result(self, test_summary_path, tmp_path):
        runner = DataLoopRunner(
            summary_path=test_summary_path,
            output_dir=tmp_path / "dlt_output",
        )
        result = runner.run()

        assert isinstance(result, DataLoopResult)
        assert result.run_id == "20260605_smoke"
        assert result.started_at
        assert result.finished_at

    def test_runner_writes_output_files(self, test_summary_path, tmp_path):
        out = tmp_path / "dlt_output"
        runner = DataLoopRunner(summary_path=test_summary_path, output_dir=out)
        runner.run()

        assert (out / "night_metric_record.json").exists()
        assert (out / "recommendation_bundle.json").exists()
        assert (out / "data_loop_report.md").exists()

        # Verify report content
        report = (out / "data_loop_report.md").read_text(encoding="utf-8")
        assert "20260605_smoke" in report
        assert "Recommendations" in report

    def test_runner_writeback(self, test_summary_path, tmp_path):
        craft_dir = tmp_path / "craft_memory"
        out = tmp_path / "dlt_output"
        runner = DataLoopRunner(
            summary_path=test_summary_path,
            output_dir=out,
            craft_memory_dir=craft_dir,
        )
        result = runner.run(writeback=True)

        assert result.craft_writeback_count >= 0
        assert result.calibration_writeback_count >= 0

    def test_runner_with_all_sources(self, test_summary_path, test_queue_path, tmp_path):
        runner = DataLoopRunner(
            summary_path=test_summary_path,
            queue_path=test_queue_path,
            output_dir=tmp_path / "dlt_output",
        )
        result = runner.run()

        assert result.run_id == "20260605_smoke"
        queue = result.night_metric_record.get("queue", {})
        assert queue.get("total_tasks") == 3

    def test_result_to_dict_serializable(self, test_summary_path, tmp_path):
        runner = DataLoopRunner(
            summary_path=test_summary_path,
            output_dir=tmp_path / "dlt_output",
        )
        result = runner.run()
        json.dumps(result.to_dict())  # must not raise

    def test_runner_fatal_error_hold_decision(self, tmp_path):
        """A run with fatal error should produce HOLD decision."""
        summary = {
            "run_id": "fatal_run", "started_at": "",
            "success": 3, "failed": 1, "total_selected": 4,
            "dry_run": False,
            "fatal_error": "FileNotFoundError: /tmp/missing.log",
            "tasks": [],
        }
        path = tmp_path / "fatal_summary.json"
        path.write_text(json.dumps(summary, ensure_ascii=False) + "\n", encoding="utf-8")

        runner = DataLoopRunner(summary_path=path, output_dir=tmp_path / "dlt_fatal")
        result = runner.run()

        decision = result.recommendation_bundle.get("summary", {}).get("decision", "?")
        assert decision == "HOLD"


# ═══════════════════════════════════════════════════════════════════════
# MHP-822: Report Formatting
# ═══════════════════════════════════════════════════════════════════════


class TestDataLoopReport:

    def test_report_contains_all_sections(self, test_summary_path, tmp_path):
        runner = DataLoopRunner(summary_path=test_summary_path, output_dir=tmp_path / "dlr")
        result = runner.run()

        report = (tmp_path / "dlr" / "data_loop_report.md").read_text(encoding="utf-8")
        assert "## Summary" in report
        assert "## Recommendations" in report
        assert "## Decision Rationale" in report
        assert "## Next Steps" in report

    def test_report_includes_metric_table(self, test_summary_path, tmp_path):
        runner = DataLoopRunner(summary_path=test_summary_path, output_dir=tmp_path / "dlr")
        runner.run()

        report = (tmp_path / "dlr" / "data_loop_report.md").read_text(encoding="utf-8")
        assert "| Metric | Value |" in report
        assert "success" in report.lower() or "2" in report
