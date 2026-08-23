"""Shared repository-level test fixtures."""

from __future__ import annotations

import numpy as np
import pytest


@pytest.fixture()
def stereo_wav(tmp_path):
    """Create a short generated WAV without adding audio assets to the repo."""
    import soundfile as sf

    sample_rate = 44_100
    seconds = 0.25
    time = np.arange(int(sample_rate * seconds), dtype=np.float32) / sample_rate
    audio = np.column_stack(
        (
            0.2 * np.sin(2 * np.pi * 440 * time),
            0.2 * np.sin(2 * np.pi * 554.37 * time),
        )
    ).astype(np.float32)
    path = tmp_path / "fixture.wav"
    sf.write(path, audio, sample_rate)
    return path
