"""Fixed-width log-frequency sketch from a CQT observation.

All pitch-derived values are ESTIMATOR/DESCRIPTOR: dominant_midi is not
perceived pitch, chroma is not harmony understanding, tuning deviation is
not a certified tuner.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .config import CQTConfig, DEFAULT_CONFIG, cents_from_nearest_equal_temperament, hz_to_midi
from .cqt import CQTObservation

FEATURE_NAMES: tuple[str, ...] = (
    "dominant_frequency_hz",
    "dominant_midi",
    "tuning_deviation_cents",
    "log_centroid_octaves",
    "log_spread_octaves",
    "log_spectral_entropy",
    "tonal_peakiness",
) + tuple(f"chroma_{i}" for i in range(12)) + tuple(f"octave_{i}" for i in range(9))

FEATURE_AUTHORITY: dict[str, str] = {
    "dominant_frequency_hz": "DESCRIPTOR (log-geometry grid, quadratic subbin)",
    "dominant_midi": "ESTIMATOR — not perceived pitch",
    "tuning_deviation_cents": "ESTIMATOR — not a certified tuner",
    "log_centroid_octaves": "DESCRIPTOR",
    "log_spread_octaves": "DESCRIPTOR",
    "log_spectral_entropy": "DESCRIPTOR",
    "tonal_peakiness": "DESCRIPTOR",
    **{f"chroma_{i}": "DESCRIPTOR — not harmony understanding" for i in range(12)},
    **{f"octave_{i}": "DESCRIPTOR" for i in range(9)},
}


@dataclass
class LogFrequencySketch:
    feature_names: tuple[str, ...]
    times_s: np.ndarray
    values: np.ndarray  # frames x features; NaN = unavailable
    status: str
    geometry_id: str
    config_hash: str


def _safe_entropy(p: np.ndarray) -> float:
    p = p[p > 0]
    if p.size <= 1:
        return 0.0
    h = -float(np.sum(p * np.log(p + 1e-18)))
    return h / math.log(len(p))


def _quadratic_subbin_frequency(power: np.ndarray, freqs: np.ndarray, k: int) -> float:
    if k <= 0 or k >= len(power) - 1:
        return float(freqs[k])
    y0, y1, y2 = np.log(power[k - 1:k + 2] + 1e-18)
    denom = y0 - 2 * y1 + y2
    if abs(denom) < 1e-12:
        return float(freqs[k])
    delta = 0.5 * (y0 - y2) / denom
    delta = float(np.clip(delta, -0.5, 0.5))
    log2f = np.log2(freqs[k]) + delta * (np.log2(freqs[k + 1]) - np.log2(freqs[k]))
    return float(2.0 ** log2f)


def build_log_frequency_sketch(
    obs: CQTObservation,
    config: CQTConfig = DEFAULT_CONFIG,
) -> LogFrequencySketch:
    n_frames = len(obs.times_s)
    values = np.full((n_frames, len(FEATURE_NAMES)), np.nan, dtype=np.float32)
    if obs.status != "OK":
        return LogFrequencySketch(FEATURE_NAMES, obs.times_s, values, obs.status,
                                  config.geometry_id, config.sha256())

    freqs = obs.frequencies_hz.astype(np.float64)
    log_oct = np.log2(freqs / config.fmin_hz)
    for t in range(n_frames):
        p = obs.power[:, t].astype(np.float64)
        total = float(np.sum(p))
        if total <= 1e-18:
            continue
        prob = p / total
        k = int(np.argmax(p))
        dom_f = _quadratic_subbin_frequency(p, freqs, k)
        dom_midi = float(hz_to_midi(dom_f))
        cents = float(cents_from_nearest_equal_temperament(dom_f))
        centroid = float(np.sum(prob * log_oct))
        spread = float(np.sqrt(np.sum(prob * (log_oct - centroid) ** 2)))
        entropy = _safe_entropy(prob)
        peakiness = float(np.max(prob))

        chroma = np.zeros(12, dtype=np.float64)
        for b, energy in enumerate(p):
            midi = hz_to_midi(freqs[b])
            pc = int(round(float(midi))) % 12
            chroma[pc] += energy
        if chroma.sum() > 0:
            chroma /= chroma.sum()

        octaves = np.zeros(config.n_octaves, dtype=np.float64)
        for o in range(config.n_octaves):
            lo = o * config.bins_per_octave
            hi = min((o + 1) * config.bins_per_octave, len(p))
            octaves[o] = np.sum(p[lo:hi])
        if octaves.sum() > 0:
            octaves /= octaves.sum()

        row = [dom_f, dom_midi, cents, centroid, spread, entropy, peakiness,
               *chroma.tolist(), *octaves.tolist()]
        values[t] = np.asarray(row, dtype=np.float32)

    return LogFrequencySketch(FEATURE_NAMES, obs.times_s, values, "OK",
                              config.geometry_id, config.sha256())
