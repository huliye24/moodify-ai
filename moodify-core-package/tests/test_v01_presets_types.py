"""Tests for Moodify v0.1.0 lightweight types and presets."""

import pytest

from moodify.v01_presets import PRESETS, get_preset, list_presets
from moodify.v01_types import AudioMetrics, DiagnosisReport, ProcessResult


EXPECTED_PRESETS = {"warm_vocal", "clean_master", "wide_space"}

EXPECTED_PARAM_KEYS = {
    "P01_vocal_presence_freq",
    "P02_vocal_presence_gain",
    "P03_vocal_presence_q",
    "P04_proximity_low_freq",
    "P05_proximity_low_gain",
    "P06_compression_ratio",
    "P07_compression_attack",
    "P08_compression_release",
    "P09_compression_threshold",
    "P10_reverb_t60",
    "P11_reverb_dry_wet",
    "P12_reverb_width",
    "P13_harmonic_drive",
    "P14_high_shelf_freq",
    "P15_high_shelf_gain",
}


@pytest.mark.v01
def test_v01_presets_are_exactly_three():
    assert set(list_presets()) == EXPECTED_PRESETS
    assert set(PRESETS.keys()) == EXPECTED_PRESETS


@pytest.mark.v01
@pytest.mark.parametrize("preset_key", sorted(EXPECTED_PRESETS))
def test_v01_each_preset_has_required_metadata_and_15_params(preset_key):
    preset = get_preset(preset_key)

    assert preset is not None
    assert isinstance(preset["name"], str)
    assert preset["name"]
    assert isinstance(preset["name_zh"], str)
    assert preset["name_zh"]
    assert isinstance(preset["description"], str)
    assert preset["description"]

    params = preset["params"]
    assert set(params.keys()) == EXPECTED_PARAM_KEYS

    for key, value in params.items():
        assert isinstance(key, str)
        assert isinstance(value, (int, float))


@pytest.mark.v01
def test_v01_get_preset_unknown_returns_none():
    assert get_preset("not_a_preset") is None


@pytest.mark.v01
def test_v01_audio_metrics_to_dict_shape():
    metrics = AudioMetrics(
        file_path="demo.wav",
        duration_s=3.2,
        sample_rate=44100,
        channels=2,
        rms_sub=-20.0,
        rms_bass=-12.0,
        rms_low_mid=-10.0,
        rms_mid=-8.0,
        rms_presence=-9.0,
        rms_air=-18.0,
        peak_db=-1.0,
        crest_factor=4.2,
        dynamic_range_db=7.5,
        correlation_lr=0.55,
    )

    data = metrics.to_dict()

    assert data["file_path"] == "demo.wav"
    assert data["duration_s"] == 3.2
    assert data["sample_rate"] == 44100
    assert data["channels"] == 2
    assert set(data.keys()) == {
        "file_path",
        "duration_s",
        "sample_rate",
        "channels",
        "spectrum",
        "dynamics",
        "stereo",
    }
    assert data["spectrum"]["bass"] == -12.0
    assert data["dynamics"]["crest_factor"] == 4.2
    assert data["stereo"]["correlation_lr"] == 0.55


@pytest.mark.v01
def test_v01_diagnosis_report_to_dict_shape():
    metrics = AudioMetrics(file_path="demo.wav")
    report = DiagnosisReport(
        metrics=metrics,
        overall_health="fair",
        issues=["issue 1"],
        strengths=["strength 1"],
        suggested_presets=["clean_master"],
    )

    data = report.to_dict()

    assert data["overall_health"] == "fair"
    assert data["issues"] == ["issue 1"]
    assert data["strengths"] == ["strength 1"]
    assert data["suggested_presets"] == ["clean_master"]
    assert data["metrics"]["file_path"] == "demo.wav"


@pytest.mark.v01
def test_v01_process_result_defaults_are_safe():
    result = ProcessResult(input_path="missing.wav", success=False, error="failed")

    assert result.input_path == "missing.wav"
    assert result.output_path == ""
    assert result.preset == ""
    assert result.success is False
    assert result.error == "failed"
