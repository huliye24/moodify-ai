"""Scattering-inspired cascade: carrier modulus (U1) -> frames -> envelope
decimation -> modulation bank (second-order-inspired summary)."""

from __future__ import annotations

from math import gcd

import numpy as np
from scipy.signal import resample_poly

from .config import TextureConfig
from .wavelets import analytic_wavelet_bank, modulation_wavelet_bank


def _frame_reduce(values: np.ndarray, sr: int, frame_ms: int, hop_ms: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Mean-reduce rows (features, samples) into frames."""
    frame = max(1, int(round(frame_ms * sr / 1000)))
    hop = max(1, int(round(hop_ms * sr / 1000)))
    n = values.shape[1]
    if n < frame:
        starts = np.array([0], dtype=np.int64)
        ends = np.array([n], dtype=np.int64)
        return values.mean(axis=1, keepdims=True).T, starts, ends
    count = (n - frame) // hop + 1
    out = np.empty((count, values.shape[0]), dtype=np.float64)
    starts = np.empty(count, dtype=np.int64)
    ends = np.empty(count, dtype=np.int64)
    for i in range(count):
        s = i * hop
        e = s + frame
        out[i] = values[:, s:e].mean(axis=1)
        starts[i] = s
        ends[i] = e
    return out, starts, ends


def _decimate_envelope(u1: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    if orig_sr == target_sr:
        return u1.copy()
    g = gcd(orig_sr, target_sr)
    up, down = target_sr // g, orig_sr // g
    rows = [resample_poly(row, up, down).astype(np.float64) for row in u1]
    min_n = min(map(len, rows))
    return np.stack([r[:min_n] for r in rows], axis=0)


def compute_scattering_like(x: np.ndarray, sr: int, config: TextureConfig) -> dict:
    """First-order carrier modulus + second-order modulation summary."""
    config.validate()
    centers = config.carrier_centers_hz
    carrier_complex = analytic_wavelet_bank(x, sr, centers, config.carrier_q)
    u1 = np.abs(carrier_complex)

    first_frames, starts, ends = _frame_reduce(u1, sr, config.frame_ms, config.hop_ms)
    first_global = u1.mean(axis=1)
    first_std = u1.std(axis=1)
    first_cv = first_std / (first_global + config.eps)

    env = _decimate_envelope(u1, sr, config.envelope_sample_rate)
    mod_rates = config.modulation_rates_hz
    mod_by_carrier = np.empty((len(centers), len(mod_rates)), dtype=np.float64)
    for i, row in enumerate(env):
        if len(mod_rates) == 0:  # first-order-only configuration
            continue
        centered = row - np.mean(row)  # DC removal: modulation measures fluctuation
        mods = modulation_wavelet_bank(centered, config.envelope_sample_rate, mod_rates, config.modulation_q)
        mod_by_carrier[i] = np.mean(np.abs(mods), axis=1)

    return {
        "carrier_centers_hz": np.asarray(centers, dtype=np.float64),
        "u1": u1,
        "first_frames": first_frames,
        "frame_starts_samples": starts,
        "frame_ends_samples": ends,
        "first_global": first_global,
        "first_cv": first_cv,
        "modulation_rates_hz": np.asarray(mod_rates, dtype=np.float64),
        "mod_by_carrier": mod_by_carrier,
    }
