"""Deterministic synthetic fixtures for the Wave Field suite.

No copyrighted material; every asset is generated at test time and kept small
(4-6 s, 48 kHz stereo) so the suite stays fast while still exercising the
loudness / stereo measurement paths.
"""

from __future__ import annotations

import json

import numpy as np
import pytest
import soundfile as sf

SR = 48000


def synth_stereo(seconds: float = 6.0, sample_rate: int = SR) -> np.ndarray:
    """Two detuned partials with a slow amplitude envelope — enough structure
    for crest factor, stereo correlation and spectral descriptors to be
    meaningful."""
    n = int(sample_rate * seconds)
    t = np.arange(n) / sample_rate
    env = 0.55 + 0.45 * np.sin(2 * np.pi * 0.25 * t)
    left = 0.34 * env * np.sin(2 * np.pi * 220.0 * t)
    right = 0.30 * env * np.sin(2 * np.pi * 330.0 * t)
    return np.stack([left, right], axis=1).astype(np.float32)


def synth_mono(seconds: float = 3.0, sample_rate: int = SR) -> np.ndarray:
    n = int(sample_rate * seconds)
    t = np.arange(n) / sample_rate
    return (0.30 * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)


@pytest.fixture
def source_wav(tmp_path):
    path = tmp_path / "source.wav"
    sf.write(str(path), synth_stereo(), SR, subtype="FLOAT")
    return path


@pytest.fixture
def mono_wav(tmp_path):
    path = tmp_path / "mono.wav"
    sf.write(str(path), synth_mono(), SR, subtype="FLOAT")
    return path


@pytest.fixture
def case_dir(tmp_path):
    """A minimal Studio case: the lane mounts under ``<case>/studio/wavefield``."""
    case = tmp_path / "case_wavefield_test"
    case.mkdir()
    (case / "case.json").write_text(
        json.dumps({"case_id": "case_wavefield_test"}), encoding="utf-8"
    )
    return case
