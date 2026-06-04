"""MHP-636-638: PDF Page Templates and Theme.

Page template contract (header/body/footer), dark industrial theme,
figure export helper. Part of ECHAIN-MOODIFY-PDF-REPORT-011.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .pdf_assets import BrandAssets


# ═══════════════════════════════════════════════════════════════════════════
# MHP-637: Dark Industrial Theme
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class PdfTheme:
    """Dark industrial theme colors and typography for Acoustic CT reports."""

    # Colors
    bg_dark: str = "#0f0f1a"
    brand_color: str = "#1a1a2e"
    accent_color: str = "#e94560"
    grid_color: str = "#333355"
    text_color: str = "#eaeaea"
    text_muted: str = "#8888aa"
    warn_color: str = "#ff6b35"
    ok_color: str = "#2ecc71"

    # Typography
    font_family: str = "monospace"
    title_size: int = 14
    heading_size: int = 12
    body_size: int = 9
    small_size: int = 7

    # Layout
    page_width_inches: float = 8.27   # A4
    page_height_inches: float = 11.69
    dpi: int = 150
    header_height: float = 0.08
    footer_height: float = 0.06
    body_margin_left: float = 0.08
    body_margin_right: float = 0.92
    body_top: float = 0.88
    body_bottom: float = 0.10

    # Risk band colors
    risk_sub_bass: str = "#e94560"
    risk_low_mid: str = "#ff6b35"
    risk_harsh: str = "#ffaa00"
    risk_sibilance: str = "#ffdd00"
    safe_band: str = "#2ecc71"
    neutral_band: str = "#8888aa"

    def risk_band_color(self, band_name: str) -> str:
        """Return the color for a named risk band."""
        mapping = {
            "sub_bass": self.risk_sub_bass,
            "bass": self.safe_band,
            "low_mid": self.risk_low_mid,
            "mid": self.neutral_band,
            "presence": self.neutral_band,
            "harshness": self.risk_harsh,
            "sibilance": self.risk_sibilance,
            "air": self.neutral_band,
        }
        return mapping.get(band_name, self.neutral_band)


# Default theme instance
DEFAULT_THEME = PdfTheme()


# ═══════════════════════════════════════════════════════════════════════════
# MHP-636: Page Template Contract
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class PageTemplate:
    """A single PDF page with header/body/footer regions.

    Provides a stable contract: header preserves logo + title space,
    body is the content region, footer holds page number and metadata.
    """

    theme: PdfTheme = field(default_factory=lambda: DEFAULT_THEME)
    brand: BrandAssets = field(default_factory=BrandAssets.resolve)
    page_number: int = 1
    total_pages: int = 1

    def create_figure(self, title: str = "", subtitle: str = "") -> plt.Figure:
        """Create a matplotlib figure with the dark theme and brand header.

        Args:
            title: Main title for the page header.
            subtitle: Subtitle line below the title.

        Returns:
            A matplotlib Figure ready for content drawing.
        """
        fig = plt.figure(
            figsize=(self.theme.page_width_inches, self.theme.page_height_inches),
            facecolor=self.theme.bg_dark,
        )
        self._draw_header(fig, title, subtitle)
        self._draw_footer(fig)
        return fig

    def _draw_header(self, fig: plt.Figure, title: str, subtitle: str) -> None:
        """Draw the brand header with logo and title."""
        theme = self.theme

        # Logo
        if self.brand.logo_available and self.brand.logo_path:
            try:
                logo_img = plt.imread(str(self.brand.logo_path))
                ax_logo = fig.add_axes(
                    [0.02, 0.93, 0.05, 0.05], zorder=10
                )
                ax_logo.imshow(logo_img)
                ax_logo.axis("off")
            except Exception:
                pass  # Logo load failure is non-fatal

        # Title
        fig.text(
            0.10, 0.96, "MOODIFY ACOUSTIC CT",
            fontsize=theme.title_size, fontweight="bold",
            color=theme.accent_color, fontfamily=theme.font_family,
        )
        if subtitle:
            fig.text(
                0.10, 0.93, subtitle,
                fontsize=theme.small_size, color=theme.text_color,
                fontfamily=theme.font_family,
            )

    def _draw_footer(self, fig: plt.Figure) -> None:
        """Draw the page footer with page number and branding."""
        theme = self.theme
        footer_y = 0.03

        fig.text(
            0.08, footer_y,
            f"Moodify Acoustic CT Report | Page {self.page_number}/{self.total_pages}",
            ha="left", fontsize=theme.small_size, color=theme.text_muted,
            fontfamily=theme.font_family,
        )
        fig.text(
            0.92, footer_y,
            "Moodify PDF Report Module",
            ha="right", fontsize=theme.small_size, color=theme.text_muted,
            fontfamily=theme.font_family,
        )

    # ── Body region helpers ───────────────────────────────────────────

    def full_body_axes(self, fig: plt.Figure) -> plt.Axes:
        """Create axes filling the body region."""
        return fig.add_axes([
            self.theme.body_margin_left,
            self.theme.body_bottom,
            self.theme.body_margin_right - self.theme.body_margin_left,
            self.theme.body_top - self.theme.body_bottom,
        ])

    def top_half_axes(self, fig: plt.Figure) -> plt.Axes:
        """Create axes for the top half of the body."""
        mid = (self.theme.body_top + self.theme.body_bottom) / 2
        return fig.add_axes([
            self.theme.body_margin_left, mid,
            self.theme.body_margin_right - self.theme.body_margin_left,
            self.theme.body_top - mid,
        ])

    def bottom_half_axes(self, fig: plt.Figure) -> plt.Axes:
        """Create axes for the bottom half of the body."""
        mid = (self.theme.body_top + self.theme.body_bottom) / 2
        return fig.add_axes([
            self.theme.body_margin_left, self.theme.body_bottom,
            self.theme.body_margin_right - self.theme.body_margin_left,
            mid - self.theme.body_bottom,
        ])

    def style_axes(self, ax: plt.Axes) -> None:
        """Apply dark theme styling to an axes."""
        theme = self.theme
        ax.set_facecolor(theme.bg_dark)
        ax.tick_params(colors=theme.text_color, labelsize=theme.small_size)
        for spine in ax.spines.values():
            spine.set_color(theme.grid_color)
        ax.grid(True, alpha=0.15, color=theme.grid_color)


# ═══════════════════════════════════════════════════════════════════════════
# MHP-638: Figure Export Helper
# ═══════════════════════════════════════════════════════════════════════════

def export_figure_to_image(
    fig: plt.Figure,
    output_path: str,
    dpi: int = 150,
    facecolor: Optional[str] = None,
) -> str:
    """Export a matplotlib figure to an image file (PNG).

    Args:
        fig: The matplotlib Figure to export.
        output_path: Destination path (should end with .png).
        dpi: Resolution in dots per inch.
        facecolor: Background color (uses theme default if None).

    Returns:
        The output path on success.
    """
    bg = facecolor or DEFAULT_THEME.bg_dark
    fig.savefig(output_path, dpi=dpi, facecolor=bg, bbox_inches="tight")
    plt.close(fig)
    return output_path


def export_figure_to_pdf_page(
    fig: plt.Figure,
    pdf_pages,
    dpi: int = 150,
    facecolor: Optional[str] = None,
) -> None:
    """Add a matplotlib figure as a page in a PdfPages document.

    Args:
        fig: The matplotlib Figure to add.
        pdf_pages: A matplotlib.backends.backend_pdf.PdfPages instance.
        dpi: Resolution.
        facecolor: Background color.
    """
    bg = facecolor or DEFAULT_THEME.bg_dark
    fig.savefig(pdf_pages, format="pdf", dpi=dpi, facecolor=bg,
                bbox_inches="tight")
    plt.close(fig)


def render_summary_text_page(
    fig: plt.Figure,
    lines: list[str],
    title: str = "Report Summary",
    start_y: float = 0.82,
    line_height: float = 0.035,
) -> None:
    """Render a list of text lines onto a figure as a summary page.

    Args:
        fig: The figure to draw on.
        lines: List of text lines to render.
        title: Heading for the summary block.
        start_y: Starting y position (figure coordinates 0-1).
        line_height: Vertical spacing between lines.
    """
    theme = DEFAULT_THEME
    # Title
    fig.text(
        0.10, start_y + 0.02, title,
        fontsize=theme.heading_size, fontweight="bold",
        color=theme.accent_color, fontfamily=theme.font_family,
    )
    # Lines
    for i, line in enumerate(lines):
        y = start_y - i * line_height
        color = theme.warn_color if line.startswith("[!]") else theme.text_color
        fig.text(
            0.10, y, line,
            fontsize=theme.body_size, color=color,
            fontfamily=theme.font_family,
        )
