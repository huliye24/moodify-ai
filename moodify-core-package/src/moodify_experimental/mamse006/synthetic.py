"""Synthetic fixtures for MAMSE-006 tests and demos (seeded, reproducible)."""

from __future__ import annotations

import numpy as np


def harmonic_broadband(duration_s: float, sr: int, seed: int = 7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    t = np.arange(int(duration_s * sr)) / sr
    freqs = np.geomspace(80, min(12000, sr / 2 - 500), 80)
    phases = rng.uniform(0, 2 * np.pi, size=freqs.size)
    amps = 1 / np.sqrt(freqs)
    x = np.sum(amps[:, None] * np.sin(2 * np.pi * freqs[:, None] * t + phases[:, None]), axis=0)
    x /= np.max(np.abs(x)) + 1e-12
    return 0.35 * x


def am_signal(duration_s: float, sr: int, modulation_hz: float, depth: float = 0.8, seed: int = 7) -> np.ndarray:
    t = np.arange(int(duration_s * sr)) / sr
    carrier = harmonic_broadband(duration_s, sr, seed)
    env = 1.0 + depth * np.sin(2 * np.pi * modulation_hz * t)
    y = carrier * env
    y /= np.max(np.abs(y)) + 1e-12
    return 0.5 * y


def ripple_surface(n_bands: int, n_frames: int, frame_rate_hz: float, bands_per_octave: float,
                   temporal_hz: float, spectral_cpo: float, direction: int = 1) -> np.ndarray:
    u = np.arange(n_bands) / bands_per_octave
    t = np.arange(n_frames) / frame_rate_hz
    phase = 2 * np.pi * (spectral_cpo * u[:, None] - direction * temporal_hz * t[None, :])
    return 20.0 * np.cos(phase)


def static_ripple_surface(n_bands: int, n_frames: int, bands_per_octave: float, spectral_cpo: float) -> np.ndarray:
    u = np.arange(n_bands) / bands_per_octave
    profile = 20.0 * np.cos(2 * np.pi * spectral_cpo * u)
    return np.repeat(profile[:, None], n_frames, axis=1)
