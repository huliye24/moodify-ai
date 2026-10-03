"""Moodify brand shell — white theme, logo, window icon (one-shell product).

The product definition (human, 2026-10-02): Moodify is the company's desktop
software — ONE shell, white, carrying the company logo, with the flow fixed
as: pick a song → detect → data & charts → repair/mixing plan. This module
owns the shared brand surface so both the app hub and the report view render
identically. The logo is a company brand asset committed under
``moodify/ui/assets/``; every accessor degrades gracefully to text if the
asset is missing (a broken brand must never crash the measurement tool).
"""

from __future__ import annotations

from pathlib import Path

BG_WHITE = "#ffffff"
FG_TEXT = "#16181d"
FG_MUTED = "#6b7280"
HAIRLINE = "#e5e7eb"
ACCENT = "#4f46e5"  # taken from the logo's violet-blue wave

_ASSETS = Path(__file__).parent / "assets"
LOGO_PATH = _ASSETS / "moodify_logo.png"
ICON_PATH = _ASSETS / "moodify_icon_64.png"

_WINDOW_TITLE = "Moodify"


def apply_white_theme(root, style) -> None:
    """White product shell: white surfaces, hairline separators, quiet accent."""
    style.configure(".", background=BG_WHITE, foreground=FG_TEXT)
    style.configure("TFrame", background=BG_WHITE)
    style.configure("TLabel", background=BG_WHITE, foreground=FG_TEXT)
    style.configure("Muted.TLabel", background=BG_WHITE, foreground=FG_MUTED)
    style.configure("TButton", background=BG_WHITE, foreground=FG_TEXT,
                    bordercolor=HAIRLINE, focuscolor=ACCENT, padding=(10, 4))
    style.map("TButton", background=[("active", "#f3f4f6")])
    style.configure("TNotebook", background=BG_WHITE, bordercolor=BG_WHITE)
    style.configure("TNotebook.Tab", background=BG_WHITE, foreground=FG_MUTED,
                    padding=(16, 7))
    style.map("TNotebook.Tab",
              background=[("selected", BG_WHITE)],
              foreground=[("selected", FG_TEXT)])
    style.configure("Treeview", background=BG_WHITE, fieldbackground=BG_WHITE,
                    foreground=FG_TEXT, rowheight=26, bordercolor=HAIRLINE)
    style.configure("Treeview.Heading", background=BG_WHITE, foreground=FG_MUTED)
    style.map("Treeview", background=[("selected", "#eef2ff")])
    style.configure("TLabelframe", background=BG_WHITE, bordercolor=HAIRLINE)
    style.configure("TLabelframe.Label", background=BG_WHITE, foreground=FG_MUTED)
    style.configure("Badge.TLabel", background="#eef2ff", foreground=ACCENT,
                    padding=(8, 2))
    root.configure(background=BG_WHITE)


def load_logo(width: int = 280):
    """Return a ``tk.PhotoImage`` of the company logo, or None when absent.

    ``tk.PhotoImage`` subsampling keeps this dependency-free (no PIL at
    runtime); the committed asset is pre-scaled, so the factor stays small.
    """
    if not LOGO_PATH.is_file():
        return None
    import tkinter as tk

    try:
        photo = tk.PhotoImage(file=str(LOGO_PATH))
    except Exception:
        return None
    factor = max(1, round(photo.width() / width))
    if factor > 1:
        photo = photo.subsample(factor)
    return photo


def set_app_icon(root) -> None:
    """Set the window icon from the brand mark; silent when unavailable."""
    if not ICON_PATH.is_file():
        return
    try:
        import tkinter as tk

        root.iconphoto(True, tk.PhotoImage(file=str(ICON_PATH)))
    except Exception:
        pass
