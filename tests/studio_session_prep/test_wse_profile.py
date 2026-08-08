"""Tests for WSE profile generation — deterministic synthetic signals."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from tools.studio_session_prep.metrics_adapter import (
    band_fractions,
    comparison_metrics,
    left_right_correlation,
    level_metrics,
    loudness_metrics,
    spectral_metrics,
)
from tools.studio_session_prep.wse_profile import (
    WseProfile,
    compute_wse_profile,
    compute_window_evolution,
    _linear_to_db,
)


# ── Synthetic signal factories ────────────────────────────────

def make_silence(duration_s: float = 1.0, sr: int = 48000):
    samples = int(sr * duration_s)
    return np.zeros(samples, dtype=np.float64), sr


def make_sine(freq: float, duration_s: float = 1.0, sr: int = 48000, amp: float = 0.5):
    samples = int(sr * duration_s)
    t = np.linspace(0, duration_s, samples, endpoint=False)
    return (amp * np.sin(2 * np.pi * freq * t)).astype(np.float64), sr


def make_stereo_sine(freq: float = 440, duration_s: float = 1.0, sr: int = 48000, amp: float = 0.5):
    samples = int(sr * duration_s)
    t = np.linspace(0, duration_s, samples, endpoint=False)
    left = amp * np.sin(2 * np.pi * freq * t)
    right = amp * np.sin(2 * np.pi * freq * t)
    return np.column_stack([left, right]).astype(np.float64), sr


def make_stereo_out_of_phase(freq: float = 440, duration_s: float = 1.0, sr: int = 48000, amp: float = 0.5):
    samples = int(sr * duration_s)
    t = np.linspace(0, duration_s, samples, endpoint=False)
    left = amp * np.sin(2 * np.pi * freq * t)
    right = -amp * np.sin(2 * np.pi * freq * t)
    return np.column_stack([left, right]).astype(np.float64), sr


def make_mixed_freq(duration_s: float = 1.0, sr: int = 48000):
    samples = int(sr * duration_s)
    t = np.linspace(0, duration_s, samples, endpoint=False)
    y = (
        0.3 * np.sin(2 * np.pi * 100 * t) +
        0.3 * np.sin(2 * np.pi * 1000 * t) +
        0.15 * np.sin(2 * np.pi * 5000 * t)
    )
    return y.astype(np.float64), sr


def make_known_gain(gain_linear: float, duration_s: float = 1.0, sr: int = 48000):
    y, sr = make_sine(440, duration_s, sr, amp=0.5)
    return y * gain_linear, sr


class TestLevelMetrics:
    def test_sine_peak(self):
        y, sr = make_sine(440, amp=0.5)
        result = level_metrics(y)
        assert result.values["peak"] == pytest.approx(0.5, abs=0.01)
        assert result.values["rms"] == pytest.approx(0.5 / np.sqrt(2), abs=0.01)

    def test_silence(self):
        y, sr = make_silence()
        result = level_metrics(y)
        assert result.values["rms"] == pytest.approx(0.0, abs=1e-6)
        assert result.values["crest_factor"] is None

    def test_known_gain(self):
        y1, _ = make_known_gain(1.0)
        y2, _ = make_known_gain(2.0)
        r1 = level_metrics(y1)
        r2 = level_metrics(y2)
        assert r2.values["peak"] == pytest.approx(2 * r1.values["peak"], rel=0.01)

    def test_empty_signal(self):
        result = level_metrics(np.array([], dtype=np.float64))
        assert result.values["peak"] is None
        assert len(result.warnings) > 0


class TestSpectralMetrics:
    def test_sine_centroid(self):
        y, sr = make_sine(1000, duration_s=2.0)
        result = spectral_metrics(y, sr)
        assert result.values["spectral_centroid_hz"] is not None
        assert result.values["spectral_centroid_hz"] == pytest.approx(1000, rel=0.15)

    def test_sine_entropy(self):
        y, sr = make_sine(440, duration_s=2.0)
        result = spectral_metrics(y, sr)
        assert result.values["spectral_entropy"] is not None
        # Pure sine has low entropy
        assert result.values["spectral_entropy"] < 0.5

    def test_mixed_entropy(self):
        y, sr = make_mixed_freq(duration_s=2.0)
        result = spectral_metrics(y, sr)
        mixed_entropy = result.values["spectral_entropy"]
        y_sine, sr_sine = make_sine(440, duration_s=2.0)
        sine_entropy = spectral_metrics(y_sine, sr_sine).values["spectral_entropy"]
        assert mixed_entropy is not None and sine_entropy is not None
        # Mixed signal should have higher entropy than pure sine
        assert mixed_entropy > sine_entropy

    def test_short_signal(self):
        y = np.array([0.1, 0.2], dtype=np.float64)
        result = spectral_metrics(y, 48000, frame_size=2048)
        assert result.values["spectral_centroid_hz"] is None

    def test_deterministic(self):
        np.random.seed(42)
        y = np.random.randn(48000).astype(np.float64)
        r1 = spectral_metrics(y, 48000)
        np.random.seed(42)
        y = np.random.randn(48000).astype(np.float64)
        r2 = spectral_metrics(y, 48000)
        assert r1.values == r2.values


class TestBandFractions:
    def test_sine_in_correct_band(self):
        y, sr = make_sine(1000, duration_s=2.0)
        result = band_fractions(y, sr)
        # 1000 Hz should be in band 250-2000
        bf = result.values["band_250_2000_fraction"]
        assert bf is not None
        assert bf > 0.5  # most energy in this band

    def test_silence_returns_null(self):
        y, sr = make_silence()
        result = band_fractions(y, sr)
        assert all(v is None for v in result.values.values())

    def test_sum_is_one(self):
        y, sr = make_mixed_freq(duration_s=2.0)
        result = band_fractions(y, sr)
        total = sum(v for v in result.values.values() if v is not None)
        assert total == pytest.approx(1.0, abs=0.01)


class TestLeftRightCorrelation:
    def test_stereo_in_phase(self):
        y, sr = make_stereo_in_phase_440(duration_s=2.0)
        result = left_right_correlation(y)
        assert result.values["left_right_correlation"] == pytest.approx(1.0, abs=0.01)

    def test_stereo_out_of_phase(self):
        y, sr = make_stereo_out_of_phase()
        result = left_right_correlation(y)
        assert result.values["left_right_correlation"] == pytest.approx(-1.0, abs=0.01)

    def test_mono_is_null(self):
        y = np.array([0.1, 0.2, 0.1], dtype=np.float64)
        result = left_right_correlation(y)
        assert result.values["left_right_correlation"] is None

    def test_constant_signal_null(self):
        y = np.ones((100, 2), dtype=np.float64)
        result = left_right_correlation(y)
        assert result.values["left_right_correlation"] is None


class TestComparisonMetrics:
    def test_identical_signals(self):
        y, _ = make_sine(440)
        result = comparison_metrics(y, y)
        assert result.values["waveform_correlation"] == pytest.approx(1.0, abs=0.01)
        assert result.values["fitted_scalar_gain"] == pytest.approx(1.0, abs=0.01)
        assert result.values["relative_residual"] == pytest.approx(0.0, abs=0.01)
        assert result.values["difference_snr_db"] > 60  # very high SNR

    def test_gain_difference(self):
        y1, _ = make_known_gain(1.0)
        y2, _ = make_known_gain(2.0)
        result = comparison_metrics(y1, y2)
        assert result.values["fitted_scalar_gain"] == pytest.approx(2.0, rel=0.01)

    def test_different_lengths_null(self):
        y1 = np.array([0.1, 0.2], dtype=np.float64)
        y2 = np.array([0.1], dtype=np.float64)
        result = comparison_metrics(y1, y2)
        assert result.values["waveform_correlation"] is None


class TestLoudnessMetrics:
    def test_pyloudnorm_available_or_graceful(self):
        """Should either return LUFS or null with warnings — never crash."""
        y, sr = make_sine(1000, duration_s=3.0)
        result = loudness_metrics(y, sr)
        # LRA and true peak must ALWAYS be null
        assert result.values["lra_lu"] is None
        assert result.values["true_peak_dbtp"] is None
        # LUFS may be available
        if result.values["loudness_lufs"] is not None:
            assert isinstance(result.values["loudness_lufs"], float)

    def test_lra_true_peak_always_null(self):
        """Even with pyloudnorm, LRA and true peak must be null."""
        y, sr = make_sine(1000, duration_s=3.0)
        result = loudness_metrics(y, sr)
        assert result.values["lra_lu"] is None
        assert result.values["true_peak_dbtp"] is None


class TestWseProfile:
    def test_profile_on_sine(self, tmp_path):
        """End-to-end WSE profile on synthetic audio."""
        import soundfile as sf

        y, sr = make_sine(1000, duration_s=1.0)
        audio_path = tmp_path / "test.wav"
        sf.write(str(audio_path), y, sr)

        from tools.studio_session_prep.studio_prep import _sha256_file
        sha = _sha256_file(audio_path)

        profile = compute_wse_profile(str(audio_path), source_sha256=sha)
        assert profile.peak_linear is not None
        assert profile.rms_linear is not None
        assert profile.crest_factor is not None
        assert profile.spectral_centroid_hz is not None
        assert profile.left_right_correlation is None  # mono → null
        # Explicit nulls
        assert profile.lra_lu is None
        assert profile.true_peak_dbtp is None
        assert profile.phase_rotation_deg is None
        assert profile.masking_index is None

    def test_profile_to_dict(self, tmp_path):
        import soundfile as sf

        y, sr = make_sine(1000, duration_s=1.0)
        audio_path = tmp_path / "test.wav"
        sf.write(str(audio_path), y, sr)

        from tools.studio_session_prep.studio_prep import _sha256_file
        sha = _sha256_file(audio_path)

        profile = compute_wse_profile(str(audio_path), source_sha256=sha)
        d = profile.to_dict()
        assert d["profile_version"] == "1.0.0"
        assert "unavailable" in d
        # All unavailable keys present
        assert "lra_lu" in d["unavailable"]
        assert "true_peak_dbtp" in d["unavailable"]
        assert "phase_rotation_deg" in d["unavailable"]
        assert "masking_index" in d["unavailable"]
        # All values are "null — ..." strings
        for k, v in d["unavailable"].items():
            assert v.startswith("null"), f"{k} should start with 'null'"

    def test_silence_profile(self, tmp_path):
        import soundfile as sf

        y, sr = make_silence(duration_s=0.5)
        audio_path = tmp_path / "silence.wav"
        sf.write(str(audio_path), y, sr)

        profile = compute_wse_profile(str(audio_path))
        # Silence should have warnings
        assert len(profile.warnings) > 0
        # Crest factor should be null for silence
        assert profile.crest_factor is None


class TestWindowEvolution:
    def test_windows_on_sine(self, tmp_path):
        import soundfile as sf

        y, sr = make_sine(1000, duration_s=2.0)
        audio_path = tmp_path / "test.wav"
        sf.write(str(audio_path), y, sr)

        windows, count = compute_window_evolution(str(audio_path), frame_size=2048, hop_size=1024)
        # 2s @ 48kHz = 96000 samples. windows ≈ (96000-2048)/1024 ≈ 91
        assert count > 0
        assert count == len(windows)
        assert all("window_index" in w for w in windows)
        assert all("time_s" in w for w in windows)
        assert all("rms_linear" in w for w in windows)
        assert all("peak_linear" in w for w in windows)

    def test_short_audio_no_windows(self):
        y = np.array([0.1, 0.2], dtype=np.float64)
        import soundfile as sf
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            sf.write(f.name, y, 48000)
            windows, count = compute_window_evolution(f.name, frame_size=2048)
        assert count == 0
        assert windows == []


# ── helper ────────────────────────────────────────────────────

def make_stereo_in_phase_440(duration_s=1.0, sr=48000):
    return make_stereo_sine(440, duration_s, sr)
