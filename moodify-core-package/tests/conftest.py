"""Shared test fixtures."""
import numpy as np
import pytest


@pytest.fixture
def mock_audio():
    """Generate a 10-second test stereo signal at 44100 Hz."""
    sr = 44100
    t = np.arange(sr * 10) / sr
    left = 0.3 * np.sin(2 * np.pi * 440 * t)   # A4
    right = 0.3 * np.sin(2 * np.pi * 554 * t)   # C#5
    return np.stack([left, right], axis=1).astype(np.float32), sr


@pytest.fixture
def mock_wav(tmp_path, mock_audio):
    """Write mock audio to a temporary WAV file."""
    import soundfile as sf
    audio, sr = mock_audio
    path = tmp_path / "test.wav"
    sf.write(str(path), audio, sr)
    return str(path)
