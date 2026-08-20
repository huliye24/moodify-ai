"""Constant-Q observation via librosa.cqt (locked 0.11.0).

The dense CQT matrix is a transient in-memory intermediate: it is released
after sketch/evidence extraction and never persisted by default.
"""

from __future__ import annotations

from dataclasses import dataclass

import librosa
import numpy as np

from .config import CQTConfig, DEFAULT_CONFIG


@dataclass
class CQTObservation:
    sample_rate: int
    hop_length: int
    frequencies_hz: np.ndarray
    times_s: np.ndarray
    magnitude: np.ndarray  # (bins, frames) transient in-memory research representation
    power: np.ndarray
    status: str
    notes: tuple[str, ...]

    def mean_power(self) -> np.ndarray:
        if self.power.size == 0:
            return np.zeros(len(self.frequencies_hz), dtype=np.float64)
        return np.mean(self.power, axis=1)


def _mono(samples: np.ndarray) -> np.ndarray:
    x = np.asarray(samples, dtype=np.float32)
    if x.ndim == 2:
        x = x.mean(axis=1)
    if x.ndim != 1:
        raise ValueError("samples must be mono or (samples, channels)")
    return x


def compute_cqt_observation(
    samples: np.ndarray,
    sr: int,
    config: CQTConfig = DEFAULT_CONFIG,
) -> CQTObservation:
    x = _mono(samples)
    freqs = config.frequencies()
    if len(x) == 0 or not np.isfinite(x).all():
        return CQTObservation(sr, config.hop_length, freqs, np.array([]),
                              np.empty((len(freqs), 0)), np.empty((len(freqs), 0)),
                              "UNAVAILABLE", ("empty or non-finite input",))
    if np.max(np.abs(x)) < 1e-10:
        n_frames = 1 + max(0, (len(x) - 1) // config.hop_length)
        return CQTObservation(sr, config.hop_length, freqs,
                              librosa.frames_to_time(np.arange(n_frames), sr=sr, hop_length=config.hop_length),
                              np.zeros((len(freqs), n_frames), dtype=np.float32),
                              np.zeros((len(freqs), n_frames), dtype=np.float32),
                              "SILENCE", ("no dominant-frequency claim for silence",))

    C = librosa.cqt(
        x,
        sr=sr,
        hop_length=config.hop_length,
        fmin=config.fmin_hz,
        n_bins=config.n_bins,
        bins_per_octave=config.bins_per_octave,
        filter_scale=config.filter_scale,
        norm=1,
        sparsity=config.sparsity,
        window=config.window,
        scale=True,
        pad_mode="constant",
        res_type="soxr_hq",
    )
    mag = np.abs(C).astype(np.float32)
    power = (mag.astype(np.float64) ** 2).astype(np.float32)
    times = librosa.frames_to_time(np.arange(C.shape[1]), sr=sr, hop_length=config.hop_length)
    return CQTObservation(sr, config.hop_length, freqs, times, mag, power, "OK", ())


def dominant_frequency_from_mean(obs: CQTObservation) -> float | None:
    if obs.status != "OK" or obs.power.size == 0:
        return None
    p = obs.mean_power()
    if not np.any(p > 0):
        return None
    k = int(np.argmax(p))
    return float(obs.frequencies_hz[k])


def local_peaks_from_mean(obs: CQTObservation, min_relative: float = 0.05) -> list[tuple[int, float, float]]:
    """Return (bin, frequency_hz, mean_power) local maxima, strongest first."""
    if obs.status != "OK":
        return []
    p = obs.mean_power().astype(np.float64)
    if len(p) < 3 or np.max(p) <= 0:
        return []
    threshold = np.max(p) * min_relative
    out = []
    for k in range(1, len(p) - 1):
        if p[k] >= threshold and p[k] > p[k - 1] and p[k] >= p[k + 1]:
            out.append((k, float(obs.frequencies_hz[k]), float(p[k])))
    out.sort(key=lambda item: item[2], reverse=True)
    return out
