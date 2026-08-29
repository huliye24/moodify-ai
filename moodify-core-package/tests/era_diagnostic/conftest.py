"""Deterministic synthetic fixtures for Era Diagnostic tests (MFY-CR-P03).

All assets are generated at test time from numpy/scipy — nothing copyrighted,
nothing committed as binary.
"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest
import scipy.signal as sig

SR = 48000
DURATION_S = 8.0
RNG_SEED = 20260817

_TONE_FREQS = (220.0, 440.0, 880.0, 1760.0, 3520.0, 7040.0, 10000.0, 12000.0, 14080.0, 17500.0, 19000.0)
_TONE_AMPS = (0.15, 0.15, 0.15, 0.15, 0.15, 0.10, 0.10, 0.10, 0.05, 0.03, 0.02)
# silence gaps (start / middle / end) so quiet windows exist for noise-floor checks
_SILENCE = ((0.0, 1.2), (4.5, 5.7), (7.0, 8.0))


def make_probe(sr: int = SR, duration: float = DURATION_S) -> SimpleNamespace:
    return SimpleNamespace(duration_seconds=duration, sha256="synthetic-fixture",
                           sample_rate=sr, format="wav", channels=2)


def _tone_signal(sr: int, n: int, rng: np.random.Generator) -> np.ndarray:
    t = np.arange(n) / sr
    x = np.zeros(n, dtype=np.float64)
    for f, a in zip(_TONE_FREQS, _TONE_AMPS):
        x += a * np.sin(2 * np.pi * f * t)
    # musical noise bed at -40 dBFS full-band (broadband reference)
    x += 0.01 * rng.standard_normal(n)
    return x


def _apply_silence(x: np.ndarray, sr: int, rng: np.random.Generator) -> np.ndarray:
    x = x.copy()
    for start, end in _SILENCE:
        lo, hi = int(start * sr), int(end * sr)
        x[lo:hi] = 0.0
    return x


def clean_stereo(sr: int = SR, duration: float = DURATION_S) -> np.ndarray:
    """Full-band, quiet-noise-floor stereo reference with silence gaps.

    Right channel is same-phase with a gain offset plus mild decorrelation
    noise in the music region ONLY (silence stays silent). Expected stereo
    correlation ~0.97 — correlated, not mono, not defective.
    """
    rng = np.random.default_rng(RNG_SEED)
    n = int(sr * duration)
    left = _apply_silence(_tone_signal(sr, n, rng), sr, rng)
    right = 0.95 * left
    music_mask = np.ones(n, dtype=bool)
    for start, end in _SILENCE:
        lo, hi = int(start * sr), int(end * sr)
        music_mask[lo:hi] = False
    right[music_mask] += 0.06 * rng.standard_normal(int(music_mask.sum()))
    return np.stack([left, right], axis=1)


def lowpass(x: np.ndarray, cutoff_hz: float, sr: int = SR) -> np.ndarray:
    sos = sig.butter(4, cutoff_hz / (sr / 2), btype="low", output="sos")
    y = np.zeros_like(x)
    for ch in range(x.shape[1]):
        y[:, ch] = sig.sosfiltfilt(sos, x[:, ch])
    return y


def add_noise(x: np.ndarray, dbfs: float, rng: np.random.Generator, everywhere: bool = False) -> np.ndarray:
    """Add white noise at ``dbfs`` relative to full scale.

    ``everywhere=False`` keeps the silence gaps silent (hiss present only with
    music); ``everywhere=True`` models hiss that is audible in quiet too.
    """
    amp = 10 ** (dbfs / 20)
    y = x.copy()
    if everywhere:
        y = y + amp * rng.standard_normal(y.shape)
    else:
        music_mask = np.ones(y.shape[0], dtype=bool)
        for start, end in _SILENCE:
            lo, hi = int(start * SR), int(end * SR)
            music_mask[lo:hi] = False
        noise = amp * rng.standard_normal(y.shape)
        y[music_mask] = y[music_mask] + noise[music_mask]
    return y


def clipped(x: np.ndarray, threshold: float = 0.999) -> np.ndarray:
    y = x * 50.0
    return np.clip(y, -threshold, threshold)


def to_mono(x: np.ndarray) -> np.ndarray:
    m = x.mean(axis=1, keepdims=True)
    return np.repeat(m, 2, axis=1)


def width_scaled(x: np.ndarray, k: float) -> np.ndarray:
    mid = (x[:, 0] + x[:, 1]) / 2.0
    side = (x[:, 0] - x[:, 1]) / 2.0 * k
    return np.stack([mid + side, mid - side], axis=1)


def phase_flipped(x: np.ndarray, start_s: float, end_s: float, sr: int = SR) -> np.ndarray:
    y = x.copy()
    lo, hi = int(start_s * sr), int(end_s * sr)
    y[lo:hi, 1] = -y[lo:hi, 1]
    return y


def dark_but_clean(sr: int = SR, duration: float = DURATION_S) -> np.ndarray:
    """Arrangement-limited dark mix: low/mid content only, no presence energy."""
    rng = np.random.default_rng(RNG_SEED + 1)
    n = int(sr * duration)
    t = np.arange(n) / sr
    x = 0.2 * np.sin(2 * np.pi * 220 * t) + 0.15 * np.sin(2 * np.pi * 440 * t)
    x = _apply_silence(x, sr, rng)
    x = np.stack([x, x], axis=1)
    return lowpass(x, 9000.0, sr)


def metricize(samples: np.ndarray, sr: int = SR) -> dict:
    """Turn synthetic audio into the standard metric record the engine consumes."""
    from moodify.auditory.metrics import compute_metrics
    from moodify.auditory.stereo import compute_stereo_metrics

    metrics = compute_metrics(samples, sr, make_probe(sr))
    metrics.update(compute_stereo_metrics(samples))
    channels = samples.shape[1] if samples.ndim > 1 else 1
    metrics["sample_rate"] = {"value": sr, "unit": "Hz", "method": "ffprobe",
                              "status": "VALID", "warnings": []}
    metrics["channels"] = {"value": channels, "unit": "ch", "method": "ffprobe",
                           "status": "VALID", "warnings": []}
    return metrics


@pytest.fixture
def clean() -> np.ndarray:
    return clean_stereo()


@pytest.fixture
def clean_metrics(clean) -> dict:
    return metricize(clean)
