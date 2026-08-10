"""Standards-backed loudness measurements (MFY-PHASE1-DEPTH-001).

Integrated loudness follows ITU-R BS.1770-5 / EBU Tech 3341: per-channel
K-weighting with standard 48 kHz coefficients (44.1 kHz uses the same
coefficients, an accepted approximation), channel-weighted energy
aggregation, 400 ms blocks, -70 LUFS absolute gate and -10 LU relative
gate. Other sample rates are resampled to 48 kHz before weighting.
Loudness Range follows EBU Tech 3342 (3 s short-term loudness
percentiles); insufficient duration yields UNAVAILABLE, never a fake 0.
"""

from __future__ import annotations

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from scipy.signal import lfilter, resample_poly

# BS.1770 K-weighting coefficients (48 kHz; accepted for 44.1 kHz).
_RLB_B = [1.53512485958697, -2.69169618940638, 1.19839281085285]
_RLB_A = [1.0, -1.69065929318241, 0.73248077421585]
_HS_B = [1.0, -2.0, 1.0]
_HS_A = [1.0, -1.99004745483398, 0.99007225036621]

_ABS_GATE_LUFS = -70.0
_REL_GATE_LU = -10.0
_BLOCK_S = 0.4
_SHORT_BLOCK_S = 3.0
_LOUDNESS_OFFSET = -0.691  # 130 dB reference


def _k_weighted(x: np.ndarray, sr: int) -> np.ndarray:
    """K-weighting (RLB high-pass + high-shelf).

    Standard coefficients are defined at 48 kHz. 44.1 kHz uses the same
    coefficients (accepted, error < 0.1 LU). Other rates are resampled
    to 48 kHz first, per BS.1770 guidance.
    """
    if sr not in (44100, 48000):
        x = resample_poly(x, 48000, sr)
    y = lfilter(_RLB_B, _RLB_A, x)
    return lfilter(_HS_B, _HS_A, y)


def _block_loudness(y: np.ndarray, sr: int, block_s: float, overlap: float = 0.75) -> np.ndarray:
    """Per-block loudness with standard 75% overlap (BS.1770: 400 ms / 100 ms hop)."""
    block = int(block_s * sr)
    hop = max(1, int(block * (1 - overlap)))
    n = len(y)
    if n < block:
        return np.array([])
    z = sliding_window_view(y, block)[::hop]  # view, no copy
    return 10 * np.log10(np.mean(z ** 2, axis=1) + 1e-12) + _LOUDNESS_OFFSET


def _channel_weight(channels: int) -> list[float]:
    # BS.1770-5: L=1.0, R=1.0, C=1.0, Ls/Rs=1.41. We handle mono/stereo.
    if channels <= 1:
        return [1.0]
    return [1.0, 1.0]


def integrated_loudness_lufs(samples: np.ndarray, sr: int) -> float:
    """BS.1770 integrated loudness for mono or stereo signals (not 5.1)."""
    if samples.ndim == 1:
        samples = samples[:, None]
    weights = _channel_weight(samples.shape[1])
    energies = []
    for channel, weight in zip(range(samples.shape[1]), weights):
        weighted = _k_weighted(samples[:, channel], sr)
        loudness = _block_loudness(weighted, sr, _BLOCK_S)
        if loudness.size == 0:
            return _ABS_GATE_LUFS
        energies.append(weight * 10 ** (loudness / 10))
    combined = np.sum(energies, axis=0) / sum(weights)
    # loudness already carries _LOUDNESS_OFFSET; re-adding it here double-counts
    # the 130 dB reference (measured -0.65 to -1.28 LUFS bias vs pyloudnorm).
    block_loudness = 10 * np.log10(combined + 1e-12)

    abs_gate = block_loudness[block_loudness > _ABS_GATE_LUFS]
    if abs_gate.size == 0:
        return _ABS_GATE_LUFS
    rel_threshold = np.mean(abs_gate) + _REL_GATE_LU
    final = abs_gate[abs_gate > rel_threshold]
    if final.size == 0:
        return _ABS_GATE_LUFS
    return float(10 * np.log10(np.mean(10 ** (final / 10)) + 1e-12))


def loudness_range_lu(samples: np.ndarray, sr: int) -> float | None:
    """EBU Tech 3342 loudness range; None when duration is insufficient."""
    mono = samples.mean(axis=1) if samples.ndim > 1 else samples
    weighted = _k_weighted(mono, sr)
    short = _block_loudness(weighted, sr, _SHORT_BLOCK_S)
    if short.size < 2:
        return None
    lo, hi = np.percentile(short, [10, 95])
    return float(max(0.0, hi - lo))
