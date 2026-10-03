"""Shared fixtures for mix_graph tests."""

import numpy as np
import pytest
import soundfile as sf


@pytest.fixture
def stereo_wav(tmp_path):
    """A 3-second stereo WAV with moderate dynamics and nonzero side energy."""
    sr = 44100
    t = np.arange(sr * 3) / sr
    left = 0.35 * np.sin(2 * np.pi * 440 * t) + 0.08 * np.sin(2 * np.pi * 880 * t)
    right = 0.28 * np.sin(2 * np.pi * 554 * t) + 0.08 * np.sin(2 * np.pi * 880 * t)
    audio = np.column_stack([left, right]).astype(np.float32)
    path = tmp_path / "src.wav"
    sf.write(str(path), audio, sr, subtype="PCM_16")
    return path, sr


@pytest.fixture
def mono_wav(tmp_path):
    """A 2-second mono WAV."""
    sr = 44100
    t = np.arange(sr * 2) / sr
    audio = (0.3 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    path = tmp_path / "mono.wav"
    sf.write(str(path), audio, sr, subtype="PCM_16")
    return path, sr


def band_rms_db(audio: np.ndarray, sr: int, low: float, high: float) -> float:
    """RMS energy (dB) of the mono sum within [low, high] Hz."""
    mono = audio if audio.ndim == 1 else audio.mean(axis=1)
    spectrum = np.abs(np.fft.rfft(mono)) ** 2
    freqs = np.fft.rfftfreq(len(mono), 1.0 / sr)
    mask = (freqs >= low) & (freqs <= high)
    power = float(np.mean(spectrum[mask]))
    return float(10 * np.log10(power + 1e-20))
