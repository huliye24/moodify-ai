"""Deterministic perturbation operators (MFY-PHASE1-DEPTH-005).

Every operator is a versioned deterministic function of its parameters.
Perturbations are scientific instruments for validating the ear, not
product post-processing.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from moodify.auditory.lab.models import PerturbationSpec

PERTURBATION_VERSION = "lab-perturbation-v1"

# operator -> ladder strengths (params + region)
LADDERS: dict[str, list[dict]] = {
    # Digital full-scale clipping requires the region to reach >= 0.999.
    # pre_gain_db normalizes the C1 source (peak 0.3) to full scale first.
    "HARD_CLIP": [
        {"threshold": 0.999, "pre_gain_db": 12.0, "region_start_ms": 2000, "region_end_ms": 2600},
        {"threshold": 1.0, "pre_gain_db": 12.0, "region_start_ms": 2000, "region_end_ms": 2600},
    ],
    "NEAR_CLIP": [
        {"threshold": 0.95, "pre_gain_db": 12.0, "region_start_ms": 2000, "region_end_ms": 2600},
        {"threshold": 0.98, "pre_gain_db": 12.0, "region_start_ms": 2000, "region_end_ms": 2600},
    ],
    "DC_OFFSET": [
        {"offset": 0.01, "region_start_ms": 0, "region_end_ms": 0},
        {"offset": 0.05, "region_start_ms": 0, "region_end_ms": 0},
    ],
    # The stepped region must be long enough for the 400 ms level window
    # to hold several fully-stepped windows; <= 6 dB stays below clipping.
    "GAIN_STEP": [
        {"gain_db": 8.0, "region_start_ms": 3000, "region_end_ms": 4600},
        {"gain_db": 12.0, "region_start_ms": 3000, "region_end_ms": 4600},
    ],
    "SILENCE_INSERT": [
        {"duration_ms": 300, "region_start_ms": 4000, "region_end_ms": 4300},
        {"duration_ms": 600, "region_start_ms": 4000, "region_end_ms": 4600},
        {"duration_ms": 1000, "region_start_ms": 4000, "region_end_ms": 5000},
    ],
    "LOWPASS": [
        {"cutoff_hz": 12000, "region_start_ms": 2000, "region_end_ms": 4000},
        {"cutoff_hz": 8000, "region_start_ms": 2000, "region_end_ms": 4000},
        {"cutoff_hz": 4000, "region_start_ms": 2000, "region_end_ms": 4000},
    ],
    "ANTIPHASE_REGION": [
        {"region_start_ms": 1500, "region_end_ms": 2500},
        {"region_start_ms": 1500, "region_end_ms": 3500},
    ],
    "NOISE_INJECTION": [
        {"snr_db": 20.0, "region_start_ms": 2000, "region_end_ms": 6000},
        {"snr_db": 10.0, "region_start_ms": 2000, "region_end_ms": 6000},
    ],
    "DYNAMIC_COMPRESSION": [
        {"ratio": 2.0, "threshold": 0.15, "region_start_ms": 0, "region_end_ms": 0},
        {"ratio": 4.0, "threshold": 0.15, "region_start_ms": 0, "region_end_ms": 0},
    ],
}


def apply_perturbation(x: np.ndarray, sr: int, spec: PerturbationSpec) -> np.ndarray:
    """Apply one operator to the source; returns a new array (never mutates)."""
    out = np.array(x, dtype=np.float64, copy=True)
    handler: Callable = {
        "HARD_CLIP": _hard_clip,
        "NEAR_CLIP": _near_clip,
        "DC_OFFSET": _dc_offset,
        "GAIN_STEP": _gain_step,
        "SILENCE_INSERT": _silence_insert,
        "LOWPASS": _lowpass,
        "ANTIPHASE_REGION": _antiphase,
        "NOISE_INJECTION": _noise_injection,
        "DYNAMIC_COMPRESSION": _dynamic_compression,
    }[spec.operator]
    return handler(out, sr, spec)


def _region_slice(x: np.ndarray, sr: int, start_ms: int, end_ms: int):
    if end_ms <= 0:
        return slice(None)
    return slice(int(start_ms * sr / 1000), int(end_ms * sr / 1000))


def _hard_clip(x: np.ndarray, sr: int, spec: PerturbationSpec) -> np.ndarray:
    threshold = float(spec.params.get("threshold", 1.0))
    pre_gain = 10 ** (float(spec.params.get("pre_gain_db", 0.0)) / 20)
    region = _region_slice(x, sr, spec.region_start_ms, spec.region_end_ms)
    x[region] = np.clip(x[region] * pre_gain, -threshold, threshold)
    return x


def _near_clip(x: np.ndarray, sr: int, spec: PerturbationSpec) -> np.ndarray:
    # Clamp (not normalize) so near-full-scale samples sit in the
    # 0.95..0.999 band that the near-clipping detector observes.
    threshold = float(spec.params.get("threshold", 0.98))
    pre_gain = 10 ** (float(spec.params.get("pre_gain_db", 0.0)) / 20)
    region = _region_slice(x, sr, spec.region_start_ms, spec.region_end_ms)
    x[region] = np.clip(x[region] * pre_gain, -threshold, threshold)
    return x


def _dc_offset(x: np.ndarray, sr: int, spec: PerturbationSpec) -> np.ndarray:
    offset = float(spec.params.get("offset", 0.01))
    return x + offset


def _gain_step(x: np.ndarray, sr: int, spec: PerturbationSpec) -> np.ndarray:
    gain = 10 ** (float(spec.params.get("gain_db", 6.0)) / 20)
    region = _region_slice(x, sr, spec.region_start_ms, spec.region_end_ms)
    x[region] = x[region] * gain
    return x


def _silence_insert(x: np.ndarray, sr: int, spec: PerturbationSpec) -> np.ndarray:
    region = _region_slice(x, sr, spec.region_start_ms, spec.region_end_ms)
    x[region] = 0.0
    return x


def _lowpass(x: np.ndarray, sr: int, spec: PerturbationSpec) -> np.ndarray:
    from scipy.signal import butter, lfilter

    cutoff = float(spec.params.get("cutoff_hz", 8000))
    region = _region_slice(x, sr, spec.region_start_ms, spec.region_end_ms)
    b, a = butter(6, cutoff / (sr / 2))
    x[region] = lfilter(b, a, x[region])
    return x


def _antiphase(x: np.ndarray, sr: int, spec: PerturbationSpec) -> np.ndarray:
    if x.ndim < 2 or x.shape[1] < 2:
        raise ValueError("ANTIPHASE_REGION requires stereo source")
    region = _region_slice(x, sr, spec.region_start_ms, spec.region_end_ms)
    x[region, 1] = -x[region, 1]
    return x


def _noise_injection(x: np.ndarray, sr: int, spec: PerturbationSpec) -> np.ndarray:
    snr_db = float(spec.params.get("snr_db", 20.0))
    region = _region_slice(x, sr, spec.region_start_ms, spec.region_end_ms)
    rng = np.random.default_rng(42)
    seg = x[region]
    signal_power = np.mean(seg ** 2) + 1e-12
    noise_power = signal_power / (10 ** (snr_db / 10))
    x[region] = seg + rng.standard_normal(seg.shape) * np.sqrt(noise_power)
    return x


def _dynamic_compression(x: np.ndarray, sr: int, spec: PerturbationSpec) -> np.ndarray:
    ratio = float(spec.params.get("ratio", 2.0))
    threshold = float(spec.params.get("threshold", 0.3))
    compressed = np.where(np.abs(x) > threshold,
                          threshold + (np.abs(x) - threshold) / ratio,
                          np.abs(x))
    return np.sign(x) * compressed
