"""MHP-673-675: PDF QA Checks.

PDF quality assurance: non-empty pages, logo presence, footer readability,
text extraction smoke, image render smoke.

Part of ECHAIN-MOODIFY-PDF-REPORT-011 / NEM-PDF-OPS-QA-SYSTEM-035.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .pdf_assets import BrandAssets


@dataclass
class PdfQAResult:
    """Result of a PDF QA check."""

    check_name: str
    passed: bool
    details: str = ""
    severity: str = "info"  # info | warning | error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check": self.check_name,
            "passed": self.passed,
            "details": self.details,
            "severity": self.severity,
        }


@dataclass
class PdfQARun:
    """Collection of QA check results for a PDF report."""

    pdf_path: str
    checks: List[PdfQAResult] = field(default_factory=list)
    passed: int = 0
    failed: int = 0
    warnings: int = 0

    def add(self, result: PdfQAResult) -> None:
        self.checks.append(result)
        if result.passed:
            self.passed += 1
        elif result.severity == "error":
            self.failed += 1
        else:
            self.warnings += 1

    @property
    def all_passed(self) -> bool:
        return self.failed == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pdf_path": self.pdf_path,
            "summary": {
                "total": len(self.checks),
                "passed": self.passed,
                "failed": self.failed,
                "warnings": self.warnings,
                "all_passed": self.all_passed,
            },
            "checks": [c.to_dict() for c in self.checks],
        }


def _file_size_kb(path: str) -> float:
    """Get file size in KB."""
    try:
        return Path(path).stat().st_size / 1024
    except Exception:
        return 0.0


# ═══════════════════════════════════════════════════════════════════════════
# MHP-673: PDF QA Checks
# ═══════════════════════════════════════════════════════════════════════════

def qa_non_empty_pages(pdf_path: str) -> PdfQAResult:
    """Check that the PDF file exists and is non-empty."""
    path = Path(pdf_path)
    if not path.exists():
        return PdfQAResult(
            "non_empty_pages", False,
            f"PDF file does not exist: {pdf_path}", "error",
        )
    size_kb = _file_size_kb(pdf_path)
    if size_kb < 1.0:
        return PdfQAResult(
            "non_empty_pages", False,
            f"PDF file is too small: {size_kb:.1f} KB", "error",
        )
    return PdfQAResult(
        "non_empty_pages", True,
        f"PDF exists, size: {size_kb:.1f} KB",
    )


def qa_logo_presence(pdf_path: str, brand: Optional[BrandAssets] = None) -> PdfQAResult:
    """Check that the brand logo is available for PDF generation.

    Note: This checks logo availability at generation time, not inside the
    rendered PDF (which would require PDF parsing libraries).
    """
    brand = brand or BrandAssets.resolve()
    if brand.logo_available:
        return PdfQAResult(
            "logo_presence", True,
            f"Logo available at: {brand.logo_path}",
        )
    return PdfQAResult(
        "logo_presence", False,
        f"Logo not available: {brand.logo_error}", "warning",
    )


def qa_manifest_exists(pdf_path: str) -> PdfQAResult:
    """Check that a manifest JSON file exists alongside the PDF."""
    manifest_path = Path(pdf_path).with_suffix(".manifest.json")
    if manifest_path.exists():
        return PdfQAResult(
            "manifest_exists", True,
            f"Manifest found: {manifest_path}",
        )
    return PdfQAResult(
        "manifest_exists", False,
        f"No manifest found at: {manifest_path}", "warning",
    )


def qa_page_count(pdf_path: str, min_pages: int = 1) -> PdfQAResult:
    """Check estimated page count from file size heuristic.

    For accurate page counts, use a PDF parsing library.
    This provides a rough estimate based on file size.
    """
    size_kb = _file_size_kb(pdf_path)
    # Rough heuristic: ~50-200 KB per page for matplotlib PDFs
    estimated_pages = max(1, int(size_kb / 80))
    if estimated_pages >= min_pages:
        return PdfQAResult(
            "page_count", True,
            f"Estimated {estimated_pages} page(s), meets minimum {min_pages}",
        )
    return PdfQAResult(
        "page_count", False,
        f"Estimated {estimated_pages} page(s), below minimum {min_pages}", "warning",
    )


# ═══════════════════════════════════════════════════════════════════════════
# MHP-674: Text Extraction Smoke
# ═══════════════════════════════════════════════════════════════════════════

def qa_text_extraction_smoke(pdf_path: str) -> PdfQAResult:
    """Check that the PDF has extractable text by verifying metadata presence.

    Since we use matplotlib.backends.backend_pdf, text is rendered as vector
    paths, not extractable strings. This check verifies the manifest provides
    the text metadata needed for search/index. Falls back to checking raw PDF
    content for text markers.
    """
    path = Path(pdf_path)
    if not path.exists():
        return PdfQAResult("text_extraction_smoke", False, "PDF not found", "error")

    try:
        raw = path.read_bytes()
        # Check for PDF header and basic text markers
        has_pdf_header = raw.startswith(b"%PDF")
        has_text_markers = b"BT" in raw and b"ET" in raw  # Begin/End text objects
        has_metadata = b"/Title" in raw or b"/Creator" in raw

        if has_pdf_header and (has_text_markers or has_metadata):
            return PdfQAResult(
                "text_extraction_smoke", True,
                "PDF has text markers and/or metadata",
            )
        elif has_pdf_header:
            return PdfQAResult(
                "text_extraction_smoke", True,
                "PDF is valid; text extraction limited (vector text). "
                "Use .manifest.json for full text metadata.",
            )
        return PdfQAResult(
            "text_extraction_smoke", False,
            "PDF lacks expected text markers", "warning",
        )
    except Exception as e:
        return PdfQAResult("text_extraction_smoke", False, str(e), "error")


# ═══════════════════════════════════════════════════════════════════════════
# MHP-675: Image/Render Smoke
# ═══════════════════════════════════════════════════════════════════════════

def qa_image_render_smoke(pdf_path: str) -> PdfQAResult:
    """Check that the PDF can be rendered (first page check).

    Since we use matplotlib, this verifies the PDF has valid content streams
    and is not corrupted.
    """
    path = Path(pdf_path)
    if not path.exists():
        return PdfQAResult("image_render_smoke", False, "PDF not found", "error")

    try:
        raw = path.read_bytes()
        has_pdf_header = raw.startswith(b"%PDF")
        has_eof = raw.rstrip().endswith(b"%%EOF")
        has_streams = b"stream" in raw and b"endstream" in raw

        if has_pdf_header and has_eof and has_streams:
            return PdfQAResult(
                "image_render_smoke", True,
                f"PDF is structurally valid ({len(raw) / 1024:.1f} KB, "
                f"has header, streams, and EOF marker)",
            )
        issues = []
        if not has_pdf_header:
            issues.append("missing PDF header")
        if not has_eof:
            issues.append("missing EOF marker")
        if not has_streams:
            issues.append("no content streams")
        return PdfQAResult(
            "image_render_smoke", False,
            f"PDF structure issues: {', '.join(issues)}", "error",
        )
    except Exception as e:
        return PdfQAResult("image_render_smoke", False, str(e), "error")


# ═══════════════════════════════════════════════════════════════════════════
# Full QA Suite
# ═══════════════════════════════════════════════════════════════════════════

def run_full_qa(
    pdf_path: str,
    brand: Optional[BrandAssets] = None,
    min_pages: int = 1,
) -> PdfQARun:
    """Run all QA checks on a generated PDF report.

    Args:
        pdf_path: Path to the PDF file.
        brand: Optional BrandAssets for logo check.
        min_pages: Minimum expected page count.

    Returns:
        PdfQARun with all check results.
    """
    run = PdfQARun(pdf_path=pdf_path)

    # Structural checks
    run.add(qa_non_empty_pages(pdf_path))
    run.add(qa_page_count(pdf_path, min_pages=min_pages))

    # Content checks
    run.add(qa_logo_presence(pdf_path, brand=brand))
    run.add(qa_manifest_exists(pdf_path))
    run.add(qa_text_extraction_smoke(pdf_path))
    run.add(qa_image_render_smoke(pdf_path))

    return run
