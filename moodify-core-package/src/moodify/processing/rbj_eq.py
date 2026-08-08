"""
rbj_eq.py — RBJ Biquad Equalizer (AEP-ACU-002)
================================================

Production-grade RBJ biquad EQ implementing the Robert Bristow-Johnson
Audio EQ Cookbook formulae. Replaces the legacy FFT sigmoid/Gaussian EQ.

Filter types: low_shelf, high_shelf, peaking, high_pass, low_pass.

All coefficient functions are pure — they compute (b, a) tuples.
All processing functions use scipy.signal.lfilter for vectorised execution.

Reference: https://webaudio.github.io/Audio-EQ-Cookbook/audio-eq-cookbook.html
"""

from __future__ import annotations

import math
from typing import List, Tuple

import numpy as np
from scipy.signal import lfilter

# ── Type aliases ──────────────────────────────────────────────────
Coeffs = Tuple[np.ndarray, np.ndarray]  # (b, a) each shape (3,)

# ── Coefficient functions ─────────────────────────────────────────


def _prewarp(freq_hz: float, sr: float) -> Tuple[float, float, float]:
    """Compute pre-warped constants for a given frequency."""
    w0 = 2.0 * math.pi * freq_hz / sr
    return w0, math.cos(w0), math.sin(w0)


def rbj_low_shelf_coeffs(
    freq_hz: float, q: float, gain_db: float, sr: float,
) -> Coeffs:
    """RBJ low-shelf biquad coefficients. Q controls steepness."""
    w0, cos_w0, sin_w0 = _prewarp(freq_hz, sr)
    A = 10.0 ** (gain_db / 40.0)
    alpha = sin_w0 / (2.0 * max(q, 0.025))

    b0 = A * ((A + 1.0) - (A - 1.0) * cos_w0 + 2.0 * math.sqrt(A) * alpha)
    b1 = 2.0 * A * ((A - 1.0) - (A + 1.0) * cos_w0)
    b2 = A * ((A + 1.0) - (A - 1.0) * cos_w0 - 2.0 * math.sqrt(A) * alpha)
    a0 = (A + 1.0) + (A - 1.0) * cos_w0 + 2.0 * math.sqrt(A) * alpha
    a1 = -2.0 * ((A - 1.0) + (A + 1.0) * cos_w0)
    a2 = (A + 1.0) + (A - 1.0) * cos_w0 - 2.0 * math.sqrt(A) * alpha

    return _normalise(b0, b1, b2, a0, a1, a2)


def rbj_high_shelf_coeffs(
    freq_hz: float, q: float, gain_db: float, sr: float,
) -> Coeffs:
    """RBJ high-shelf biquad coefficients. Q controls steepness."""
    w0, cos_w0, sin_w0 = _prewarp(freq_hz, sr)
    A = 10.0 ** (gain_db / 40.0)
    alpha = sin_w0 / (2.0 * max(q, 0.025))

    b0 = A * ((A + 1.0) + (A - 1.0) * cos_w0 + 2.0 * math.sqrt(A) * alpha)
    b1 = -2.0 * A * ((A - 1.0) + (A + 1.0) * cos_w0)
    b2 = A * ((A + 1.0) + (A - 1.0) * cos_w0 - 2.0 * math.sqrt(A) * alpha)
    a0 = (A + 1.0) - (A - 1.0) * cos_w0 + 2.0 * math.sqrt(A) * alpha
    a1 = 2.0 * ((A - 1.0) - (A + 1.0) * cos_w0)
    a2 = (A + 1.0) - (A - 1.0) * cos_w0 - 2.0 * math.sqrt(A) * alpha

    return _normalise(b0, b1, b2, a0, a1, a2)


def rbj_peaking_coeffs(
    freq_hz: float, q: float, gain_db: float, sr: float,
) -> Coeffs:
    """RBJ peaking (bell) biquad coefficients. Q = fc / bandwidth."""
    w0, cos_w0, sin_w0 = _prewarp(freq_hz, sr)
    A = 10.0 ** (gain_db / 40.0)
    alpha = sin_w0 / (2.0 * max(q, 0.025))

    b0 = 1.0 + alpha * A
    b1 = -2.0 * cos_w0
    b2 = 1.0 - alpha * A
    a0 = 1.0 + alpha / A
    a1 = -2.0 * cos_w0
    a2 = 1.0 - alpha / A

    return _normalise(b0, b1, b2, a0, a1, a2)


def rbj_highpass_coeffs(freq_hz: float, q: float, sr: float) -> Coeffs:
    """RBJ high-pass biquad coefficients."""
    w0, cos_w0, sin_w0 = _prewarp(freq_hz, sr)
    alpha = sin_w0 / (2.0 * max(q, 0.025))

    b0 = (1.0 + cos_w0) / 2.0
    b1 = -(1.0 + cos_w0)
    b2 = (1.0 + cos_w0) / 2.0
    a0 = 1.0 + alpha
    a1 = -2.0 * cos_w0
    a2 = 1.0 - alpha

    return _normalise(b0, b1, b2, a0, a1, a2)


def rbj_lowpass_coeffs(freq_hz: float, q: float, sr: float) -> Coeffs:
    """RBJ low-pass biquad coefficients."""
    w0, cos_w0, sin_w0 = _prewarp(freq_hz, sr)
    alpha = sin_w0 / (2.0 * max(q, 0.025))

    b0 = (1.0 - cos_w0) / 2.0
    b1 = 1.0 - cos_w0
    b2 = (1.0 - cos_w0) / 2.0
    a0 = 1.0 + alpha
    a1 = -2.0 * cos_w0
    a2 = 1.0 - alpha

    return _normalise(b0, b1, b2, a0, a1, a2)


def _normalise(b0, b1, b2, a0, a1, a2) -> Coeffs:
    """Normalise by a0, return (b, a) as ndarrays."""
    inv_a0 = 1.0 / a0
    b = np.array([b0 * inv_a0, b1 * inv_a0, b2 * inv_a0], dtype=np.float64)
    a = np.array([1.0, a1 * inv_a0, a2 * inv_a0], dtype=np.float64)
    return b, a


# ── Coefficient dispatch ──────────────────────────────────────────

COEFF_FUNCTIONS = {
    "low_shelf": rbj_low_shelf_coeffs,
    "high_shelf": rbj_high_shelf_coeffs,
    "peaking": rbj_peaking_coeffs,
    "high_pass": rbj_highpass_coeffs,
    "low_pass": rbj_lowpass_coeffs,
}

# ── Frequency response ────────────────────────────────────────────


def compute_freq_response(
    coeffs: Coeffs, n_fft: int = 4096, sr: float = 44100.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute magnitude frequency response (dB) from biquad coefficients.

    Returns (freqs_hz, magnitude_db).
    """
    from scipy.signal import freqz

    b, a = coeffs
    w, h = freqz(b, a, worN=n_fft, fs=sr)
    mag_db = 20.0 * np.log10(np.abs(h) + 1e-15)
    return w, mag_db


def cascade_freq_response(
    coeffs_list: List[Coeffs], n_fft: int = 4096, sr: float = 44100.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute magnitude response of cascaded biquad filters."""
    from scipy.signal import freqz

    w = None
    h_total = None
    for b, a in coeffs_list:
        w, h = freqz(b, a, worN=n_fft, fs=sr)
        if h_total is None:
            h_total = np.abs(h)
        else:
            h_total *= np.abs(h)
    mag_db = 20.0 * np.log10(h_total + 1e-15)
    return w, mag_db


# ── Processing functions ──────────────────────────────────────────


def apply_biquad(audio: np.ndarray, b: np.ndarray, a: np.ndarray) -> np.ndarray:
    """Apply a single biquad filter to audio using scipy lfilter (vectorised)."""
    if audio.ndim == 1:
        return lfilter(b, a, audio)
    elif audio.ndim == 2:
        result = np.zeros_like(audio)
        for ch in range(audio.shape[1]):
            result[:, ch] = lfilter(b, a, audio[:, ch])
        return result
    else:
        raise ValueError(f"Audio must be 1D (mono) or 2D (stereo), got shape {audio.shape}")


def apply_rbj_eq(
    audio: np.ndarray,
    sr: float,
    filters: List[dict],
) -> np.ndarray:
    """Apply a chain of RBJ biquad filters to audio.

    Parameters
    ----------
    audio : np.ndarray, shape (n,) or (n, 2)
    sr : float, sample rate in Hz
    filters : list of dict, each with keys:
        - "type": "low_shelf" | "high_shelf" | "peaking" | "high_pass" | "low_pass"
        - "freq_hz": float
        - "gain_db": float (for shelf/peaking, default 0)
        - "q": float (default 0.707 for shelf, 1.0 for peaking)

    Returns
    -------
    processed : np.ndarray, same shape as input
    """
    if not filters:
        return audio.copy()

    result = audio.copy()
    for fspec in filters:
        ftype = fspec.get("type", "peaking")
        if ftype not in COEFF_FUNCTIONS:
            raise ValueError(
                f"Unknown filter type '{ftype}'. "
                f"Must be one of: {list(COEFF_FUNCTIONS.keys())}"
            )

        freq_hz = float(fspec.get("freq_hz", 1000.0))
        gain_db = float(fspec.get("gain_db", 0.0))
        q = float(fspec.get("q", 1.0 if ftype == "peaking" else 0.707))

        # Clamp safety
        freq_hz = max(1.0, min(freq_hz, sr / 2.0 - 1.0))
        q = max(0.025, min(q, 40.0))
        gain_db = max(-48.0, min(gain_db, 48.0))

        coeff_fn = COEFF_FUNCTIONS[ftype]
        if ftype in ("high_pass", "low_pass"):
            b, a = coeff_fn(freq_hz, q, sr)
        else:
            b, a = coeff_fn(freq_hz, q, gain_db, sr)

        # Check for NaN / inf in coefficients
        if np.any(~np.isfinite(b)) or np.any(~np.isfinite(a)):
            raise ValueError(
                f"Non-finite biquad coefficients for filter: {fspec}. "
                f"b={b}, a={a}"
            )

        result = apply_biquad(result, b, a)

    # Safety clip
    result = np.clip(result, -1.0, 1.0)

    return result


# ── Public API ────────────────────────────────────────────────────

__all__ = [
    "rbj_low_shelf_coeffs",
    "rbj_high_shelf_coeffs",
    "rbj_peaking_coeffs",
    "rbj_highpass_coeffs",
    "rbj_lowpass_coeffs",
    "COEFF_FUNCTIONS",
    "compute_freq_response",
    "cascade_freq_response",
    "apply_biquad",
    "apply_rbj_eq",
]
