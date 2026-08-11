"""1D temporal + 2D spectro-temporal modulation analysis.

Temporal rates are Hz (from the frame-rate axis); spectral rates are
cycles/octave (from bands_per_octave). Marginals are non-negative and
normalized; the ridge is always a CANDIDATE, never an authority.
"""

from __future__ import annotations

import numpy as np


def _segment_starts(n_frames: int, win: int, hop: int) -> list[int]:
    if n_frames <= win:
        return [0]
    starts = list(range(0, n_frames - win + 1, hop))
    if starts[-1] != n_frames - win:
        starts.append(n_frames - win)
    return starts


def analyze_surface(
    surface_db: np.ndarray,
    frame_rate_hz: float,
    bands_per_octave: float,
    modulation_window_seconds: float,
    modulation_hop_seconds: float,
):
    m = np.asarray(surface_db, dtype=np.float64)
    if m.ndim != 2 or min(m.shape) < 2:
        raise ValueError("surface_db must be [log_freq, time]")
    n_f, n_t = m.shape
    win_t = min(n_t, max(8, int(round(modulation_window_seconds * frame_rate_hz))))
    hop_t = max(1, int(round(modulation_hop_seconds * frame_rate_hz)))
    starts = _segment_starts(n_t, win_t, hop_t)

    global_centered = m - float(np.mean(m))
    dynamic = m - np.mean(m, axis=1, keepdims=True)
    wf = np.hanning(n_f)[:, None]
    wt = np.hanning(win_t)[None, :]
    window2 = wf * wt

    joint = np.zeros((n_f, win_t), dtype=np.float64)
    dyn_joint = np.zeros_like(joint)
    for s in starts:
        a = global_centered[:, s:s + win_t]
        d = dynamic[:, s:s + win_t]
        if a.shape[1] < win_t:
            pad = win_t - a.shape[1]
            a = np.pad(a, ((0, 0), (0, pad)))
            d = np.pad(d, ((0, 0), (0, pad)))
        joint += np.abs(np.fft.fftshift(np.fft.fft2(a * window2))) ** 2
        dyn_joint += np.abs(np.fft.fftshift(np.fft.fft2(d * window2))) ** 2
    joint /= len(starts)
    dyn_joint /= len(starts)

    temporal_rates = np.fft.fftshift(np.fft.fftfreq(win_t, d=1.0 / frame_rate_hz))
    spectral_rates = np.fft.fftshift(np.fft.fftfreq(n_f, d=1.0 / bands_per_octave))

    temporal_marginal = dyn_joint.sum(axis=0)
    spectral_marginal = joint.sum(axis=1)
    return {
        "joint_power": joint,
        "dynamic_joint_power": dyn_joint,
        "temporal_rates_hz": temporal_rates,
        "spectral_rates_cpo": spectral_rates,
        "temporal_marginal": temporal_marginal,
        "spectral_marginal": spectral_marginal,
        "segment_count": len(starts),
        "modulation_window_frames": win_t,
    }


def normalize_distribution(x: np.ndarray) -> np.ndarray:
    x = np.maximum(np.asarray(x, dtype=np.float64), 0.0)
    total = float(np.sum(x))
    return x / total if total > 0 else np.zeros_like(x)


def normalized_entropy(x: np.ndarray) -> float:
    p = normalize_distribution(x)
    nz = p[p > 0]
    if nz.size <= 1:
        return 0.0
    h = -float(np.sum(nz * np.log(nz)))
    return h / np.log(p.size)
