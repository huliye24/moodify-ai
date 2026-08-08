"""Tests for xclp_gate — X-CLP gate helper for Moodify modules."""
import pytest

# X-CLP is an external cloud-side tool located at /home/ubuntu/X-CLP, not a
# declared Moodify runtime dependency. Its integration tests are collected only
# when that optional package is present; absence remains visible as a skip
# instead of aborting collection for unrelated hardening tests.
pytest.importorskip("xclp", reason="optional cloud-side X-CLP package is unavailable")

from moodify_runtime.xclp_gate import (
    GateReport,
    ScoreResult,
    score_module,
    gate_module,
    format_gate_report_markdown,
    classify_score,
    compute_l_code,
    clamp_score,
)


class TestClampScore:
    def test_clamps_low(self):
        assert clamp_score(-5) == 0.0

    def test_clamps_high(self):
        assert clamp_score(150) == 100.0

    def test_passes_through(self):
        assert clamp_score(75.5) == 75.5


class TestComputeLCode:
    def test_perfect_score(self):
        assert compute_l_code(100, 100, 100, 100) == 100.0

    def test_zero_dimension_kills_score(self):
        assert compute_l_code(100, 100, 100, 0) == 0.0

    def test_mid_range(self):
        s = compute_l_code(70, 70, 70, 70)
        assert 20 < s < 30

    def test_nem_ready_target(self):
        s = compute_l_code(80, 80, 80, 80)
        assert s >= 40  # 0.8^4 * 100 ≈ 40.96


class TestClassifyScore:
    def test_fragile(self):
        level, gate = classify_score(10)
        assert level == "Fragile"
        assert gate == "REJECT"

    def test_core(self):
        level, gate = classify_score(85)
        assert level == "Ecosystem-ready"
        assert gate == "CORE"

    def test_nem_ready(self):
        level, gate = classify_score(65)
        assert level == "NEM-ready"
        assert gate == "ADOPT"


class TestScoreModule:
    def test_returns_score_result(self):
        result = score_module("test_mod", 70, 75, 80, 65)
        assert isinstance(result, ScoreResult)
        assert result.project_name == "test_mod"
        assert result.R_speed == 70
        assert result.L_code > 0


class TestGateModule:
    def test_passes_when_above_target(self):
        report = gate_module("xclp_gate", 90, 90, 90, 90, xclp_target=60)
        assert report.passed is True
        assert report.gap == 0.0

    def test_fails_when_below_target(self):
        report = gate_module("weak_mod", 30, 30, 30, 30, xclp_target=60)
        assert report.passed is False
        assert report.gap > 0
        assert len(report.notes) > 0

    def test_notes_identify_weakest_dimension(self):
        report = gate_module("mod", 80, 20, 80, 80, xclp_target=60)
        assert not report.passed
        assert any("S_structure" in n for n in report.notes)


class TestFormatGateReportMarkdown:
    def test_single_report(self):
        report = gate_module("mod", 90, 90, 90, 90, xclp_target=60)
        md = format_gate_report_markdown([report], title="Test Report")
        assert "# Test Report" in md
        assert "mod" in md
        assert "PASS" in md
        assert "1/1" in md

    def test_mixed_pass_fail(self):
        r1 = gate_module("good", 90, 90, 90, 90, xclp_target=60)
        r2 = gate_module("bad", 30, 30, 30, 30, xclp_target=60)
        md = format_gate_report_markdown([r1, r2])
        assert "PASS" in md
        assert "FAIL" in md
        assert "1/2" in md
        assert "## Failures" in md
