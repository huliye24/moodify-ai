"""Tests for comparison_report — stepwise delta report generator."""
import json
import tempfile
from pathlib import Path

from moodify_runtime.comparison_report import (
    ComparisonReport,
    generate_comparison_json,
    generate_comparison_markdown,
    write_comparison_report,
)
from moodify_runtime.mrs_surface import compute_mrs_surface
from moodify_runtime.fusion_scorer import compute_fusion_score
from moodify_runtime.craft_evidence import (
    create_step_evidence, create_manifest,
)


class TestGenerateComparisonJson:
    def test_basic_report(self):
        report = ComparisonReport(
            report_id="RPT_001", sample_id="S1",
            preset="warm", genre="piano",
        )
        out = generate_comparison_json(report)
        parsed = json.loads(out)
        assert parsed["report_id"] == "RPT_001"
        assert parsed["sample_id"] == "S1"

    def test_with_mrs_surface(self):
        surface = compute_mrs_surface(sample_id="S1", genre="piano", preset="warm")
        report = ComparisonReport(
            report_id="RPT_002", sample_id="S1",
            preset="warm", genre="piano",
            mrs_surface=surface,
        )
        out = generate_comparison_json(report)
        parsed = json.loads(out)
        assert "mrs_surface" in parsed
        assert parsed["mrs_surface"]["composite"] > 0

    def test_with_fusion_score(self):
        fs = compute_fusion_score(sample_id="S1", preset="warm")
        report = ComparisonReport(
            report_id="RPT_003", sample_id="S1",
            preset="warm", genre="piano",
            fusion_score=fs,
        )
        out = generate_comparison_json(report)
        assert "fusion_score" in json.loads(out)


class TestGenerateComparisonMarkdown:
    def test_full_report(self):
        surface = compute_mrs_surface(sample_id="S1")
        fs = compute_fusion_score(sample_id="S1")
        steps = [
            create_step_evidence("input_normalize", 0),
            create_step_evidence("silence_trim", 1),
        ]
        manifest = create_manifest("M1", "R1", "test_chain", steps)
        report = ComparisonReport(
            report_id="RPT_FULL", sample_id="S1",
            preset="warm", genre="piano",
            mrs_surface=surface, fusion_score=fs, craft_manifest=manifest,
        )
        md = generate_comparison_markdown(report)
        assert "# Stepwise Comparison Report" in md
        assert "MRS Quality Surface" in md
        assert "Fusion Score" in md
        assert "Craft Chain Evidence" in md
        assert "Input Normalize" in md


class TestWriteComparisonReport:
    def test_writes_files(self):
        d = tempfile.mkdtemp()
        out_dir = Path(d) / "reports"
        surface = compute_mrs_surface(sample_id="S1")
        fs = compute_fusion_score(sample_id="S1")
        report = ComparisonReport(
            report_id="RPT_W", sample_id="S1", preset="warm", genre="piano",
            mrs_surface=surface, fusion_score=fs,
        )
        paths = write_comparison_report(report, out_dir)
        assert Path(paths["json"]).exists()
        assert Path(paths["markdown"]).exists()

        content = Path(paths["json"]).read_text()
        assert "RPT_W" in content
