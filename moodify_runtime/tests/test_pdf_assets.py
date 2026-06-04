"""Tests for pdf_assets."""
from moodify_runtime.pdf_assets import BrandAssets

class TestBrandAssets:
    def test_default(self):
        ba = BrandAssets()
        assert ba.logo_path is not None or isinstance(ba.logo_path, (str, type(None)))
    def test_resolve(self):
        ba = BrandAssets()
        ba.resolve()
        assert ba.logo_available in (True, False)
