"""Tests for trend_analyzer — cross-night trend metrics."""
import tempfile
from pathlib import Path

from moodify_runtime.learning_store import NightRecord, append_night
from moodify_runtime.trend_analyzer import (
    analyze_trends,
    format_trend_json,
    format_trend_markdown,
    _direction,
    TrendReport,
    TrendPoint,
)


class TestDirection:
    def test_stable(self):
        assert _direction(10.0, 10.1) == "stable"

    def test_improving(self):
        assert _direction(10.0, 10.5) == "improving"

    def test_declining(self):
        assert _direction(10.0, 9.4) == "declining"

    def test_none_prev(self):
        assert _direction(None, 10.0) == "stable"

    def test_zero_prev(self):
        assert _direction(0.0, 1.0) == "improving"
        assert _direction(0.0, 0.0) == "stable"


class TestAnalyzeTrends:
    def _make_store(self, store_path: Path) -> None:
        nights = [
            NightRecord(run_id="R1", started_at="2026-01-01T12:00:00", night_label="2026-01-01",
                        selected_count=10, success_count=10, avg_eds=-15.0, avg_elapsed_s=110.0),
            NightRecord(run_id="R2", started_at="2026-01-02T12:00:00", night_label="2026-01-02",
                        selected_count=10, success_count=9, avg_eds=-14.5, avg_elapsed_s=108.0),
            NightRecord(run_id="R3", started_at="2026-01-03T12:00:00", night_label="2026-01-03",
                        selected_count=10, success_count=10, avg_eds=-13.8, avg_elapsed_s=105.0),
        ]
        for nr in nights:
            append_night(store_path, nr)

    def test_analyzes_trends(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "store.jsonl"
        self._make_store(p)

        report = analyze_trends(p)
        assert report.summary["total_nights"] == 3
        assert report.summary["eds_improving_nights"] >= 2
        assert len(report.points) == 3

    def test_empty_store(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "store.jsonl"
        report = analyze_trends(p)
        assert report.summary["total_nights"] == 0
        assert report.points == []

    def test_single_night(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "store.jsonl"
        append_night(p, NightRecord(run_id="R1", started_at="2026-01-01T12:00:00", night_label="2026-01-01",
                                    selected_count=5, success_count=5, avg_eds=-15.0))
        report = analyze_trends(p)
        assert len(report.points) == 1
        assert report.points[0].eds_direction == "stable"


class TestFormatTrendJson:
    def test_outputs_valid_json(self):
        import json
        report = TrendReport(
            window_size=3, summary={"total_nights": 1, "eds_improving_nights": 0, "eds_declining_nights": 0},
            points=[TrendPoint(night_label="2026-01-01", avg_eds=-15.0, avg_elapsed_s=110.0, success_rate=1.0)],
        )
        out = format_trend_json(report)
        parsed = json.loads(out)
        assert parsed["window_size"] == 3
        assert len(parsed["points"]) == 1


class TestFormatTrendMarkdown:
    def test_outputs_markdown(self):
        report = TrendReport(
            window_size=3, summary={"total_nights": 1, "eds_improving_nights": 0, "eds_declining_nights": 0,
                                     "eds_overall_direction": "stable", "elapsed_overall_direction": "stable"},
            points=[TrendPoint(night_label="2026-01-01", avg_eds=-15.0, avg_elapsed_s=110.0, success_rate=1.0)],
        )
        md = format_trend_markdown(report)
        assert "# Multi-Night Trend Report" in md
        assert "2026-01-01" in md
        assert "-15.0" in md
