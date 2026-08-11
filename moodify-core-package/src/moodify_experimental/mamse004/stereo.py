"""Stereo phase geometry: cross-spectrum IPD -> interchannel delay + GCC-PHAT.

Cross-spectrum convention is fixed to C = R * conj(L); positive interchannel
delay means the right channel arrives later than the left. GCC-PHAT is an
independent estimate; disagreement is reported, never silently resolved.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import stft

from .config import PhaseGeometryConfig
from .phase import EPS, group_delay_from_phase, magnitude_mask


def gcc_phat_delay(left: np.ndarray, right: np.ndarray, sr: int, max_delay_ms: float = 5.0) -> float:
    """GCC-PHAT delay estimate in seconds. Positive => right is later than left."""
    left = np.asarray(left, dtype=np.float64)
    right = np.asarray(right, dtype=np.float64)
    n = 1
    target = len(left) + len(right)
    while n < target:
        n *= 2
    L = np.fft.rfft(left, n=n)
    R = np.fft.rfft(right, n=n)
    cross = R * np.conj(L)
    phat = cross / (np.abs(cross) + EPS)
    corr = np.fft.irfft(phat, n=n)
    max_samp = min(int(round(max_delay_ms * 1e-3 * sr)), n // 2 - 1)
    if max_samp <= 0:
        return 0.0
    window = np.concatenate([corr[-max_samp:], corr[:max_samp + 1]])
    lags = np.arange(-max_samp, max_samp + 1)
    lag = int(lags[int(np.argmax(np.abs(window)))])
    return lag / sr


def analyze_stereo_phase(left: np.ndarray, right: np.ndarray, sr: int, cfg: PhaseGeometryConfig) -> dict:
    left = np.asarray(left, dtype=np.float64)
    right = np.asarray(right, dtype=np.float64)
    if min(len(left), len(right)) < cfg.n_fft:
        return {
            "frequency_hz": np.array([], dtype=np.float64),
            "frame_time_s": np.array([], dtype=np.float64),
            "ipd_rad": np.empty((0, 0)),
            "interchannel_delay_s": np.empty((0, 0)),
            "valid_mask": np.empty((0, 0), dtype=bool),
            "summary": {
                "ipd_available": False,
                "reason": f"signal shorter than n_fft ({min(len(left), len(right))} < {cfg.n_fft})",
                "valid_bin_ratio": 0.0,
                "interchannel_delay_median_ms": None,
                "interchannel_delay_mad_ms": None,
                "gcc_phat_delay_ms": None,
                "cross_method_disagreement_ms": None,
            },
        }
    f, t, L = stft(left, fs=sr, window=cfg.window, nperseg=cfg.n_fft,
                   noverlap=cfg.n_fft - cfg.hop_length, nfft=cfg.n_fft,
                   boundary=None, padded=False)
    _, _, R = stft(right, fs=sr, window=cfg.window, nperseg=cfg.n_fft,
                   noverlap=cfg.n_fft - cfg.hop_length, nfft=cfg.n_fft,
                   boundary=None, padded=False)
    L = L.T
    R = R.T
    band = (f >= cfg.f_min_hz) & (f <= min(cfg.f_max_hz, sr / 2))
    f2 = f[band]
    L = L[:, band]
    R = R[:, band]
    cross = R * np.conj(L)
    ipd = np.angle(cross)
    omega = 2 * np.pi * f2
    delay = group_delay_from_phase(ipd, omega, axis=1)
    cross_mag = np.sqrt(np.abs(L) * np.abs(R))
    mask = magnitude_mask(cross_mag, cfg.magnitude_floor_db, axis=1)
    valid = delay[mask & np.isfinite(delay)]
    if valid.size:
        med = float(np.median(valid))
        mad = float(np.median(np.abs(valid - med)))
    else:
        med = mad = None
    gcc = gcc_phat_delay(left, right, sr, cfg.gcc_max_delay_ms)
    disagreement = None if med is None else abs(med - gcc)
    return {
        "frequency_hz": f2,
        "frame_time_s": t,
        "ipd_rad": ipd,
        "interchannel_delay_s": delay,
        "valid_mask": mask,
        "summary": {
            "ipd_available": True,
            "valid_bin_ratio": float(mask.mean()) if mask.size else 0.0,
            "interchannel_delay_median_ms": None if med is None else med * 1000.0,
            "interchannel_delay_mad_ms": None if mad is None else mad * 1000.0,
            "gcc_phat_delay_ms": gcc * 1000.0,
            "cross_method_disagreement_ms": None if disagreement is None else disagreement * 1000.0,
        },
    }
