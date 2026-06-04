"""Tests for pdf_templates."""
from moodify_runtime.pdf_templates import PdfTheme, PageTemplate


class TestPdfTheme:
    def test_default(self):
        t = PdfTheme()
        assert t.bg_dark is not None
        assert t.text_color is not None
    def test_custom(self):
        t = PdfTheme(accent_color="#ff0000", text_color="#ffffff")
        assert t.accent_color == "#ff0000"
    def test_title_size(self):
        t = PdfTheme()
        assert t.title_size > 0


class TestPageTemplate:
    def test_defaults(self):
        pt = PageTemplate()
        assert pt.page_number is not None
    def test_numbered(self):
        pt = PageTemplate(page_number=3, total_pages=10)
        assert pt.page_number == 3
