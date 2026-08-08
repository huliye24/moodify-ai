"""Tests for significance_evaluator — signal vs noise detection."""
import tempfile
from pathlib import Path

from moodify_runtime.learning_store import NightRecord, append_night
from moodify_runtime.significance_evaluator import (
    compare_groups,
    evaluate_store,
    format_significance_json,
    format_significance_markdown,
    _mean_std,
    _cohens_d,
    _effect_label,
    SignificanceReport,
    GroupStats,
)


class TestMeanStd:
    def test_basic(self):
        m, s = _mean_std([1.0, 2.0, 3.0])
        assert m == 2.0
        assert s == 1.0

    def test_empty(self):
        m, s = _mean_std([])
        assert m == 0.0
        assert s == 0.0

    def test_single(self):
        m, s = _mean_std([5.0])
        assert m == 5.0
        assert s == 0.0


class TestCohensD:
    def test_large_effect(self):
        d = _cohens_d(10.0, 1.0, 10, 5.0, 1.0, 10)
        assert d > 2.0

    def test_no_effect(self):
        d = _cohens_d(5.0, 1.0, 10, 5.0, 1.0, 10)
        assert d == 0.0


class TestEffectLabel:
    def test_labels(self):
        assert _effect_label(0.1) == "negligible"
        assert _effect_label(0.3) == "small"
        assert _effect_label(0.6) == "medium"
        assert _effect_label(1.0) == "large"


class TestCompareGroups:
    def _make_nights(self) -> list[NightRecord]:
        return [
            NightRecord(run_id="R1", night_label="2026-01-01", started_at="", selected_count=5, success_count=5,
                        avg_eds=-15.0, avg_elapsed_s=110.0),
            NightRecord(run_id="R2", night_label="2026-01-02", started_at="", selected_count=5, success_count=5,
                        avg_eds=-14.5, avg_elapsed_s=108.0),
            NightRecord(run_id="R3", night_label="2026-01-03", started_at="", selected_count=5, success_count=5,
                        avg_eds=-14.0, avg_elapsed_s=106.0),
            NightRecord(run_id="R4", night_label="2026-01-04", started_at="", selected_count=5, success_count=5,
                        avg_eds=-10.0, avg_elapsed_s=95.0),
            NightRecord(run_id="R5", night_label="2026-01-05", started_at="", selected_count=5, success_count=5,
                        avg_eds=-9.0, avg_elapsed_s=90.0),
        ]

    def test_compares_groups(self):
        records = self._make_nights()
        report = compare_groups(records, split_index=3)
        assert report.group_a.label == "recent"
        assert report.group_b.label == "baseline"
        assert report.group_a.n == 2
        assert report.group_b.n == 3
        assert len(report.results) == 2

    def test_insufficient_data(self):
        records = [
            NightRecord(run_id="R1", night_label="2026-01-01", started_at="", selected_count=5, success_count=5),
        ]
        report = compare_groups(records, split_index=1)
        if report.results:
            for r in report.results:
                assert r.signal == "insufficient_data" or r.effect_label == "insufficient_data"


class TestEvaluateStore:
    def test_evaluates(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "store.jsonl"
        for i in range(6):
            append_night(p, NightRecord(
                run_id=f"R{i}", night_label=f"2026-01-0{i+1}", started_at="",
                selected_count=5, success_count=5,
                avg_eds=-15.0 + i * 0.5, avg_elapsed_s=110.0 - i * 2.0,
            ))
        report = evaluate_store(p)
        assert report.group_a.n >= 1
        assert report.group_b.n >= 1


class TestFormatSignificance:
    def test_json_output(self):
        import json
        report = SignificanceReport(
            group_a=GroupStats("recent", 2, -10.0, 1.0, 95.0, 5.0),
            group_b=GroupStats("baseline", 3, -15.0, 0.5, 110.0, 2.0),
        )
        out = format_significance_json(report)
        parsed = json.loads(out)
        assert parsed["group_a"]["n"] == 2

    def test_markdown_output(self):
        report = SignificanceReport(
            group_a=GroupStats("recent", 2, -10.0, 1.0, 95.0, 5.0),
            group_b=GroupStats("baseline", 3, -15.0, 0.5, 110.0, 2.0),
        )
        md = format_significance_markdown(report)
        assert "# Statistical Significance Report" in md
        assert "recent" in md
        assert "baseline" in md
