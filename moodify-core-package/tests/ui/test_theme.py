"""Moodify brand shell — asset presence and packaging pins.

The white one-shell product carries the company logo (brand asset committed
under ``moodify/ui/assets/``). These tests pin the assets' existence and
format so a packaging regression (wheel missing the assets) fails loudly;
the Tk rendering itself is exercised on the desktop.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from moodify.ui.theme import ICON_PATH, LOGO_PATH

pytestmark = pytest.mark.v01

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def test_logo_asset_is_committed_and_valid_png():
    assert LOGO_PATH.is_file(), "brand logo missing from moodify/ui/assets"
    assert LOGO_PATH.read_bytes()[:8] == _PNG_MAGIC


def test_icon_asset_is_committed_and_valid_png():
    assert ICON_PATH.is_file(), "window icon missing from moodify/ui/assets"
    assert ICON_PATH.read_bytes()[:8] == _PNG_MAGIC


def test_theme_colors_are_the_white_product_shell():
    from moodify.ui.theme import ACCENT, BG_WHITE, FG_TEXT

    assert BG_WHITE == "#ffffff"
    assert FG_TEXT.startswith("#")
    assert ACCENT.startswith("#")


def test_assets_are_declared_as_package_data():
    pyproject = Path(__file__).parents[2] / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8")
    assert '[tool.setuptools.package-data]' in text
    assert '"moodify.ui" = ["assets/*.png"]' in text
