"""MHP-634-635: PDF Brand Asset Management.

Brand asset resolver, logo loading, fallback behavior, and asset validation.
Part of ECHAIN-MOODIFY-PDF-REPORT-011 / NEM-PDF-FOUNDATION-PROBE-033.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")


# ── Canonical paths ──────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_LOGO_PATH = PROJECT_ROOT / "assets" / "brand" / "moodify_logo_symbol_original_white_canvas_1254.png"


@dataclass
class BrandAssets:
    """Resolved brand assets for PDF report generation."""

    logo_path: Optional[Path] = None
    logo_available: bool = False
    logo_error: str = ""
    project_root: Path = field(default_factory=lambda: PROJECT_ROOT)

    @classmethod
    def resolve(cls, logo_path: Optional[Path] = None) -> "BrandAssets":
        """Resolve brand assets. Uses canonical path if none provided.

        Args:
            logo_path: Optional override path for the logo file.

        Returns:
            BrandAssets with resolution status.
        """
        target = Path(logo_path) if logo_path else CANONICAL_LOGO_PATH

        assets = cls(logo_path=target, project_root=PROJECT_ROOT)

        if target.exists():
            assets.logo_available = True
            return assets

        # Try fallback locations
        fallbacks = [
            PROJECT_ROOT / "assets" / "moodify_logo.png",
            PROJECT_ROOT / "assets" / "logo.png",
            PROJECT_ROOT / "assets" / "brand" / "logo.png",
        ]
        for fb in fallbacks:
            if fb.exists():
                assets.logo_path = fb
                assets.logo_available = True
                return assets

        assets.logo_error = (
            f"Brand logo not found at canonical path: {target}. "
            f"Checked fallbacks: {[str(f) for f in fallbacks]}. "
            "PDF reports will be generated without logo."
        )
        return assets

    def load_image(self):
        """Load logo as a matplotlib image array.

        Returns:
            numpy array if logo is available, None otherwise.
        """
        if not self.logo_available or not self.logo_path:
            return None
        try:
            return matplotlib.pyplot.imread(str(self.logo_path))
        except Exception as e:
            self.logo_error = f"Failed to load logo image: {e}"
            self.logo_available = False
            return None

    def validate(self) -> dict:
        """Validate brand assets and return status dict."""
        result = {
            "logo_available": self.logo_available,
            "logo_path": str(self.logo_path) if self.logo_path else None,
        }
        if self.logo_error:
            result["error"] = self.logo_error
        return result
