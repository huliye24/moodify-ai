"""Tests for pdf_qa."""
from moodify_runtime.pdf_qa import (
    PdfQAResult, PdfQARun, _file_size_kb, qa_non_empty_pages, qa_page_count,
)

class TestResult:
    def test_passed(self):
        r = PdfQAResult(check_name="c", passed=True, details="ok")
        assert r.passed

class TestRun:
    def test_default(self):
        r = PdfQARun(pdf_path="/tmp/t.pdf")
        assert r.pdf_path == "/tmp/t.pdf"

class TestFileSize:
    def test_nonexistent(self):
        assert _file_size_kb("/nonexistent/x.pdf") == 0

class TestQA:
    def test_non_empty(self):
        r = qa_non_empty_pages("/nonexistent/x.pdf")
        assert isinstance(r, PdfQAResult)
    def test_page_count(self):
        r = qa_page_count("/nonexistent/x.pdf")
        assert isinstance(r, PdfQAResult)
