"""ffprobe/ffmpeg subprocess output must decode as UTF-8 regardless of locale.

Regression: on a Chinese-locale Windows host (GBK ANSI codepage) the default
``text=True`` decoding crashed the reader thread for any file whose name or
metadata carries non-ASCII bytes — ffprobe echoes the filename back in its
``-show_format`` JSON. stdout then came back ``None`` and ``probe`` died with
``TypeError``. Every real user music library hit this; ASCII-named test
fixtures never could.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

pytestmark = pytest.mark.v01


def _write_named_wav(tmp_path: Path, name: str) -> Path:
    sr = 8000
    t = np.linspace(0.0, 0.25, sr // 4, endpoint=False)
    samples = (0.2 * np.sin(2 * np.pi * 440.0 * t)).astype("float32")
    path = tmp_path / name
    sf.write(path, samples, sr)
    return path


def test_probe_survives_non_ascii_filename(tmp_path):
    from moodify.auditory.decode import probe

    path = _write_named_wav(tmp_path, "北极星与黑夜.wav")
    file_probe = probe(path)
    assert file_probe.filename == "北极星与黑夜.wav"
    assert file_probe.duration_seconds == pytest.approx(0.25, abs=0.05)


def test_decode_survives_non_ascii_filename(tmp_path):
    from moodify.auditory.decode import decode

    path = _write_named_wav(tmp_path, "唯有痛苦从不说谎.wav")
    decoded = decode(path, 8000)
    assert decoded.samples.shape[0] > 0


def test_spectrogram_renders_non_ascii_filename(tmp_path):
    from moodify.auditory.profiles import MFY_WSE_SCAN_PROFILE_001
    from moodify.auditory.spectrogram import generate_spectrogram

    path = _write_named_wav(tmp_path, "我想被偏爱，不想被路过.wav")
    out = tmp_path / "spec.png"
    run = generate_spectrogram(path, out, MFY_WSE_SCAN_PROFILE_001, "logarithmic")
    assert run.return_code == 0
    assert out.is_file() and out.stat().st_size > 0
