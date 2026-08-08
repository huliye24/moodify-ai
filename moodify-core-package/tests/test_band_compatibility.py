import numpy as np

from moodify.bands import BAND_7_EDGES, BAND_7_NAMES, get_band_edges
from moodify.v01_analyzer import _compute_band_rms


def test_seven_band_definitions_are_in_frequency_order():
    names = [name for name, _low, _high in BAND_7_EDGES]
    assert names == BAND_7_NAMES
    assert names[-2:] == ["brilliance", "air"]


def test_legacy_six_band_analysis_does_not_emit_brilliance():
    sr = 16000
    t = np.arange(sr, dtype=np.float64) / sr
    signal = np.sin(2.0 * np.pi * 6000.0 * t)
    legacy = _compute_band_rms(signal, sr, get_band_edges("6"))
    current = _compute_band_rms(signal, sr, get_band_edges("7"))
    assert "brilliance" not in legacy
    assert "brilliance" in current
