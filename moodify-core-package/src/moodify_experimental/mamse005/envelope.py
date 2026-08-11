"""Spectral envelope analysis: resonance candidates + roughness measure.

Resonance candidates are envelope peaks with a prominence gate — they are
candidates, never ground-truth formants, especially on full mixes.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import find_peaks


def resonance_candidates(envelope_logmag: np.ndarray, sr: int, n_fft: int, max_hz: float,
                         prominence_db: float, max_candidates: int) -> list[dict]:
    env = np.asarray(envelope_logmag, dtype=np.float64)
    freq = np.fft.rfftfreq(n_fft, 1 / sr)
    db = 20 / np.log(10) * env
    mask = (freq >= 80) & (freq <= min(max_hz, sr / 2))
    indices = np.where(mask)[0]
    if indices.size < 3:
        return []
    local = db[indices]
    peaks, props = find_peaks(local, prominence=prominence_db, distance=max(1, int(80 / (sr / n_fft))))
    if peaks.size == 0:
        return []
    prom = props["prominences"]
    order = np.argsort(prom)[::-1][:max_candidates]
    rows = []
    for j in order:
        k = int(indices[int(peaks[j])])
        rows.append({"frequency_hz": float(freq[k]), "prominence_db": float(prom[j]), "envelope_db": float(db[k])})
    return sorted(rows, key=lambda r: r["frequency_hz"])


def roughness_measure(y: np.ndarray) -> float:
    y = np.asarray(y, dtype=np.float64)
    if y.size < 3:
        return 0.0
    d2 = np.diff(y, n=2)
    return float(np.sqrt(np.mean(d2 * d2)))
