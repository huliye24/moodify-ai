"""Pairwise service end-to-end tests (real scans, synthetic wavs)."""
from __future__ import annotations

import json
import math
import struct
import wave
from pathlib import Path

import pytest

from moodify.evaluation.pairwise.service import record_human_decision, run_pairwise_judge


def _write_tone(path: Path, seconds: float = 3.0, gain: float = 1.0, rate: int = 48000) -> None:
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        frames = bytearray()
        for i in range(int(rate * seconds)):
            value = int(12000 * gain * math.sin(2 * math.pi * 440 * i / rate))
            value = max(-32768, min(32767, value))
            frames += struct.pack("<h", value)
        wav.writeframes(bytes(frames))


def _write_corrupt(path: Path) -> None:
    path.write_bytes(b"NOT_A_WAV" * 256)


def _ffmpeg_available() -> bool:
    from moodify.auditory.decode import _which_ffmpeg, _which_ffprobe

    try:
        _which_ffmpeg()
        _which_ffprobe()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _ffmpeg_available(), reason="ffmpeg not available")
def test_pairwise_judge_persists_artifacts(tmp_path: Path):
    a = tmp_path / "a.wav"
    b = tmp_path / "b.wav"
    _write_tone(a, gain=1.0)
    _write_tone(b, gain=1.8)  # clipping candidate
    case_root = tmp_path / "cases" / "PW-1"
    result = run_pairwise_judge(case_id="PW-1", case_root=case_root, candidate_a_path=a, candidate_b_path=b)

    assert result["outcome"] in {"A_WINS", "B_WINS", "INCONCLUSIVE"}
    assert result["judgment_id"]
    assert (case_root / "06_pairwise" / "judgment.json").is_file()
    assert (case_root / "06_pairwise" / "comparison.json").is_file()
    assert (case_root / "06_pairwise" / "candidates.json").is_file()
    assert (case_root / "06_pairwise" / "policy.json").is_file()
    judgment = json.loads((case_root / "06_pairwise" / "judgment.json").read_text(encoding="utf-8"))
    assert judgment["policy_version"] == "pairwise_policy_v1"
    assert judgment["outcome"] == result["outcome"]


@pytest.mark.skipif(not _ffmpeg_available(), reason="ffmpeg not available")
def test_analysis_failure_abstains_and_keeps_evidence(tmp_path: Path):
    a = tmp_path / "a.wav"
    b = tmp_path / "b.wav"
    _write_tone(a)
    _write_corrupt(b)
    case_root = tmp_path / "cases" / "PW-2"
    result = run_pairwise_judge(case_id="PW-2", case_root=case_root, candidate_a_path=a, candidate_b_path=b)
    assert result["outcome"] == "INCONCLUSIVE"
    assert result["analysis_failed"]
    assert (case_root / "06_pairwise" / "judgment.json").is_file()


def test_human_decision_persists_override(tmp_path: Path):
    case_root = tmp_path / "cases" / "PW-3"
    case_root.mkdir(parents=True)
    (case_root / "06_pairwise").mkdir()
    result = record_human_decision(
        case_root=case_root,
        pairwise_case_id="PW-3",
        decision="CHOOSE_B",
        machine_outcome="A_WINS",
        machine_confidence="HIGH",
        override_reason="listener preference",
    )
    assert result["human_decision"]["decision"] == "CHOOSE_B"
    assert result["preference_record"]["label_source"] == "HUMAN_OVERRIDE"
    assert result["preference_record"]["eligible_for_training"] is True
    assert (case_root / "06_pairwise" / "human_decision.json").is_file()
    prefs = (case_root / "09_learning" / "pairwise_preferences.jsonl").read_text(encoding="utf-8")
    assert "HUMAN_OVERRIDE" in prefs


def test_machine_only_preference_not_eligible(tmp_path: Path):
    from moodify.evaluation.pairwise.service import _append_preference_record
    from moodify.evaluation.pairwise.models import PreferenceRecord

    case_root = tmp_path / "cases" / "PW-4"
    _append_preference_record(
        case_root,
        PreferenceRecord(
            preference_record_id="pref-1", pairwise_case_id="PW-4",
            preferred_candidate="A", label_source="MACHINE_ONLY",
            machine_outcome="A_WINS", machine_confidence="HIGH",
            eligible_for_training=False,
        ),
    )
    prefs = (case_root / "09_learning" / "pairwise_preferences.jsonl").read_text(encoding="utf-8")
    assert "MACHINE_ONLY" in prefs


def test_missing_candidate_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        run_pairwise_judge(
            case_id="PW-5", case_root=tmp_path / "cases",
            candidate_a_path=tmp_path / "missing.wav",
            candidate_b_path=tmp_path / "missing2.wav",
        )
