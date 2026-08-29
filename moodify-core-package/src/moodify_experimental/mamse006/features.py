"""Modulation feature summary: rate/scale/energy ratios/orientation/ridge.

All outputs are EXPERIMENTAL descriptors. Ridge is a CANDIDATE; orientation
is a spectrogram-texture index, not physical source motion.
"""

from __future__ import annotations

import numpy as np

from .modulation import normalized_entropy


def _band_ratio(rates, power, lo, hi):
    mask = (rates >= lo) & (rates < hi)
    total = float(np.sum(power)) + 1e-20
    return float(np.sum(power[mask]) / total)


def summarize_modulation(mod: dict, temporal_min_hz=0.25, temporal_max_hz=40.0, spectral_max_cpo=4.0) -> dict:
    tr = np.asarray(mod["temporal_rates_hz"])
    sr = np.asarray(mod["spectral_rates_cpo"])
    tm = np.asarray(mod["temporal_marginal"])
    sm = np.asarray(mod["spectral_marginal"])
    dyn = np.asarray(mod["dynamic_joint_power"])

    tmask = (tr >= temporal_min_hz) & (tr <= temporal_max_hz)
    tpow = tm[tmask]
    trate = tr[tmask]
    if tpow.size == 0 or np.sum(tpow) <= 1e-18:
        temporal_peak = None
        temporal_centroid = None
    else:
        temporal_peak = float(trate[int(np.argmax(tpow))])
        temporal_centroid = float(np.sum(trate * tpow) / (np.sum(tpow) + 1e-20))

    smask = np.abs(sr) <= spectral_max_cpo
    sr_abs = np.abs(sr[smask])
    spow = sm[smask]
    nonzero = sr_abs > (1.0 / max(2, sr.size / 2))
    if np.any(nonzero) and np.sum(spow[nonzero]) > 1e-18:
        spectral_peak = float(sr_abs[nonzero][int(np.argmax(spow[nonzero]))])
    else:
        spectral_peak = None

    pos_t = (tr >= temporal_min_hz) & (tr <= temporal_max_hz)
    valid_s = (np.abs(sr) > 1e-9) & (np.abs(sr) <= spectral_max_cpo)
    e_pos = float(np.sum(dyn[np.ix_(sr > 1e-9, pos_t)]))
    e_neg = float(np.sum(dyn[np.ix_(sr < -1e-9, pos_t)]))
    orientation = (e_pos - e_neg) / (e_pos + e_neg + 1e-20)

    ridge_mask = np.outer(valid_s, pos_t)
    masked = np.where(ridge_mask, dyn, 0.0)
    total_valid = float(masked.sum())
    ridge = None
    if total_valid > 1e-18:
        i, j = np.unravel_index(int(np.argmax(masked)), masked.shape)
        rt = float(tr[j])
        rs = float(sr[i])
        i0, i1 = max(0, i - 1), min(masked.shape[0], i + 2)
        j0, j1 = max(0, j - 1), min(masked.shape[1], j + 2)
        local = float(masked[i0:i1, j0:j1].sum())
        ridge = {
            "temporal_rate_hz": rt,
            "spectral_rate_cpo": rs,
            "velocity_oct_per_s": float(rt / abs(rs)) if abs(rs) > 1e-12 else None,
            "ridge_concentration": local / (total_valid + 1e-20),
            "status": "CANDIDATE",
        }

    pos_valid_power = tm[tmask]
    return {
        "temporal_peak_hz": temporal_peak,
        "temporal_centroid_hz": temporal_centroid,
        "slow_energy_ratio": _band_ratio(trate, pos_valid_power, 0.25, 4.0) if trate.size else 0.0,
        "mid_energy_ratio": _band_ratio(trate, pos_valid_power, 4.0, 16.0) if trate.size else 0.0,
        "fast_energy_ratio": _band_ratio(trate, pos_valid_power, 16.0, temporal_max_hz + 1e-9) if trate.size else 0.0,
        "temporal_modulation_entropy": normalized_entropy(pos_valid_power),
        "spectral_peak_cpo": spectral_peak,
        "diagonal_orientation_index": float(np.clip(orientation, -1.0, 1.0)),
        "ridge": ridge,
    }
