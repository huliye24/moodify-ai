"""Tests for over_dark."""
import tempfile, struct
import numpy as np
from pathlib import Path
from moodify_runtime.over_dark import (
    OverDarkResult, _read_pcm_mono, _band_energy_fft, _compute_band_energies, detect_over_dark,
)

def _make_wav(path, sr=44100, freq=440.0, amp=0.5):
    t = np.linspace(0, 1, sr, endpoint=False)
    samples = (amp * np.sin(2*np.pi*freq*t) * 32767).astype(np.int16)
    with open(path, 'wb') as f:
        ds = len(samples)*2
        f.write(b'RIFF'); f.write(struct.pack('<I', 36+ds)); f.write(b'WAVE')
        f.write(b'fmt '); f.write(struct.pack('<IHHIIHH', 16, 1, 1, sr, sr*2, 2, 16))
        f.write(b'data'); f.write(struct.pack('<I', ds)); f.write(samples.tobytes())

class TestRead:
    def test_mono(self):
        path = tempfile.mktemp(suffix=".wav"); _make_wav(path)
        samples, sr = _read_pcm_mono(path)
        assert sr == 44100 and len(samples) > 0

class TestBandEnergy:
    def test_positive(self):
        sr = 44100; t = np.linspace(0, 1, sr, endpoint=False)
        samples = np.sin(2*np.pi*440*t)
        assert _band_energy_fft(samples, sr, 200, 800) > 0

class TestBandEnergies:
    def test_returns_dict(self):
        path = tempfile.mktemp(suffix=".wav"); _make_wav(path)
        energies = _compute_band_energies(path)
        assert isinstance(energies, dict)
        assert len(energies) > 0

class TestDetect:
    def test_normal(self):
        path = tempfile.mktemp(suffix=".wav"); _make_wav(path)
        r = detect_over_dark(path, path)
        assert isinstance(r, OverDarkResult)

class TestResult:
    def test_full(self):
        r = OverDarkResult(level="moderate", score=0.45, affected_bands=["low"],
                          band_scores={"low":0.6,"mid":0.3,"high":0.2},
                          is_processing_induced=False, recommendation="fix")
        assert r.level == "moderate"
