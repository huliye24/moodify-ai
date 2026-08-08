"""Tests for report generation — Markdown and HTML output."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.studio_session_prep.reporting import (
    build_comparison_table,
    build_markdown_report,
    build_html_report,
)


class TestComparisonTable:
    def test_basic_comparison(self):
        ref = {
            "source_path": "/tmp/ref.wav",
            "level": {"peak_dbfs": -3.0, "rms_db": -18.0, "crest_factor": 5.0},
            "spectral": {"spectral_centroid_hz": 1500.0, "spectral_entropy": 0.6, "spectral_flux": 0.01},
            "stereo": {"left_right_correlation": 0.8},
            "band_fractions": {"band_20_250_fraction": 0.1, "band_250_2000_fraction": 0.4},
        }
        cand = {
            "source_path": "/tmp/cand.wav",
            "level": {"peak_dbfs": -2.0, "rms_db": -16.0, "crest_factor": 4.5},
            "spectral": {"spectral_centroid_hz": 1600.0, "spectral_entropy": 0.55, "spectral_flux": 0.015},
            "stereo": {"left_right_correlation": 0.75},
            "band_fractions": {"band_20_250_fraction": 0.12, "band_250_2000_fraction": 0.38},
        }
        comp = build_comparison_table(ref, cand)
        assert comp["human_review"] == "PENDING"
        assert "peak_dbfs_delta" in comp["deltas"]
        assert comp["deltas"]["peak_dbfs_delta"] == pytest.approx(1.0, abs=0.01)
        assert comp["deltas"]["rms_db_delta"] == pytest.approx(2.0, abs=0.01)
        assert comp["deltas"]["crest_factor_delta"] == pytest.approx(-0.5, abs=0.01)

    def test_large_rms_delta_warns(self):
        ref = {"source_path": "r", "level": {"rms_db": -20.0}, "spectral": {}, "stereo": {}, "band_fractions": {}}
        cand = {"source_path": "c", "level": {"rms_db": -15.0}, "spectral": {}, "stereo": {}, "band_fractions": {}}
        comp = build_comparison_table(ref, cand)
        assert len(comp["warnings"]) > 0
        assert any("loudness" in w.lower() or "Large" in w for w in comp["warnings"])

    def test_limitations_present(self):
        ref = {"source_path": "r", "level": {}, "spectral": {}, "stereo": {}, "band_fractions": {}}
        cand = {"source_path": "c", "level": {}, "spectral": {}, "stereo": {}, "band_fractions": {}}
        comp = build_comparison_table(ref, cand)
        assert len(comp["limitations"]) >= 2

    def test_null_metrics_handle_gracefully(self):
        ref = {"source_path": "r", "level": {"peak_dbfs": None}, "spectral": {}, "stereo": {}, "band_fractions": {}}
        cand = {"source_path": "c", "level": {"peak_dbfs": None}, "spectral": {}, "stereo": {}, "band_fractions": {}}
        comp = build_comparison_table(ref, cand)
        assert comp["human_review"] == "PENDING"
        # No crash


class TestMarkdownReport:
    def test_basic_report(self):
        md = build_markdown_report()
        assert "# Moodify Studio Session" in md
        assert "Limitations" in md
        assert "Disclaimer" in md

    def test_report_with_manifest(self):
        manifest = {
            "session_brief": {
                "project_title": "Test Project",
                "client_name": "Test Client",
                "session_date": "2026-08-01",
                "engineer_name": "Engineer",
                "studio_location": "Studio A",
                "genre": "pop",
            },
            "recording_spec": {
                "sample_rate": "48000",
                "bit_depth": "24",
                "file_format": "wav",
                "target_peak_dbfs": -6.0,
                "channel_count": 2,
            },
        }
        md = build_markdown_report(manifest=manifest)
        assert "Test Project" in md
        assert "Test Client" in md
        assert "48000" in md

    def test_report_with_wse_profile(self):
        wse = {
            "source_path": "/tmp/test.wav",
            "source_sha256": "a" * 64,
            "duration_s": 10.0,
            "sample_rate": 48000,
            "channels": 2,
            "level": {"peak_dbfs": -3.0, "rms_db": -18.0, "crest_factor": 5.0},
            "loudness": {"loudness_lufs": -16.0, "lra_lu": None, "true_peak_dbtp": None},
            "spectral": {"spectral_centroid_hz": 1500.0, "spectral_entropy": 0.6, "spectral_flux": 0.01},
            "band_fractions": {"band_20_250_fraction": 0.1, "band_250_2000_fraction": 0.4},
            "unavailable": {
                "lra_lu": "null — reason",
                "true_peak_dbtp": "null — reason",
                "phase_rotation_deg": "null — reason",
                "masking_index": "null — reason",
            },
        }
        md = build_markdown_report(wse_profile=wse)
        assert "WSE Analysis" in md
        assert "null" in md

    def test_report_with_candidates(self):
        candidates = [
            {"candidate_id": "conservative", "preset": "clean_master",
             "executed": True, "dry_run": False, "exit_code": 0, "duration_s": 1.5,
             "output_audio": "/tmp/out.wav", "output_sha256": "b" * 64},
            {"candidate_id": "balanced", "preset": "clean_master",
             "executed": False, "dry_run": True, "exit_code": None, "duration_s": 0.0},
        ]
        md = build_markdown_report(candidate_results=candidates)
        assert "conservative" in md
        assert "balanced" in md

    def test_report_with_comparisons(self):
        comp = [{
            "human_review": "PENDING",
            "deltas": {"rms_db_delta": 1.5, "peak_dbfs_delta": 0.5},
            "warnings": ["Moderate loudness change"],
            "limitations": [],
        }]
        md = build_markdown_report(comparisons=comp)
        assert "Candidate Comparisons" in md
        assert "PENDING" in md
        assert "rms_db_delta" in md

    def test_report_no_auto_language(self):
        md = build_markdown_report()
        assert "必然提升" not in md
        assert "发行级" not in md
        assert "超过人工" not in md
        assert "better sounding" not in md.lower()


class TestHTMLReport:
    def test_html_generation(self):
        md = build_markdown_report()
        html = build_html_report(md, title="Test Report")
        assert "<!DOCTYPE html>" in html
        assert "<title>Test Report</title>" in html
        assert "</html>" in html

    def test_html_escapes_content(self):
        md = "# Test <script>alert('xss')</script>"
        html = build_html_report(md)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html
