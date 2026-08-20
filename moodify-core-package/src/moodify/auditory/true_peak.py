"""True peak measurement (MFY-PHASE1-DEPTH-001).

ITU-R BS.1770-5 true peak: the maximum of the reconstructed continuous
signal, obtained by oversampling. We use 4x polyphase resampling
(scipy resample_poly), which is a close approximation of the standard's
interpolation guidance. The value is reported per-channel with the max
aggregation; gain applied before oversampling matches the standard's
order of operations.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import resample_poly

OVERSAMPLE = 4


def true_peak_db(x: np.ndarray, sr: int | None = None) -> float:
    """4x oversampled true peak in dBFS (per-channel max for stereo)."""
    if x.ndim == 1:
        x = x[:, None]
    peaks = []
    for channel in range(x.shape[1]):
        upsampled = resample_poly(x[:, channel], OVERSAMPLE, 1)
        peaks.append(float(np.max(np.abs(upsampled))))
    peak = max(peaks)
    return float(20 * np.log10(peak + 1e-12))
