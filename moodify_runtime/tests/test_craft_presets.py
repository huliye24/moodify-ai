"""Tests for craft_presets."""
from moodify_runtime.craft_presets import (
    PresetCategory, PresetMetadata, load_preset_metadata, validate_preset_safety,
)

class TestPresetMetadata:
    def test_load_warm_vocal(self):
        m = load_preset_metadata("warm_vocal")
        assert m is not None
        assert m.name == "warm_vocal"
    def test_load_clean_master(self):
        m = load_preset_metadata("clean_master")
        assert m is not None
    def test_load_wide_space(self):
        m = load_preset_metadata("wide_space")
        assert m is not None

class TestSafetyGate:
    def test_validate(self):
        result = validate_preset_safety("warm_vocal", "/tmp/test.wav")
        assert result is not None
