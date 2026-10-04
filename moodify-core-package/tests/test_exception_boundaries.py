"""CODE_QUALITY_001 — exception boundaries are narrow, and recoverable stays recoverable.

Two properties are proven for each boundary this task changed:

1. the intended fallback / skip still happens;
2. an **unexpected** failure no longer disappears silently.

Property 2 is the one that matters: several of these tests fail against the
previous ``except Exception: pass`` code, which is the point — they are the
regression guard for silent failure swallowing.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from moodify.memory import history as history_module
from moodify.memory.history import ProcessingHistory


def _record(**overrides) -> dict:
    base = dict(
        diagnosis_vector=[0.5] * 5,
        params={"P01_vocal_presence_gain": 1.0},
        strength_vector={"S": 0.5},
        whs_before=1.0,
        whs_after=1.1,
        eds=10.0,
        proxy_score=0.5,
        emotion_code="GA",
        emotion_name="gentle_awakening",
        user_intent="test",
        satisfied=None,
        user_feedback="",
        timestamp="2026-10-04T00:00:00Z",
    )
    base.update(overrides)
    return base


# ── tolerant parser: skip still works ─────────────────────────────────────


def test_history_skips_malformed_lines_but_keeps_valid_ones(tmp_path: Path):
    """Property 1 — one bad line must not cost us the readable ones."""
    path = tmp_path / "processing_history.jsonl"
    path.write_text(
        json.dumps(_record()) + "\n"
        + "{ this is not json\n"
        + json.dumps({"unexpected": "shape"}) + "\n"
        + json.dumps(_record(emotion_code="DR")) + "\n",
        encoding="utf-8",
    )
    records = ProcessingHistory(str(tmp_path)).load_all()
    assert [r.emotion_code for r in records] == ["GA", "DR"]


def test_history_does_not_swallow_unexpected_errors(tmp_path: Path, monkeypatch):
    """Property 2 — an unexpected failure must surface.

    ``RuntimeError`` is not in the narrowed catch set. Against the previous
    ``except Exception: pass`` this returned ``[]`` and the failure vanished.
    """
    path = tmp_path / "processing_history.jsonl"
    path.write_text(json.dumps(_record()) + "\n", encoding="utf-8")

    class Boom(RuntimeError):
        pass

    def explode(**_kwargs):
        raise Boom("programming error, not bad data")

    monkeypatch.setattr(history_module, "ProcessingRecord", explode)
    with pytest.raises(Boom):
        ProcessingHistory(str(tmp_path)).load_all()


# ── audio I/O: the decoder fallback survives ──────────────────────────────


def test_load_audio_raises_for_undecodable_input(tmp_path: Path):
    """Neither decoder succeeds: the caller gets an exception, never a silent empty result."""
    from moodify.audio_io import load_audio

    junk = tmp_path / "junk.wav"
    junk.write_bytes(b"this is not audio")
    with pytest.raises(Exception):
        load_audio(str(junk))


def _ffmpeg_available() -> bool:
    try:
        from moodify.auditory.decode import _which_ffmpeg

        _which_ffmpeg()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _ffmpeg_available(), reason="ffmpeg not available")
def test_m4a_falls_through_to_librosa_instead_of_aborting(tmp_path: Path):
    """§11 — narrowing to ``sf.SoundFileError`` must not remove the fallback.

    soundfile cannot decode M4A, so this exercises exactly the path the narrow
    catch exists to permit. The assertion is on *where* the error comes from,
    not on whether decoding ultimately succeeds: if the catch were too narrow,
    soundfile's own ``SoundFileError`` would propagate and books the failure as
    a decode failure rather than a missing backend.
    """
    import numpy as np
    import soundfile as sf
    from moodify.auditory.decode import _which_ffmpeg
    from moodify.audio_io import load_audio

    wav = tmp_path / "src.wav"
    t = np.arange(44100) / 44100
    sf.write(str(wav), (0.3 * np.sin(2 * np.pi * 440 * t)).astype(np.float32), 44100)
    m4a = tmp_path / "src.m4a"
    result = subprocess.run(
        [_which_ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-i", str(wav),
         "-c:a", "aac", str(m4a)],
        capture_output=True, text=True,
    )
    if result.returncode != 0 or not m4a.is_file():
        pytest.skip("could not produce an M4A fixture")

    try:
        data, sr = load_audio(str(m4a), always_2d=True)
    except Exception as exc:  # noqa: BLE001 - the point is which layer failed
        assert not isinstance(exc, sf.SoundFileError), (
            "soundfile's failure propagated: the decoder fallback was not attempted"
        )
        pytest.skip(f"no M4A backend in this environment: {type(exc).__name__}")
    assert data.ndim == 2
    assert data.shape[0] > 0
    assert sr > 0


# ── tolerant parser: calibration history ──────────────────────────────────


def test_calibration_history_skips_malformed_lines(tmp_path: Path, monkeypatch):
    """Property 1 for the calibration JSONL reader."""
    from moodify.calibration import server as server_module

    path = tmp_path / "d_history.jsonl"
    path.write_text(
        json.dumps({"d": 1.0}) + "\n"
        + "not json\n"
        + json.dumps({"d": 2.0}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(server_module, "HISTORY_PATH", str(path))
    assert server_module._load_d_history() == [{"d": 1.0}, {"d": 2.0}]
