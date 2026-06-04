"""Tests for MRS engine + over_dark detection."""
import tempfile

import numpy as np
import pytest

from moodify_runtime.mrs_engine import MRSScoreResult
from moodify_runtime.over_dark import (
    OverDarkResult, _band_energy_fft, _compute_band_energies, detect_over_dark,
)


def _make_sine_wav(path, sr=44100, freq=440.0, amplitude=0.5):
    import struct
    t = np.linspace(0, 1, sr, endpoint=False)
    samples = (amplitude * np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)
    with open(path, 'wb') as f:
        data_size = len(samples) * 2
        f.write(b'RIFF')
        f.write(struct.pack('<I', 36 + data_size))
        f.write(b'WAVE')
        f.write(b'fmt ')
        f.write(struct.pack('<IHHIIHH', 16, 1, 1, sr, sr * 2, 2, 16))
        f.write(b'data')
        f.write(struct.pack('<I', data_size))
        f.write(samples.tobytes())


class TestMRSScoreResult:
    def test_default_result(self):
        r = MRSScoreResult(sample_id="test")
        assert r.sample_id == "test"
        assert r.genre == ""
        assert r.over_dark_level == "none"

    def test_pseudo_mrs_fields(self):
        r = MRSScoreResult(sample_id="test", genre="pop", preset="warm_vocal",
                           pseudo_mrs_before=0.5, pseudo_mrs_after=0.72,
                           pseudo_mrs_delta=0.22)
        d = r.to_dict()
        assert d["pseudo_mrs_delta"] == pytest.approx(0.22)

    def test_over_dark_fields(self):
        r = MRSScoreResult(sample_id="test", over_dark_level="moderate",
                           over_dark_score=0.45,
                           over_dark_affected_bands=["low", "sub_bass"])
        assert r.over_dark_level == "moderate"
        assert len(r.over_dark_affected_bands) == 2

    def test_to_dict_all_keys_present(self):
        r = MRSScoreResult(sample_id="full", genre="rock", preset="clean_master",
                           pseudo_mrs_before=0.3, pseudo_mrs_after=0.7, pseudo_mrs_delta=0.4,
                           over_dark_level="none", gate_decision="PASS")
        d = r.to_dict()
        for k in ["sample_id", "genre", "preset", "pseudo_mrs_delta",
                   "over_dark_level", "gate_decision"]:
            assert k in d


class TestOverDark:
    def test_band_energy_sine(self):
        sr = 44100
        t = np.linspace(0, 1, sr, endpoint=False)
        samples = np.sin(2 * np.pi * 440 * t)
        e = _band_energy_fft(samples, sr, 200, 800)
        assert e > 0

    def test_band_energy_low_vs_mid(self):
        sr = 44100
        t = np.linspace(0, 1, sr, endpoint=False)
        samples = np.sin(2 * np.pi * 440 * t)
        low = _band_energy_fft(samples, sr, 20, 200)
        mid = _band_energy_fft(samples, sr, 200, 800)
        # A 440Hz tone should have more energy in mid than low
        assert mid > low

    def test_detect_over_dark_normal(self):
        path = tempfile.mktemp(suffix=".wav")
        _make_sine_wav(path, freq=1000, amplitude=0.7)
        result = detect_over_dark(path, path)  # before=after for smoke
        assert result.level in ("none", "mild", "moderate", "severe")

    def test_detect_over_dark_low(self):
        path = tempfile.mktemp(suffix=".wav")
        _make_sine_wav(path, freq=60, amplitude=0.3)
        result = detect_over_dark(path, path)
        assert result.level in ("none", "mild", "moderate", "severe")

    def test_over_dark_result_creation(self):
        r = OverDarkResult(
            level="moderate", score=0.45,
            affected_bands=["low", "sub_bass"],
            band_scores={"low": 0.6, "sub_bass": 0.5, "mid": 0.3, "high": 0.2},
            is_processing_induced=False,
            recommendation="Reduce bass boost",
        )
        assert r.level == "moderate"
        assert r.score == 0.45
        assert "low" in r.affected_bands
        assert not r.is_processing_induced

    def test_nonexistent_file_handled(self):
        result = detect_over_dark("/nonexistent/a.wav", "/nonexistent/b.wav")
        assert isinstance(result, OverDarkResult)
