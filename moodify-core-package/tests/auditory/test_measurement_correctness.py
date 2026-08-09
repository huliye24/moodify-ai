"""Measurement correctness tests (MFY-PHASE1-DEPTH-001, Gates G2-G8).

Deterministic fixtures with analytic truth exercise the standards-backed
loudness/true-peak modules, registry integrity, sample-rate matrix,
mono/stereo behavior, estimator honesty and FFmpeg oracle comparison.
"""

from __future__ import annotations

import numpy as np
import pytest

from moodify.auditory.loudness import integrated_loudness_lufs, loudness_range_lu
from moodify.auditory.measurement_registry import load_registry, registry_summary
from moodify.auditory.metrics import compute_metrics
from moodify.auditory.true_peak import true_peak_db


# ---------------------------------------------------------------------------
# Deterministic fixture generators (F001-F010 families)
# ---------------------------------------------------------------------------

def _sine(seconds: float, gain: float, freq: float, sr: int,
          channels: int = 1, phase: float = 0.0) -> np.ndarray:
    t = np.arange(int(seconds * sr)) / sr
    mono = gain * np.sin(2 * np.pi * freq * t + phase)
    if channels == 1:
        return mono
    return np.stack([mono, mono], axis=1)


def _sine_stereo_inv(seconds: float, gain: float, freq: float, sr: int) -> np.ndarray:
    t = np.arange(int(seconds * sr)) / sr
    mono = gain * np.sin(2 * np.pi * freq * t)
    return np.stack([mono, -mono], axis=1)


def _inter_sample_peak_stress(sr: int) -> np.ndarray:
    """Waveform whose reconstructed peak exceeds the discrete sample peak."""
    # Alternating near-full-scale samples at a frequency that pushes the
    # interpolated waveform above the sample peak.
    n = sr // 4
    x = np.zeros(n)
    for i in range(0, n, 2):
        x[i] = 0.99 if (i // 2) % 2 == 0 else -0.99
    return x


def _dc(seconds: float, offset: float, sr: int, channels: int = 1) -> np.ndarray:
    mono = np.full(int(seconds * sr), offset)
    return mono if channels == 1 else np.stack([mono, mono], axis=1)


class _Probe:
    def __init__(self, sha256: str = "sha256:fixture"):
        self.sha256 = sha256


# ---------------------------------------------------------------------------
# Registry (G2)
# ---------------------------------------------------------------------------

def test_registry_loads_and_no_audit_required():
    registry = load_registry()
    metrics = registry["metrics"]
    assert len(metrics) >= 28
    assert all(entry["authority_class"] != "AUDIT_REQUIRED" for entry in metrics.values())
    summary = registry_summary(registry)
    assert summary["STANDARD_COMPLIANT"] >= 3  # loudness, LRA, true peak
    assert "ESTIMATOR" in summary and "PROXY" in summary


def test_registry_standard_metrics_have_reference_basis():
    registry = load_registry()
    for metric_id in ("integrated_lufs", "loudness_range_lu", "true_peak_dbfs"):
        assert registry["metrics"][metric_id]["authority_class"] == "STANDARD_COMPLIANT"
        assert registry["metrics"][metric_id].get("reference_basis")


# ---------------------------------------------------------------------------
# Analytic truth (G7, F002/F003/F004)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("sr", [44100, 48000, 96000])
@pytest.mark.parametrize("gain_db", [-3.0, -6.0, -12.0])
def test_sample_peak_rms_analytic(sr: int, gain_db: float):
    gain = 10 ** (gain_db / 20)
    x = _sine(2.0, gain, 1000.0, sr)
    metrics = compute_metrics(x, sr, _Probe())
    assert metrics["sample_peak_dbfs"]["value"] == pytest.approx(gain_db, abs=0.01)
    assert metrics["rms_dbfs"]["value"] == pytest.approx(gain_db - 3.01, abs=0.02)


def test_dc_offset_analytic():
    x = _dc(1.0, 0.25, 48000)
    metrics = compute_metrics(x, 48000, _Probe())
    assert metrics["dc_offset_left"]["value"] == pytest.approx(0.25, abs=1e-7)


def test_clipping_count_exact():
    x = np.concatenate([np.full(10, 1.0), np.zeros(100)])
    metrics = compute_metrics(x, 48000, _Probe())
    assert metrics["clipping_sample_count"]["value"] == 10


def test_silence_ratio_exact():
    x = np.concatenate([np.zeros(4800), np.full(4800, 0.5)])
    metrics = compute_metrics(x, 48000, _Probe())
    assert metrics["silence_ratio"]["value"] == pytest.approx(0.5, abs=0.01)


# ---------------------------------------------------------------------------
# Loudness semantics (G4, G6)
# ---------------------------------------------------------------------------

def test_loudness_stereo_identity_matches_mono_energy():
    sr = 48000
    mono = _sine(3.0, 0.5, 440.0, sr)
    stereo_same = np.stack([mono, mono], axis=1)
    # Two identical channels: per-channel weighting sums to the same energy
    # as the mono single-channel value (weights L=R=1).
    assert integrated_loudness_lufs(stereo_same, sr) == pytest.approx(
        integrated_loudness_lufs(mono, sr), abs=0.05)


def test_loudness_short_content_returns_gated_floor():
    x = _sine(0.1, 0.5, 440.0, 48000)  # < 1 gating block
    assert integrated_loudness_lufs(x, 48000) == -70.0


def test_lra_insufficient_duration_unavailable():
    x = _sine(2.0, 0.5, 440.0, 48000)  # < 2 short-term blocks
    assert loudness_range_lu(x, 48000) is None
    metrics = compute_metrics(x, 48000, _Probe())
    assert metrics["loudness_range_lu"]["status"] == "UNAVAILABLE"
    assert metrics["loudness_range_lu"]["value"] is None


def test_lra_dynamics_family_positive():
    # Loud section followed by quiet section -> measurable LRA.
    sr = 48000
    loud = _sine(4.0, 0.9, 440.0, sr)
    quiet = _sine(4.0, 0.05, 440.0, sr)
    x = np.concatenate([loud, quiet])
    lra = loudness_range_lu(x, sr)
    assert lra is not None and lra > 3.0


# ---------------------------------------------------------------------------
# True peak (G5)
# ---------------------------------------------------------------------------

def test_true_peak_exceeds_sample_peak_on_stress():
    sr = 48000
    x = _inter_sample_peak_stress(sr)
    sample_peak = float(np.max(np.abs(x)))
    tp = 10 ** (true_peak_db(x, sr) / 20)
    assert tp > sample_peak  # reconstructed peak above discrete peak
    assert true_peak_db(x, sr) > 20 * np.log10(sample_peak + 1e-12)


def test_true_peak_sine_close_to_sample_peak():
    x = _sine(2.0, 0.9, 997.0, 48000)  # odd ratio avoids sample-on-peak
    tp = true_peak_db(x, 48000)
    sp = 20 * np.log10(float(np.max(np.abs(x))) + 1e-12)
    assert abs(tp - sp) < 0.5


# ---------------------------------------------------------------------------
# Stereo identities (G7, F006)
# ---------------------------------------------------------------------------

def test_stereo_correlation_identity_and_antiphase():
    from moodify.auditory.stereo import compute_stereo_metrics

    sr = 48000
    same = _sine(2.0, 0.5, 440.0, sr, channels=2)
    inverse = _sine_stereo_inv(2.0, 0.5, 440.0, sr)
    assert compute_stereo_metrics(same)["stereo_correlation"]["value"] == pytest.approx(1.0, abs=1e-3)
    assert compute_stereo_metrics(inverse)["stereo_correlation"]["value"] == pytest.approx(-1.0, abs=1e-3)


# ---------------------------------------------------------------------------
# Estimator honesty (G8, F008/F009)
# ---------------------------------------------------------------------------

def test_cutoff_estimator_tracks_lowpass_ladder():
    sr = 48000
    cutoffs = [8000, 10000, 12000, 14000]
    estimates = []
    for cutoff in cutoffs:
        n = sr // 2
        x = np.zeros(n)
        x[0] = 1.0
        freqs = np.fft.rfftfreq(n, 1 / sr)
        spec = np.fft.rfft(x)
        spec[freqs > cutoff] = 0
        lowpass = np.fft.irfft(spec, n)
        metrics = compute_metrics(lowpass / np.max(np.abs(lowpass)), sr, _Probe())
        estimates.append(metrics["estimated_high_frequency_cutoff_hz"]["value"])
    assert estimates[0] < estimates[1] < estimates[2] < estimates[3]  # monotonic
    # Estimator tracks the ladder within a generous band; it is not exact.
    assert abs(estimates[0] - cutoffs[0]) < 3000


# ---------------------------------------------------------------------------
# FFmpeg oracle (G4/G5 reference comparison, offline, version recorded)
# ---------------------------------------------------------------------------

def _ffmpeg_available() -> bool:
    from moodify.auditory.decode import _which_ffmpeg, _which_ffprobe

    try:
        _which_ffmpeg()
        _which_ffprobe()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _ffmpeg_available(), reason="ffmpeg not available")
def test_loudness_oracle_vs_ffmpeg_ebur128(tmp_path):
    """integrated loudness within tolerance of ffmpeg ebur128 (G4)."""
    import subprocess
    import wave

    sr = 48000
    x = _sine(4.0, 0.5, 440.0, sr)
    wav_path = tmp_path / "oracle.wav"
    with wave.open(str(wav_path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sr)
        frames = np.clip(x, -1.0, 1.0)
        wav.writeframes((frames * 32767).astype(np.int16).tobytes())

    result = subprocess.run(
        ["ffmpeg", "-nostats", "-i", str(wav_path), "-af", "ebur128", "-f", "null", "-"],
        capture_output=True, text=True, timeout=60,
    )
    assert "I:" in result.stderr
    import re

    # ffmpeg ebur128 prints per-frame lines starting at I: -70.0; the
    # final summary line is anchored at line start. Match only the summary.
    match = re.search(r"^\s+I:\s*(-?\d+\.\d+)\s+LUFS", result.stderr, re.MULTILINE)
    assert match
    ffmpeg_lufs = float(match.group(1))
    ours = integrated_loudness_lufs(x, sr)
    assert abs(ours - ffmpeg_lufs) < 1.0  # documented tolerance
