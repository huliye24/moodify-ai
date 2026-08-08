"""End-to-end pipeline test (heuristic backend, real ffmpeg normalize).

Skipped when ffmpeg is not available on the machine.
"""
from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

import pytest

from moodify.lyric_align.pipeline import run_alignment


def _ffmpeg_available() -> bool:
    from moodify.lyric_align.audio import require_command

    try:
        require_command("ffmpeg")
        require_command("ffprobe")
        return True
    except RuntimeError:
        return False


def _write_tone_wav(path: Path, seconds: float = 2.0, rate: int = 16_000) -> None:
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        frames = bytearray()
        for i in range(int(rate * seconds)):
            value = int(12000 * math.sin(2 * math.pi * 440 * i / rate))
            frames += struct.pack("<h", value)
        wav.writeframes(bytes(frames))


@pytest.mark.skipif(not _ffmpeg_available(), reason="ffmpeg/ffprobe not available")
def test_heuristic_e2e_pipeline(tmp_path: Path) -> None:
    audio = tmp_path / "tone.wav"
    lyrics = tmp_path / "lyrics.txt"
    out = tmp_path / "align_out"
    _write_tone_wav(audio, seconds=2.0)
    lyrics.write_text("première ligne\nseconde ligne\n", encoding="utf-8")

    manifest = run_alignment(
        audio_path=audio,
        lyrics_path=lyrics,
        output_dir=out,
        language="fr",
        backend_name="heuristic",
        separate_vocals="never",
    )

    assert manifest["backend"] == "heuristic"
    assert manifest["status"] == "DRAFT_ONLY"
    assert manifest["rerun_delta_ms"] == 0.0
    assert manifest["alignment_sha256"]
    assert manifest["backend_sha256"]
    assert manifest["backend_raw_sha256"]
    assert manifest["config_sha256"]
    assert manifest["score_sha256"] is None
    assert manifest["midi_sha256"] is None

    for name in (
        "alignment.json",
        "qc_report.json",
        "manifest.json",
        "lyrics.lrc",
        "lyrics.enhanced.lrc",
        "lyrics.srt",
        "lyrics.ass",
    ):
        assert (out / name).is_file(), f"missing {name}"
    assert (out / "evidence" / "analysis_16k_mono.wav").is_file()
    assert (out / "evidence" / "active_intervals.json").is_file()
    assert (out / "evidence" / "backend_raw.json").is_file()

    import json

    qc = json.loads((out / "qc_report.json").read_text(encoding="utf-8"))
    assert qc["status"] == "DRAFT_ONLY"
    assert qc["word_monotonicity_violations"] == 0
    assert qc["boundary_jumps"] == 0
    assert qc["rerun_delta_ms"] == 0.0
