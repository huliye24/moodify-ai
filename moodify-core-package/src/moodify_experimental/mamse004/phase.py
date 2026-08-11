"""Mono phase geometry: unwrap -> group delay -> phase curvature.

Group delay uses a rad/s frequency axis and outputs seconds. Low-magnitude
bins are masked, never fabricated as zero. A nonzero group delay is never
treated as a defect by itself.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import stft

from .config import PhaseGeometryConfig

EPS = 1e-12


def unwrap_phase(phase_rad: np.ndarray, axis: int = -1) -> np.ndarray:
    return np.unwrap(np.asarray(phase_rad, dtype=np.float64), axis=axis)


def group_delay_from_phase(phase_rad: np.ndarray, omega_rad_s: np.ndarray, axis: int = -1) -> np.ndarray:
    """Group delay in seconds: -d(phase)/d(omega) on a rad/s axis."""
    p = unwrap_phase(phase_rad, axis=axis)
    w = np.asarray(omega_rad_s, dtype=np.float64)
    if w.ndim != 1 or w.size < 2:
        raise ValueError("omega_rad_s must be 1D with >= 2 points")
    return -np.gradient(p, w, axis=axis, edge_order=1)


def phase_curvature_from_group_delay(group_delay_s: np.ndarray, omega_rad_s: np.ndarray, axis: int = -1) -> np.ndarray:
    """d2phi/domega2 = -d(tau_g)/domega, unit s2."""
    return -np.gradient(np.asarray(group_delay_s, dtype=np.float64), np.asarray(omega_rad_s, dtype=np.float64),
                        axis=axis, edge_order=1)


def magnitude_mask(magnitude: np.ndarray, floor_db: float = -45.0, axis: int = -1) -> np.ndarray:
    """Relative-magnitude reliability mask (per frame). Bins below floor -> False.

    Frames with no measurable energy (peak <= EPS) are masked entirely:
    digital silence carries no phase information, and a flat 0 dB relative
    ratio must not be treated as valid.
    """
    mag = np.asarray(magnitude, dtype=np.float64)
    peak = np.max(mag, axis=axis, keepdims=True)
    rel_db = 20.0 * np.log10((mag + EPS) / (peak + EPS))
    return (rel_db >= floor_db) & (peak > EPS)


def _summary(values: np.ndarray, mask: np.ndarray) -> dict:
    v = np.asarray(values, dtype=np.float64)
    m = np.asarray(mask, dtype=bool) & np.isfinite(v)
    valid = v[m]
    ratio = float(m.mean()) if m.size else 0.0
    if valid.size == 0:
        return {"valid_ratio": ratio, "median": None, "mad": None, "p95_abs": None}
    med = float(np.median(valid))
    mad = float(np.median(np.abs(valid - med)))
    p95 = float(np.percentile(np.abs(valid - med), 95))
    return {"valid_ratio": ratio, "median": med, "mad": mad, "p95_abs": p95}


def complex_stft(x: np.ndarray, sr: int, cfg: PhaseGeometryConfig):
    x = np.asarray(x, dtype=np.float64)
    f, t, z = stft(x, fs=sr, window=cfg.window, nperseg=cfg.n_fft,
                   noverlap=cfg.n_fft - cfg.hop_length, nfft=cfg.n_fft,
                   boundary=None, padded=False)
    return f, t, z.T  # [time, freq]


def _unavailable_summary(reason: str) -> dict:
    return {
        "status": "UNAVAILABLE",
        "reason": reason,
        "valid_bin_ratio": 0.0,
        "group_delay_median_ms": None,
        "group_delay_mad_ms": None,
        "group_delay_p95_abs_ms": None,
        "phase_curvature_median_s2": None,
        "phase_curvature_mad_s2": None,
    }


def analyze_mono_phase(x: np.ndarray, sr: int, cfg: PhaseGeometryConfig) -> dict:
    x = np.asarray(x, dtype=np.float64)
    if len(x) < cfg.n_fft:
        return {
            "frequency_hz": np.array([], dtype=np.float64),
            "frame_time_s": np.array([], dtype=np.float64),
            "magnitude": np.empty((0, 0)),
            "valid_mask": np.empty((0, 0), dtype=bool),
            "group_delay_s": np.empty((0, 0)),
            "phase_curvature_s2": np.empty((0, 0)),
            "summary": _unavailable_summary(f"signal shorter than n_fft ({len(x)} < {cfg.n_fft})"),
        }
    f, t, z = complex_stft(x, sr, cfg)
    band = (f >= cfg.f_min_hz) & (f <= min(cfg.f_max_hz, sr / 2))
    f2 = f[band]
    z2 = z[:, band]
    omega = 2.0 * np.pi * f2
    mag = np.abs(z2)
    mask = magnitude_mask(mag, cfg.magnitude_floor_db, axis=1)
    phase = np.angle(z2)
    gd = group_delay_from_phase(phase, omega, axis=1)
    curv = phase_curvature_from_group_delay(gd, omega, axis=1)
    sgd = _summary(gd, mask)
    sc = _summary(curv, mask)
    return {
        "frequency_hz": f2,
        "frame_time_s": t,
        "magnitude": mag,
        "valid_mask": mask,
        "group_delay_s": gd,
        "phase_curvature_s2": curv,
        "summary": {
            "valid_bin_ratio": sgd["valid_ratio"],
            "group_delay_median_ms": None if sgd["median"] is None else sgd["median"] * 1000.0,
            "group_delay_mad_ms": None if sgd["mad"] is None else sgd["mad"] * 1000.0,
            "group_delay_p95_abs_ms": None if sgd["p95_abs"] is None else sgd["p95_abs"] * 1000.0,
            "phase_curvature_median_s2": sc["median"],
            "phase_curvature_mad_s2": sc["mad"],
        },
    }


def group_delay_from_response(h: np.ndarray, sr: int, n_fft: int = 16384):
    """Synthetic helper: group delay of a real impulse response (transfer function)."""
    H = np.fft.rfft(np.asarray(h, dtype=np.float64), n=n_fft)
    f = np.fft.rfftfreq(n_fft, 1.0 / sr)
    omega = 2 * np.pi * f
    gd = group_delay_from_phase(np.angle(H), omega, axis=0)
    return f, H, gd
