"""Analytic Morlet-like wavelet bank in the FFT domain.

Self-contained research implementation; not numerically equivalent to
Kymatio/Mallat scattering wavelets.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import resample_poly


def resample_deterministic(x: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    from math import gcd

    x = np.asarray(x, dtype=np.float64)
    if orig_sr == target_sr:
        return x.copy()
    g = gcd(int(orig_sr), int(target_sr))
    return resample_poly(x, target_sr // g, orig_sr // g).astype(np.float64)


def _analytic_gaussian_response(n: int, sr: int, center_hz: float, q: float) -> np.ndarray:
    freqs = np.fft.fftfreq(n, 1.0 / sr)
    sigma = max(center_hz / q, sr / n)
    response = np.exp(-0.5 * ((freqs - center_hz) / sigma) ** 2)
    response[freqs <= 0] = 0.0
    norm = np.sqrt(np.sum(np.abs(response) ** 2))
    if norm > 0:
        response = response / norm * np.sqrt(n)
    return response.astype(np.complex128)


def analytic_wavelet_bank(x: np.ndarray, sr: int, centers_hz: tuple[float, ...], q: float) -> np.ndarray:
    """Return complex carrier responses with shape (bands, samples)."""
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    X = np.fft.fft(x)
    out = np.empty((len(centers_hz), n), dtype=np.complex128)
    for i, fc in enumerate(centers_hz):
        H = _analytic_gaussian_response(n, sr, float(fc), q)
        out[i] = np.fft.ifft(X * H)
    return out


def modulation_wavelet_bank(x: np.ndarray, sr: int, rates_hz: tuple[float, ...], q: float) -> np.ndarray:
    """Analytic low-frequency modulation responses, shape (rates, samples)."""
    return analytic_wavelet_bank(x, sr, rates_hz, q)
