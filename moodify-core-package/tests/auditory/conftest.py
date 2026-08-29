"""Deterministic synthetic fixtures for auditory scan tests (DSK-MFY-AUDITORY-SCAN-001).

No copyrighted material; all assets are generated at test time.
"""

from __future__ import annotations

import numpy as np
import pytest
import soundfile as sf

SR = 48000


def _write(path, samples, sr=SR):
    sf.write(path, samples, sr)
    return path


@pytest.fixture
def audio_dir(tmp_path):
    return tmp_path


@pytest.fixture
def fx_silence(audio_dir):
    return _write(audio_dir / "silence.wav", np.zeros((SR * 2, 2), dtype=np.float32))


@pytest.fixture
def fx_mono_sine(audio_dir):
    t = np.arange(SR * 2) / SR
    return _write(audio_dir / "mono_sine.wav", 0.3 * np.sin(2 * np.pi * 440 * t).astype(np.float32))


@pytest.fixture
def fx_stereo_sine(audio_dir):
    t = np.arange(SR * 2) / SR
    x = np.stack([0.3 * np.sin(2 * np.pi * 440 * t), 0.3 * np.sin(2 * np.pi * 554 * t)], axis=1)
    return _write(audio_dir / "stereo_sine.wav", x.astype(np.float32))


@pytest.fixture
def fx_clipped(audio_dir):
    t = np.arange(SR * 2) / SR
    x = np.stack([np.clip(1.3 * np.sin(2 * np.pi * 440 * t), -1, 1)] * 2, axis=1)
    return _write(audio_dir / "clipped.wav", x.astype(np.float32))


@pytest.fixture
def fx_dc_offset(audio_dir):
    t = np.arange(SR * 2) / SR
    x = np.stack([0.2 * np.sin(2 * np.pi * 440 * t) + 0.05] * 2, axis=1)
    return _write(audio_dir / "dc_offset.wav", x.astype(np.float32))


@pytest.fixture
def fx_low_freq_heavy(audio_dir):
    t = np.arange(SR * 2) / SR
    x = np.stack([0.4 * np.sin(2 * np.pi * 60 * t)] * 2, axis=1)
    return _write(audio_dir / "lf_heavy.wav", x.astype(np.float32))


@pytest.fixture
def fx_high_freq_heavy(audio_dir):
    t = np.arange(SR * 2) / SR
    x = np.stack([0.3 * np.sin(2 * np.pi * 8000 * t)] * 2, axis=1)
    return _write(audio_dir / "hf_heavy.wav", x.astype(np.float32))


@pytest.fixture
def fx_band_limited(audio_dir):
    t = np.arange(SR * 2) / SR
    # 200-3000 Hz band: sum of a few sine components
    x = sum(0.1 * np.sin(2 * np.pi * f * t) for f in (200, 500, 1000, 2000, 3000))
    return _write(audio_dir / "band_limited.wav", np.stack([x, x], axis=1).astype(np.float32))


@pytest.fixture
def fx_antiphase(audio_dir):
    t = np.arange(SR * 2) / SR
    x = 0.3 * np.sin(2 * np.pi * 440 * t)
    return _write(audio_dir / "antiphase.wav", np.stack([x, -x], axis=1).astype(np.float32))


@pytest.fixture
def fx_compressed(audio_dir):
    t = np.arange(SR * 2) / SR
    x = 0.3 * np.sin(2 * np.pi * 440 * t)
    y = np.tanh(x * 2.0)
    return _write(audio_dir / "compressed.wav", np.stack([y, y], axis=1).astype(np.float32))


@pytest.fixture
def fx_loudness_gain(audio_dir):
    """Loudness-only gain change: same signal, +3 dB."""
    t = np.arange(SR * 2) / SR
    x = np.stack([0.3 * np.sin(2 * np.pi * 440 * t), 0.3 * np.sin(2 * np.pi * 554 * t)], axis=1)
    return _write(audio_dir / "loudness_gain.wav", (x * 1.41).astype(np.float32))


@pytest.fixture
def fx_eq_change(audio_dir):
    """EQ-like change: source + brightened high band (low-passed boost)."""
    t = np.arange(SR * 2) / SR
    base = 0.3 * np.sin(2 * np.pi * 440 * t)
    bright = 0.25 * np.sin(2 * np.pi * 8000 * t)
    return _write(audio_dir / "eq_change.wav", np.stack([base + bright] * 2, axis=1).astype(np.float32))


@pytest.fixture
def fx_duration_mismatch(audio_dir):
    t = np.arange(int(SR * 2.5)) / SR
    x = np.stack([0.3 * np.sin(2 * np.pi * 440 * t)] * 2, axis=1)
    return _write(audio_dir / "duration_mismatch.wav", x.astype(np.float32))


@pytest.fixture
def fx_corrupt(audio_dir):
    p = audio_dir / "corrupt.wav"
    p.write_bytes(b"this is not a wav file at all" * 100)
    return p
