"""Synthetic fixtures for Identity Guard tests (MFY-CR-P05).

Deterministic, generated at test time (numpy/scipy). No copyrighted material,
no binaries in git.
"""

from __future__ import annotations

import numpy as np
import pytest
import scipy.signal as sig

SR = 48000
DURATION_S = 8.0
RNG_SEED = 20260817

_SILENCE = ((0.0, 1.2), (4.5, 5.7), (7.0, 8.0))
_TONES = (60.0, 100.0, 220.0, 440.0, 880.0, 1760.0, 3520.0, 7040.0,
          10000.0, 12000.0, 14080.0, 17500.0, 19000.0)
_AMPS = (0.12, 0.10, 0.15, 0.15, 0.15, 0.15, 0.15, 0.10,
         0.10, 0.10, 0.05, 0.03, 0.02)


def clean_stereo(sr: int = SR, duration: float = DURATION_S) -> np.ndarray:
    rng = np.random.default_rng(RNG_SEED)
    n = int(sr * duration)
    t = np.arange(n) / sr
    x = sum(a * np.sin(2 * np.pi * f * t) for f, a in zip(_TONES, _AMPS))
    x += 0.01 * rng.standard_normal(n)
    for start, end in _SILENCE:
        lo, hi = int(start * sr), int(end * sr)
        x[lo:hi] = 0.0
    left = x
    right = 0.95 * left
    music_mask = np.ones(n, dtype=bool)
    for start, end in _SILENCE:
        lo, hi = int(start * sr), int(end * sr)
        music_mask[lo:hi] = False
    right[music_mask] += 0.06 * rng.standard_normal(int(music_mask.sum()))
    return np.stack([left, right], axis=1)


def metricize(samples: np.ndarray, sr: int = SR) -> dict:
    from types import SimpleNamespace

    from moodify.auditory.metrics import compute_metrics
    from moodify.auditory.stereo import compute_stereo_metrics

    probe = SimpleNamespace(duration_seconds=DURATION_S, sha256="synthetic-fixture",
                            sample_rate=sr, format="wav", channels=2)
    metrics = compute_metrics(samples, sr, probe)
    metrics.update(compute_stereo_metrics(samples))
    metrics["sample_rate"] = {"value": sr, "unit": "Hz", "method": "ffprobe",
                              "status": "VALID", "warnings": []}
    return metrics


def _high_shelf(x: np.ndarray, cutoff_hz: float, gain: float, sr: int = SR) -> np.ndarray:
    """First-order high shelf boost: y = x + gain * highpassed(x)."""
    sos = sig.butter(2, cutoff_hz / (sr / 2), btype="high", output="sos")
    y = np.zeros_like(x)
    for ch in range(x.shape[1]):
        y[:, ch] = x[:, ch] + gain * sig.sosfiltfilt(sos, x[:, ch])
    return y


def _low_shelf(x: np.ndarray, cutoff_hz: float, gain: float, sr: int = SR) -> np.ndarray:
    sos = sig.butter(2, cutoff_hz / (sr / 2), btype="low", output="sos")
    y = np.zeros_like(x)
    for ch in range(x.shape[1]):
        y[:, ch] = x[:, ch] + gain * sig.sosfiltfilt(sos, x[:, ch])
    return y


def over_bright() -> np.ndarray:
    # strong bright tilt but below clipping threshold
    return _high_shelf(clean_stereo(), 3000.0, 0.45)


def over_bass() -> np.ndarray:
    return _low_shelf(clean_stereo(), 150.0, 0.9)


def over_compressed() -> np.ndarray:
    y = 1.4 * np.tanh(2.5 * clean_stereo())
    return y


def over_wide() -> np.ndarray:
    x = clean_stereo()
    mid = (x[:, 0] + x[:, 1]) / 2.0
    side = (x[:, 0] - x[:, 1]) / 2.0 * 2.5
    return np.stack([mid + side, mid - side], axis=1)


def over_loud() -> np.ndarray:
    y = 2.0 * np.tanh(clean_stereo())
    return y


def minimal_candidate() -> np.ndarray:
    return 1.06 * clean_stereo()  # +0.5 dB


def balanced_candidate() -> np.ndarray:
    y = 1.12 * clean_stereo()  # +1 dB, within budgets
    return _high_shelf(y, 8000.0, 0.06)


def source_metrics() -> dict:
    return metricize(clean_stereo())


@pytest.fixture
def src_metrics() -> dict:
    return source_metrics()


@pytest.fixture
def cand_metrics():
    return {
        "over_bright": metricize(over_bright()),
        "over_bass": metricize(over_bass()),
        "over_compressed": metricize(over_compressed()),
        "over_wide": metricize(over_wide()),
        "over_loud": metricize(over_loud()),
        "minimal": metricize(minimal_candidate()),
        "balanced": metricize(balanced_candidate()),
    }
