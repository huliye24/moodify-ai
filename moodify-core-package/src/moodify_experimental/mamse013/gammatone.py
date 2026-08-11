"""MAMSE-013 gammatone filterbank operator.

Real-valued 4th-order gammatone filters (Patterson-style impulse
responses), bandwidth 1.019 x ERB, filtered via FFT convolution.
Per-channel filter gain is normalized to unit peak so channel powers are
comparable across the band. Mono only in v0.1; stereo raises ValueError.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.signal import fftconvolve

from .config import ERBConfig, erb_bandwidth_hz

MIN_ENERGY = 1e-12


@dataclass
class ErbObservation:
    status: str  # VALID | EMPTY | DEGRADED
    notes: tuple[str, ...]
    center_frequencies_hz: np.ndarray
    times_s: np.ndarray
    channel_energies: np.ndarray  # n_channels x n_frames
    mean_channel_power: np.ndarray  # n_channels
    sr: int
    config_hash: str

    @property
    def dominant_channel(self) -> int:
        return int(np.argmax(self.mean_channel_power))

    @property
    def dominant_frequency_hz(self) -> float:
        return float(self.center_frequencies_hz[self.dominant_channel])

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "notes": list(self.notes),
            "n_channels": len(self.center_frequencies_hz),
            "n_frames": int(self.times_s.size),
            "dominant_channel": self.dominant_channel,
            "dominant_frequency_hz": self.dominant_frequency_hz,
            "config_hash": self.config_hash,
        }


def _gammatone_ir(freq_hz: float, bw_hz: float, sr: int,
                  order: int, max_length_s: float) -> np.ndarray:
    """Patterson-style gammatone impulse response, normalized to unit peak gain."""
    tau = 1.0 / (2.0 * np.pi * bw_hz)
    length_s = min(max_length_s, 6.0 * tau * order)
    n = max(int(np.ceil(length_s * sr)), 64)
    t = np.arange(n, dtype=np.float64) / sr
    h = (t ** (order - 1)) * np.exp(-2.0 * np.pi * bw_hz * t) * np.cos(2.0 * np.pi * freq_hz * t)
    peak = np.max(np.abs(np.fft.rfft(h)))
    if peak <= 0.0 or not np.isfinite(peak):
        raise ValueError(f"degenerate filter at {freq_hz:.1f} Hz")
    return h / peak


def _frame_energies(x: np.ndarray, hop: int, window_samples: int) -> np.ndarray:
    n_frames = max(1, (x.size - window_samples) // hop + 1)
    out = np.empty(n_frames, dtype=np.float64)
    for i in range(n_frames):
        start = i * hop
        seg = x[start:start + window_samples]
        out[i] = float(np.mean(seg ** 2)) if seg.size else 0.0
    return out


def compute_er_b_observation(
    samples: np.ndarray,
    sr: int,
    config: ERBConfig | None = None,
) -> ErbObservation:
    """Run the ERB filterbank on one mono signal."""
    config = config or ERBConfig()
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim != 1:
        raise ValueError("MAMSE-013 v0.1 is mono-only; stereo input rejected")

    notes: list[str] = []
    if x.size < config.window_samples:
        notes.append("signal shorter than analysis window")
    if np.all(~np.isfinite(x)):
        raise ValueError("signal contains no finite samples")

    channels = config.center_frequencies()
    energies = np.zeros((config.n_channels, 0), dtype=np.float64)
    powers: list[float] = []
    for freq in channels:
        bw = config.bandwidth_scale * float(erb_bandwidth_hz(freq))
        ir = _gammatone_ir(freq, bw, sr, config.gamma_order, config.max_filter_length_s)
        y = fftconvolve(x, ir, mode="full")[: x.size]
        frames = _frame_energies(y, config.hop_length, config.window_samples)
        powers.append(float(np.mean(frames)))
        energies = np.vstack([energies, frames[None, :]]) if energies.shape[1] else frames[None, :]

    times_s = np.arange(energies.shape[1], dtype=np.float64) * config.hop_length / sr
    total = float(np.sum(powers))
    status = "EMPTY" if total < MIN_ENERGY else "VALID"
    if notes:
        status = "DEGRADED" if status != "EMPTY" else status

    return ErbObservation(
        status=status,
        notes=tuple(notes),
        center_frequencies_hz=channels,
        times_s=times_s,
        channel_energies=energies,
        mean_channel_power=np.asarray(powers, dtype=np.float64),
        sr=sr,
        config_hash=config.sha256(),
    )
