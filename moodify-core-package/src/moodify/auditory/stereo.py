"""Stereo measurements (DSK-MFY-AUDITORY-SCAN-001).

Mono input: stereo metrics are null with a UNAVAILABLE status; nothing is
fabricated.
"""

from __future__ import annotations

import numpy as np

from moodify.auditory.models import MetricValue


def compute_stereo_metrics(samples: np.ndarray) -> dict:
    m: dict = {}
    if samples.ndim < 2 or samples.shape[1] < 2:
        for key in (
            "stereo_correlation", "mid_energy_ratio", "side_energy_ratio",
            "side_to_mid_db", "stereo_width_proxy", "negative_correlation_ratio",
            "phase_risk_ratio",
        ):
            m[key] = MetricValue(None, key.startswith("side_to_mid") and "dB" or "ratio",
                                 "mono", "UNAVAILABLE", ["mono input"]).to_dict()
        m["_mono"] = True
        return m

    left = samples[:, 0].astype(np.float64)
    right = samples[:, 1].astype(np.float64)
    mid = (left + right) / 2.0
    side = (left - right) / 2.0

    corr = float(np.corrcoef(left, right)[0, 1]) if np.std(left) > 0 and np.std(right) > 0 else 0.0
    m["stereo_correlation"] = MetricValue(round(corr, 4), "ratio", "pearson").to_dict()

    mid_e = float(np.mean(mid ** 2))
    side_e = float(np.mean(side ** 2))
    total = mid_e + side_e + 1e-12
    m["mid_energy_ratio"] = MetricValue(round(mid_e / total, 6), "ratio", "derived").to_dict()
    m["side_energy_ratio"] = MetricValue(round(side_e / total, 6), "ratio", "derived").to_dict()
    side_to_mid = float(10 * np.log10((side_e + 1e-12) / (mid_e + 1e-12)))
    m["side_to_mid_db"] = MetricValue(round(side_to_mid, 2), "dB", "derived").to_dict()
    m["stereo_width_proxy"] = MetricValue(round(1.0 - abs(corr), 4), "ratio", "derived").to_dict()

    # frame-wise negative correlation ratio (phase risk)
    win = 4096
    hop = 2048
    n = (len(left) - win) // hop + 1
    neg = 0
    for i in range(n):
        left_win = left[i * hop: i * hop + win]
        right_win = right[i * hop: i * hop + win]
        if np.std(left_win) > 0 and np.std(right_win) > 0:
            c = float(np.corrcoef(left_win, right_win)[0, 1])
            if c < -0.7:
                neg += 1
    neg_ratio = neg / max(n, 1)
    m["negative_correlation_ratio"] = MetricValue(round(neg_ratio, 6), "ratio", "frame-wise").to_dict()

    # phase risk: frames where side energy exceeds mid energy substantially
    phase_risk = 0
    for i in range(n):
        left_win = left[i * hop: i * hop + win]
        right_win = right[i * hop: i * hop + win]
        m_e = float(np.mean(((left_win + right_win) / 2) ** 2))
        s_e = float(np.mean(((left_win - right_win) / 2) ** 2))
        if s_e > 3.0 * m_e + 1e-12:
            phase_risk += 1
    m["phase_risk_ratio"] = MetricValue(round(phase_risk / max(n, 1), 6), "ratio", "frame-wise").to_dict()
    m["_mono"] = False
    return m
