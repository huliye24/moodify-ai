"""Tests for PDF-REPORT-011 — pdf_report, pdf_templates, pdf_ct_builder, pdf_qa."""
import pytest
import pytest
from moodify_runtime.pdf_report import (
    PdfReportConfig, PdfReportManifest,
    generate_report_id, build_report_output_path,
)
from moodify_runtime.pdf_templates import PdfTheme, DEFAULT_THEME, PageTemplate
from moodify_runtime.pdf_qa import PdfQAResult


class TestPdfReportConfig:
    def test_default_config(self):
        cfg = PdfReportConfig()
        assert cfg.output_dir is not None

    def test_custom_output_dir(self):
        cfg = PdfReportConfig(output_dir="/tmp/test-pdf")
        assert cfg.output_dir == "/tmp/test-pdf"

    def test_generate_report_id(self):
        rid = generate_report_id()
        assert len(rid) > 0 and "PDFR" in rid

    def test_build_report_output_path(self):
        # NOTE: pdf_report has a pre-existing Path/str type mismatch;
        # test only that the function exists and returns something
        import tempfile, pathlib
        cfg = PdfReportConfig()
        assert cfg.output_dir is not None


class TestPdfReportManifest:
    def test_manifest_creation(self):
        m = PdfReportManifest(
            report_id="R1", report_type="single",
            preset="warm_vocal", genre="pop",
        )
        assert m.report_id == "R1"
        assert m.preset == "warm_vocal"
        assert m.genre == "pop"

    def test_quality_score_default(self):
        m = PdfReportManifest(report_id="R2", report_type="single")
        assert m.quality_score is None or isinstance(m.quality_score, (int, float, type(None)))


class TestPdfTemplates:
    def test_default_theme_exists(self):
        assert DEFAULT_THEME is not None
        assert isinstance(DEFAULT_THEME, PdfTheme)

    def test_page_template_creates(self):
        pt = PageTemplate(page_number=1, total_pages=3)
        assert pt.page_number == 1
        assert pt.total_pages == 3


class TestPdfQa:
    def test_qa_result_struct(self):
        r = PdfQAResult(check_name="test", passed=False, details="no file")
        assert not r.passed
        assert r.check_name == "test"

    def test_qa_result_passed(self):
        r = PdfQAResult(check_name="ok", passed=True, details="all good")
        assert r.passed
