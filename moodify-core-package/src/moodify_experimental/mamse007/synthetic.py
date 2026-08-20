"""Synthetic latent-auditory matrix for tests (seeded, reproducible)."""

from __future__ import annotations

import numpy as np

FEATURES = (
    "rms_db", "peak_db", "spectral_centroid_hz", "band_bass_ratio",
    "band_presence_ratio", "band_air_ratio", "stereo_correlation",
    "crest_db", "hf_ratio", "phase_risk_proxy",
)


def latent_auditory_matrix(n: int = 720, seed: int = 7, anomaly: tuple[int, int] | None = None) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 8 * np.pi, n)
    z = np.column_stack([
        np.sin(t) + 0.20 * np.sin(0.23 * t),
        np.cos(0.47 * t + 0.4),
        np.sin(1.7 * t + 0.2) * 0.55,
    ])
    load = np.array([
        [2.4, 1.8, 0.2],
        [2.2, 1.5, 0.4],
        [380., 720., 80.],
        [-.10, -.20, .02],
        [.08, .23, .04],
        [.03, .19, .07],
        [.12, -.05, .28],
        [1.4, -.8, .4],
        [.02, .16, .05],
        [.01, .00, .05],
    ])
    offsets = np.array([-18., -6., 3200., .28, .24, .08, .72, 9.5, .16, .025])
    x = z @ load.T + offsets
    noise_scale = np.array([.20, .20, 35., .01, .01, .006, .012, .15, .006, .003])
    x += rng.normal(size=x.shape) * noise_scale
    if anomaly is not None:
        a, b = anomaly
        x[a:b, [2, 5, 6, 9]] += np.array([900., .10, -.32, .12])
    return x, z
