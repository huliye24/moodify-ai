"""MHP-639-663: Moodify Cloud PDF Report Module.

Reusable PDF report generation for acoustic CT scans, before/after comparisons,
and diagnostic reports. Uses matplotlib.backends.backend_pdf.PdfPages as the
core PDF engine with the dark industrial theme.

Part of ECHAIN-MOODIFY-PDF-REPORT-011.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

from .pdf_assets import BrandAssets, CANONICAL_LOGO_PATH
from .pdf_templates import (
    DEFAULT_THEME,
    PageTemplate,
    PdfTheme,
    export_figure_to_image,
    export_figure_to_pdf_page,
    render_summary_text_page,
)
from .utils import utc_now_iso


# ═══════════════════════════════════════════════════════════════════════════
# MHP-632: PdfReportConfig
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class PdfReportConfig:
    """Configuration for PDF report generation.

    MHP-632: Define PdfReportConfig — includes page size, theme, brand asset,
    footer, output dir.
    """

    output_dir: Path = field(default_factory=lambda: Path("outputs/pdf_reports"))
    page_size: Tuple[float, float] = (8.27, 11.69)  # A4 inches
    dpi: int = 150
    theme: PdfTheme = field(default_factory=lambda: DEFAULT_THEME)
    brand: BrandAssets = field(default_factory=BrandAssets.resolve)
    include_manifest: bool = True
    include_metadata: bool = True
    report_id_prefix: str = "PDFR"

    def resolved(self) -> "PdfReportConfig":
        """Return a copy with resolved paths."""
        result = PdfReportConfig(
            output_dir=self.output_dir.resolve(),
            page_size=self.page_size,
            dpi=self.dpi,
            theme=self.theme,
            brand=self.brand,
            include_manifest=self.include_manifest,
            include_metadata=self.include_metadata,
            report_id_prefix=self.report_id_prefix,
        )
        result.output_dir.mkdir(parents=True, exist_ok=True)
        return result


# ═══════════════════════════════════════════════════════════════════════════
# MHP-633: PdfReportManifest
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class PdfReportManifest:
    """JSON manifest linking source audio, processed audio, plots, and PDF.

    MHP-633: Define PdfReportManifest — links source audio, processed audio,
    plots, PDF.
    """

    report_id: str
    report_type: str  # "single" | "comparison"
    source_audio: str = ""
    processed_audio: str = ""
    preset: str = ""
    genre: str = ""
    pdf_path: str = ""
    pages: int = 0
    plates: List[str] = field(default_factory=list)
    mrs_before: Optional[float] = None
    mrs_after: Optional[float] = None
    mrs_delta: Optional[float] = None
    defect_flags: List[str] = field(default_factory=list)
    processing_chain: List[Dict[str, Any]] = field(default_factory=list)
    quality_score: Optional[float] = None
    generated_at: str = field(default_factory=utc_now_iso)
    generator_version: str = "0.1.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "report_type": self.report_type,
            "source_audio": self.source_audio,
            "processed_audio": self.processed_audio,
            "preset": self.preset,
            "genre": self.genre,
            "pdf_path": self.pdf_path,
            "pages": self.pages,
            "plates": self.plates,
            "mrs_before": self.mrs_before,
            "mrs_after": self.mrs_after,
            "mrs_delta": self.mrs_delta,
            "defect_flags": self.defect_flags,
            "processing_chain": self.processing_chain,
            "quality_score": self.quality_score,
            "generated_at": self.generated_at,
            "generator_version": self.generator_version,
        }

    def write(self, path: Optional[Path] = None) -> Path:
        """Write manifest to JSON file alongside the PDF."""
        if path is None:
            path = Path(self.pdf_path).with_suffix(".manifest.json")
        path.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return path


# ═══════════════════════════════════════════════════════════════════════════
# MHP-639: PDF Writer Skeleton
# ═══════════════════════════════════════════════════════════════════════════

class PdfReportWriter:
    """Main PDF report writer using matplotlib.backends.backend_pdf.PdfPages.

    MHP-639: Implement PDF Writer Skeleton — can create a one-page branded PDF
    on cloud.
    """

    def __init__(self, config: Optional[PdfReportConfig] = None):
        self.config = (config or PdfReportConfig()).resolved()
        self.theme = self.config.theme
        self.brand = self.config.brand
        self._pages: List[plt.Figure] = []
        self._template = PageTemplate(theme=self.theme, brand=self.brand)

    @property
    def page_count(self) -> int:
        return len(self._pages)

    def add_figure(self, fig: plt.Figure) -> None:
        """Add a pre-built matplotlib figure as a page."""
        self._pages.append(fig)

    def add_cover_page(self, title: str, subtitle: str = "",
                       info_lines: Optional[List[str]] = None) -> None:
        """Add a branded cover page.

        MHP-641: Add Metadata Block — cover page includes report id, preset,
        source, timestamp.
        """
        fig = self._template.create_figure(title, subtitle)
        body_start = 0.70

        if info_lines:
            render_summary_text_page(
                fig, info_lines, title="Report Information",
                start_y=body_start,
            )

        self._pages.append(fig)

    def add_text_page(self, title: str, lines: List[str]) -> None:
        """Add a text-only summary page."""
        fig = self._template.create_figure(title)
        render_summary_text_page(fig, lines, title=title)
        self._pages.append(fig)

    def write_pdf(self, output_path: str) -> str:
        """Write all accumulated pages to a single PDF file.

        Returns the output path.
        """
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with PdfPages(str(output)) as pdf:
            for i, fig in enumerate(self._pages):
                self._template.page_number = i + 1
                self._template.total_pages = len(self._pages)
                # Redraw footer with updated page numbers
                self._template._draw_footer(fig)
                export_figure_to_pdf_page(fig, pdf, dpi=self.config.dpi)

        return str(output)

    def clear(self) -> None:
        """Reset accumulated pages."""
        for fig in self._pages:
            plt.close(fig)
        self._pages.clear()


# ═══════════════════════════════════════════════════════════════════════════
# MHP-642: Output Path Policy
# ═══════════════════════════════════════════════════════════════════════════

def build_report_output_path(
    config: PdfReportConfig,
    report_id: str,
    report_type: str = "single",
) -> Path:
    """Build deterministic output path for a PDF report.

    MHP-642: Reports land in deterministic output directories.

    Structure: {output_dir}/{report_type}/{report_id}.pdf
    """
    subdir = config.output_dir / report_type
    subdir.mkdir(parents=True, exist_ok=True)
    return subdir / f"{report_id}.pdf"


def generate_report_id(prefix: str = "PDFR") -> str:
    """Generate a unique report ID."""
    return f"{prefix}_{uuid.uuid4().hex[:8].upper()}"


# ═══════════════════════════════════════════════════════════════════════════
# MHP-660: PDF Filename Policy
# ═══════════════════════════════════════════════════════════════════════════

def build_operator_friendly_filename(
    sample_id: str = "",
    preset: str = "",
    report_type: str = "ct_scan",
    extension: str = ".pdf",
) -> str:
    """Build an operator-friendly, deterministic PDF filename.

    MHP-660: Names are deterministic and operator-friendly.

    Pattern: {sample_id}_{preset}_{report_type}{extension}
    """
    parts = []
    if sample_id:
        parts.append(sample_id.replace(" ", "_")[:32])
    if preset:
        parts.append(preset.replace(" ", "_")[:24])
    parts.append(report_type)
    base = "_".join(parts)
    # Sanitize for filesystem
    safe = "".join(c if c.isalnum() or c in "_-" else "_" for c in base)
    return f"{safe}{extension}"


# ═══════════════════════════════════════════════════════════════════════════
# MHP-654: Before/After Comparison Layout
# ═══════════════════════════════════════════════════════════════════════════

def create_comparison_page(
    before_data: np.ndarray,
    after_data: np.ndarray,
    x_axis: np.ndarray,
    title: str = "Before/After Comparison",
    before_label: str = "Before",
    after_label: str = "After",
    y_label: str = "",
    theme: Optional[PdfTheme] = None,
) -> plt.Figure:
    """Create a side-by-side before/after comparison figure.

    MHP-654: Before/After comparison uses shared scales for before and after.
    """
    theme = theme or DEFAULT_THEME
    template = PageTemplate(theme=theme)

    fig = template.create_figure(title)

    # Top: Before
    ax1 = template.top_half_axes(fig)
    ax1.plot(x_axis, before_data, color=theme.accent_color, linewidth=0.8)
    ax1.set_ylabel(f"{before_label}\n{y_label}", color=theme.text_color, fontsize=theme.small_size)
    ax1.set_title(before_label, color=theme.text_color, fontsize=theme.body_size)
    template.style_axes(ax1)

    # Bottom: After
    ax2 = template.bottom_half_axes(fig)
    ax2.plot(x_axis, after_data, color=theme.ok_color, linewidth=0.8)
    ax2.set_ylabel(f"{after_label}\n{y_label}", color=theme.text_color, fontsize=theme.small_size)
    ax2.set_title(after_label, color=theme.text_color, fontsize=theme.body_size)
    ax2.set_xlabel("Time (s)", color=theme.text_color, fontsize=theme.small_size)
    template.style_axes(ax2)

    # Match y-axis limits
    y_min = min(before_data.min(), after_data.min())
    y_max = max(before_data.max(), after_data.max())
    ax1.set_ylim(y_min, y_max)
    ax2.set_ylim(y_min, y_max)

    return fig


# ═══════════════════════════════════════════════════════════════════════════
# MHP-655: Delta Chart Page
# ═══════════════════════════════════════════════════════════════════════════

def create_delta_chart_page(
    before_data: np.ndarray,
    after_data: np.ndarray,
    x_labels: List[str],
    title: str = "Delta Analysis",
    theme: Optional[PdfTheme] = None,
) -> plt.Figure:
    """Create a delta chart showing change across categories.

    MHP-655: Shows change in energy, risk, loudness, MRS if available.
    """
    theme = theme or DEFAULT_THEME
    template = PageTemplate(theme=theme)

    fig = template.create_figure(title, "Change Analysis (After − Before)")

    deltas = after_data - before_data
    colors = [theme.ok_color if d >= 0 else theme.accent_color for d in deltas]

    ax = template.full_body_axes(fig)
    bars = ax.bar(range(len(deltas)), deltas, color=colors, alpha=0.8)
    ax.axhline(0, color=theme.text_color, linewidth=0.5)
    ax.set_xticks(range(len(deltas)))
    ax.set_xticklabels(x_labels, rotation=45, ha="right",
                       color=theme.text_color, fontsize=6)
    ax.set_ylabel("Δ (After − Before)", color=theme.text_color, fontsize=theme.body_size)
    template.style_axes(ax)

    # Value labels on bars
    for bar, delta in zip(bars, deltas):
        y_pos = bar.get_height()
        offset = 0.02 * max(abs(deltas)) if max(abs(deltas)) > 0 else 0.01
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            y_pos + (offset if y_pos >= 0 else -offset * 2),
            f"{delta:+.2f}",
            ha="center", va="bottom" if y_pos >= 0 else "top",
            fontsize=6, color=theme.text_color,
        )

    return fig


# ═══════════════════════════════════════════════════════════════════════════
# MHP-659: CT Quality Score
# ═══════════════════════════════════════════════════════════════════════════

def compute_ct_quality_score(manifest: PdfReportManifest) -> float:
    """Compute a CT quality score for a report.

    MHP-659: Report includes scan completeness and visual QA status.

    Score components:
    - Pages present: up to 40 points
    - Plates generated: up to 30 points
    - MRS data present: up to 15 points
    - No defect flags: up to 15 points
    """
    score = 0.0

    # Pages (1-4 pages = reasonable)
    if manifest.pages >= 1:
        score += 10
    if manifest.pages >= 2:
        score += 10
    if manifest.pages >= 3:
        score += 10
    if manifest.pages >= 4:
        score += 10

    # Plates
    for _ in manifest.plates:
        score += min(7.5, 30.0 / max(len(manifest.plates), 1))
    score = min(score, 70.0)  # Cap pages+plates at 70

    # MRS
    if manifest.mrs_before is not None:
        score += 7.5
    if manifest.mrs_after is not None:
        score += 7.5

    # Defects
    if len(manifest.defect_flags) == 0:
        score += 15
    else:
        score += max(0, 15 - len(manifest.defect_flags) * 3)

    return round(min(score, 100.0), 1)
