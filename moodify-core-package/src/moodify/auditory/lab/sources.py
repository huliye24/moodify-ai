"""Deterministic control sources C1-C6 (MFY-PHASE1-DEPTH-005).

Synthetic, reproducible, no proprietary media. Every source has an
unperturbed control baseline.
"""

from __future__ import annotations

import numpy as np

SR = 48000

SOURCE_SPECS = {
    "C1": {"name": "pure sine", "seconds": 8.0},
    "C2": {"name": "stereo same-phase sine", "seconds": 8.0},
    "C3": {"name": "broadband noise", "seconds": 8.0},
    "C4": {"name": "band-limited noise", "seconds": 8.0},
    "C5": {"name": "two-state level sine", "seconds": 8.0},
    "C6": {"name": "mixed technical source", "seconds": 10.0},
}


def generate_source(source_id: str) -> np.ndarray:
    """Generate one control source (mono or stereo ndarray)."""
    seconds = SOURCE_SPECS[source_id]["seconds"]
    n = int(seconds * SR)
    t = np.arange(n) / SR
    if source_id == "C1":
        return (0.3 * np.sin(2 * np.pi * 440 * t)).astype(np.float64)
    if source_id == "C2":
        mono = 0.3 * np.sin(2 * np.pi * 440 * t)
        return np.stack([mono, mono], axis=1)
    if source_id == "C3":
        rng = np.random.default_rng(7)
        return (0.2 * rng.standard_normal(n)).astype(np.float64)
    if source_id == "C4":
        from scipy.signal import butter, lfilter

        rng = np.random.default_rng(8)
        b, a = butter(6, 6000 / (SR / 2))
        return lfilter(b, a, 0.2 * rng.standard_normal(n)).astype(np.float64)
    if source_id == "C5":
        half = n // 2
        low = 0.05 * np.sin(2 * np.pi * 440 * t)
        high = 0.5 * np.sin(2 * np.pi * 440 * t)
        return np.concatenate([low[:half], high[half:]]).astype(np.float64)
    # C6 mixed: sine base with a quiet band and a low-gain segment
    x = 0.3 * np.sin(2 * np.pi * 330 * t)
    x[int(2.0 * SR):int(3.0 * SR)] *= 0.2
    return x.astype(np.float64)
