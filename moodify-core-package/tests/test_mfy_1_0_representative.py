"""Deterministic Moodify 1.0 release-path validation."""

from __future__ import annotations

import hashlib
import json
import math
import struct
import wave
from pathlib import Path

import pytest

from moodify.auditory.decode import _which_ffmpeg, _which_ffprobe
from moodify.contracts import ProductionCase
from moodify.contracts.ids import validate_id
from moodify.release import analyze_to_case, reopen_case


def _tools_available() -> bool:
    try:
        _which_ffmpeg(); _which_ffprobe()
        return True
    except Exception:
        return False


def _write_wav(path: Path, *, gain: float = 0.35, frequency: float = 440.0,
               channels: int = 2, dc: float = 0.0, antiphase: bool = False) -> Path:
    with wave.open(str(path), "wb") as output:
        output.setnchannels(channels); output.setsampwidth(2); output.setframerate(48000)
        frames = bytearray()
        for index in range(48000):
            sample = gain * math.sin(2 * math.pi * frequency * index / 48000)
            for channel in range(channels):
                value = -sample if antiphase and channel == 1 else sample
                frames += struct.pack("<h", max(-32768, min(32767, int((value + dc) * 32767))))
        output.writeframes(frames)
    return path


def fixture_set(root: Path) -> dict[str, Path]:
    return {
        "normal_stereo": _write_wav(root / "normal.wav"),
        "mono": _write_wav(root / "mono.wav", channels=1),
        "clipping": _write_wav(root / "clipping.wav", gain=1.5),
        "dc_offset": _write_wav(root / "dc.wav", dc=0.2),
        "antiphase": _write_wav(root / "antiphase.wav", antiphase=True),
        "band_limited": _write_wav(root / "band_limited.wav", frequency=100.0),
        "loudness_low": _write_wav(root / "quiet.wav", gain=0.1),
        "loudness_high": _write_wav(root / "loud.wav", gain=0.8),
    }


def test_representative_fixture_matrix_is_generated(tmp_path: Path):
    fixtures = fixture_set(tmp_path)
    assert set(fixtures) == {"normal_stereo", "mono", "clipping", "dc_offset",
                             "antiphase", "band_limited", "loudness_low", "loudness_high"}
    assert all(path.stat().st_size > 44 for path in fixtures.values())


@pytest.mark.skipif(not _tools_available(), reason="FFmpeg/ffprobe unavailable")
def test_canonical_path_persists_and_reopens_without_source_mutation(tmp_path: Path):
    source = _write_wav(tmp_path / "owned.wav")
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    result = analyze_to_case(source, tmp_path / "cases")
    case = ProductionCase.model_validate(result["case"])
    validate_id(case.case_id, "case")
    assert case.lifecycle_state == "COMPLETED"
    assert case.authority_state == "HUMAN_REQUIRED"
    assert case.measurement_ids and case.evidence_ids
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    assert reopen_case(tmp_path / "cases", case.case_id) == result

    case_root = tmp_path / "cases" / case.case_id
    evidence = json.loads((case_root / "evidence.json").read_text(encoding="utf-8"))
    assert all(not Path(item.get("logical_path") or "").is_absolute() for item in evidence)
    for item in evidence:
        artifact = case_root / item["logical_path"]
        assert "sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest() == item["content_hash"]


@pytest.mark.skipif(not _tools_available(), reason="FFmpeg/ffprobe unavailable")
def test_corrupt_input_is_failed_not_completed(tmp_path: Path):
    corrupt = tmp_path / "corrupt.wav"; corrupt.write_bytes(b"not audio")
    with pytest.raises(Exception):
        analyze_to_case(corrupt, tmp_path / "cases")
    case_files = list((tmp_path / "cases").glob("case_*/case.json"))
    assert len(case_files) == 1
    assert ProductionCase.model_validate_json(
        case_files[0].read_text(encoding="utf-8")
    ).lifecycle_state == "FAILED"
