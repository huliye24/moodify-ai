"""Deterministic synthetic fixtures for reconstruction job tests (MFY-CR-P08).

All assets generated at test time; nothing committed as binary. The signal
layout mirrors the era_diagnostic clean_stereo recipe (multi-tone, silence
gaps for noise-floor checks, quiet noise bed) so P03 findings are realistic.
"""

from __future__ import annotations

import numpy as np
import pytest
import scipy.signal as sig
import soundfile as sf

SR = 48000
DURATION_S = 2.0
RNG_SEED = 20260817

_TONE_FREQS = (220.0, 440.0, 880.0, 1760.0, 3520.0, 7040.0, 10000.0, 14080.0)
_TONE_AMPS = (0.15, 0.15, 0.15, 0.15, 0.15, 0.10, 0.10, 0.05)
_SILENCE = ((0.0, 0.3), (1.2, 1.4), (1.8, 2.0))


def _clean_signal() -> np.ndarray:
    rng = np.random.default_rng(RNG_SEED)
    n = int(SR * DURATION_S)
    t = np.arange(n) / SR
    left = np.zeros(n, dtype=np.float64)
    for f, a in zip(_TONE_FREQS, _TONE_AMPS):
        left += a * np.sin(2 * np.pi * f * t)
    left += 0.01 * rng.standard_normal(n)
    for start, end in _SILENCE:
        lo, hi = int(start * SR), int(end * SR)
        left[lo:hi] = 0.0
    right = 0.95 * left
    music = np.ones(n, dtype=bool)
    for start, end in _SILENCE:
        music[int(start * SR):int(end * SR)] = False
    right[music] += 0.06 * rng.standard_normal(int(music.sum()))
    return np.stack([left, right], axis=1)


def _lowpass(x: np.ndarray, cutoff_hz: float) -> np.ndarray:
    sos = sig.butter(4, cutoff_hz / (SR / 2), btype="low", output="sos")
    y = np.zeros_like(x)
    for ch in range(x.shape[1]):
        y[:, ch] = sig.sosfiltfilt(sos, x[:, ch])
    return y


@pytest.fixture
def clean_fullband_wav(tmp_path):
    """Full-band stereo with silence gaps: no bandwidth limitation."""
    audio = _clean_signal().astype(np.float32)
    path = tmp_path / "clean.wav"
    sf.write(str(path), audio, SR)
    return path


@pytest.fixture
def lowpass_wav(tmp_path):
    """9 kHz lowpass (P03-validated strong ED-01): authorises candidates."""
    audio = _lowpass(_clean_signal(), 9000.0).astype(np.float32)
    path = tmp_path / "lowpass.wav"
    sf.write(str(path), audio, SR)
    return path


@pytest.fixture
def empty_store(tmp_path):
    from moodify.reconstruction_job.store import JobStore
    return JobStore(tmp_path / "jobs.db", lease_seconds=3600)


@pytest.fixture
def engine_config(tmp_path):
    from moodify.reconstruction_job.engine import EngineConfig
    return EngineConfig(workspace_root=tmp_path / "workspace")
