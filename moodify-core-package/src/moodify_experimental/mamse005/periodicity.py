"""Cepstral periodicity: F0 candidate via quefrency peak search.

The result is a cepstral candidate, never ground-truth pitch. Noise and
low-periodicity signals are not forced onto a stable F0.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import find_peaks


def rms_dbfs(frame: np.ndarray) -> float:
    rms = float(np.sqrt(np.mean(np.asarray(frame, dtype=np.float64) ** 2)))
    return float(20 * np.log10(rms + 1e-12))


def estimate_periodicity(cep: np.ndarray, sr: int, f0_min_hz: float, f0_max_hz: float,
                         min_score: float = 0.08) -> dict:
    c = np.asarray(cep, dtype=np.float64)
    q_min = max(1, int(np.floor(sr / f0_max_hz)))
    q_max = min(len(c) // 2 - 1, int(np.ceil(sr / f0_min_hz)))
    if q_max <= q_min + 2:
        return {"available": False, "reason": "invalid_search_range", "f0_candidate_hz": None,
                "periodicity_score": None, "quefrency_s": None, "peak_prominence": None}
    region = c[q_min:q_max + 1].copy()
    baseline = float(np.median(region))
    centered = region - baseline
    scale = float(np.median(np.abs(centered)) + 1e-9)
    peaks, props = find_peaks(centered, prominence=max(scale * 0.5, 1e-9))
    if peaks.size == 0:
        return {"available": False, "reason": "no_cepstral_peak", "f0_candidate_hz": None,
                "periodicity_score": 0.0, "quefrency_s": None, "peak_prominence": 0.0}
    prominences = props.get("prominences", np.zeros_like(peaks, dtype=float))
    qs = q_min + peaks
    raw = prominences / (scale + 1e-9)
    penalty = 1.0 / np.sqrt(np.maximum(qs / max(q_min, 1), 1.0))
    ranked = raw * penalty
    best_i = int(np.argmax(ranked))
    idx = int(qs[best_i])
    prominence = float(prominences[best_i])
    score = float(prominence / (prominence + 3.0 * scale + 1e-12))
    f0 = float(sr / idx)
    if score < min_score:
        return {"available": False, "reason": "low_periodicity", "f0_candidate_hz": None,
                "periodicity_score": score, "quefrency_s": idx / sr, "peak_prominence": prominence}
    return {"available": True, "reason": None, "f0_candidate_hz": f0, "periodicity_score": score,
            "quefrency_s": idx / sr, "peak_prominence": prominence}
