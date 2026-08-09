"""N-track service end-to-end tests (real scans, synthetic wavs)."""

from __future__ import annotations

import json
import math
import struct
import wave
from pathlib import Path

import pytest

from moodify.evaluation.ntrack.service import record_human_ranking, run_ntrack_ranking


def _write_tone(path: Path, seconds: float = 2.0, gain: float = 1.0,
                freq: float = 440.0, rate: int = 48000, noise: float = 0.0) -> None:
    import random
    rng = random.Random(7)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        frames = bytearray()
        for i in range(int(rate * seconds)):
            value = 12000 * gain * math.sin(2 * math.pi * freq * i / rate)
            if noise > 0:
                value += (rng.random() - 0.5) * 2.0 * noise * 12000
            value = max(-32768, min(32767, int(value)))
            frames += struct.pack("<h", value)
        wav.writeframes(bytes(frames))


def _write_corrupt(path: Path) -> None:
    path.write_bytes(b"NOT_A_WAV" * 128)


def _ffmpeg_available() -> bool:
    from moodify.auditory.decode import _which_ffmpeg, _which_ffprobe

    try:
        _which_ffmpeg()
        _which_ffprobe()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _ffmpeg_available(), reason="ffmpeg not available")
def test_ntrack_ranking_orders_and_persists(tmp_path: Path):
    tracks = []
    for i in range(5):
        p = tmp_path / f"t{i}.wav"
        _write_tone(p, gain=0.3 + 0.1 * i, freq=350.0 + i * 50, noise=0.003)
        tracks.append(p)
    case_root = tmp_path / "cases" / "RK-1"
    result = run_ntrack_ranking("RK-1", case_root, tracks, top_k=3)

    assert result["eligible_count"] == 5
    assert result["failed_count"] == 0
    assert len(result["ranking"]) == 5
    assert result["ranking"][0]["top_k_membership"] is True
    assert result["ranking"][3]["top_k_membership"] is False
    ntrack = case_root / "05_ntrack"
    for name in ("ranking_case.json", "candidates.json", "quality_gate.json",
                 "edges.json", "estimate.json", "policy.json"):
        assert (ntrack / name).is_file()
    estimate = json.loads((ntrack / "estimate.json").read_text(encoding="utf-8"))
    assert estimate["model_version"] == "ntrack_elo_v1"


@pytest.mark.skipif(not _ffmpeg_available(), reason="ffmpeg not available")
def test_ntrack_analysis_cached_per_hash(tmp_path: Path, monkeypatch):
    from moodify.evaluation.ntrack import service as ntrack_service

    tracks = []
    for i in range(3):
        p = tmp_path / f"t{i}.wav"
        _write_tone(p, gain=0.3 + 0.1 * i, freq=400.0 + i * 40, noise=0.003)
        tracks.append(p)
    case_root = tmp_path / "cases" / "RK-CACHE"
    calls = {"count": 0}
    original = ntrack_service.scan_audio

    def counted_scan(*args, **kwargs):
        calls["count"] += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(ntrack_service, "scan_audio", counted_scan)
    first = run_ntrack_ranking("RK-CACHE", case_root, tracks)
    first_calls = calls["count"]
    second = run_ntrack_ranking("RK-CACHE", case_root, tracks)
    assert first_calls == 3  # each unique track scanned once
    assert calls["count"] == first_calls  # cached on second run
    assert first["ranking_estimate_id"] != second["ranking_estimate_id"]


@pytest.mark.skipif(not _ffmpeg_available(), reason="ffmpeg not available")
def test_partial_failure_isolated(tmp_path: Path):
    tracks = []
    for i in range(4):
        p = tmp_path / f"t{i}.wav"
        if i == 2:
            _write_corrupt(p)
        else:
            _write_tone(p, gain=0.3 + 0.1 * i, freq=350.0 + i * 40, noise=0.003)
        tracks.append(p)
    result = run_ntrack_ranking("RK-2", tmp_path / "cases" / "RK-2", tracks, top_k=3)
    assert result["failed_count"] == 1
    assert result["eligible_count"] == 3
    assert len(result["ranking"]) == 3


@pytest.mark.skipif(not _ffmpeg_available(), reason="ffmpeg not available")
def test_duplicate_source_rejected(tmp_path: Path):
    a = tmp_path / "a.wav"
    b = tmp_path / "b.wav"
    _write_tone(a, gain=0.4, freq=440.0, noise=0.002)
    b.write_bytes(a.read_bytes())  # identical bytes
    c = tmp_path / "c.wav"
    _write_tone(c, gain=0.5, freq=500.0, noise=0.003)
    result = run_ntrack_ranking("RK-3", tmp_path / "cases" / "RK-3", [a, b, c])
    assert result["eligible_count"] == 2
    assert len(result["rejected_ids"]) == 1


@pytest.mark.skipif(not _ffmpeg_available(), reason="ffmpeg not available")
def test_human_reorder_derives_preferences(tmp_path: Path):
    tracks = []
    for i in range(4):
        p = tmp_path / f"t{i}.wav"
        _write_tone(p, gain=0.3 + 0.1 * i, freq=350.0 + i * 45, noise=0.003)
        tracks.append(p)
    case_root = tmp_path / "cases" / "RK-4"
    result = run_ntrack_ranking("RK-4", case_root, tracks, top_k=3)
    machine_order = [c["candidate_id"] for c in result["ranking"]]
    human_order = list(reversed(machine_order))
    human = record_human_ranking(case_root, "RK-4", human_order, top_k=3)
    assert human["derived_preference_count"] >= 1
    assert (case_root / "05_ntrack" / "human_ranking.json").is_file()
    decision = json.loads((case_root / "05_ntrack" / "human_ranking.json").read_text(encoding="utf-8"))
    assert tuple(decision["machine_order"]) == tuple(machine_order)
    assert tuple(decision["human_order"]) == tuple(human_order)


@pytest.mark.skipif(not _ffmpeg_available(), reason="ffmpeg not available")
def test_album_mode_produces_rerank(tmp_path: Path):
    tracks = []
    for i in range(4):
        p = tmp_path / f"t{i}.wav"
        _write_tone(p, gain=0.35, freq=440.0 + i * 8, noise=0.002)  # near-identical
        tracks.append(p)
    result = run_ntrack_ranking("RK-5", tmp_path / "cases" / "RK-5", tracks,
                                mode="ALBUM_SELECTION", top_k=3)
    assert "album_rerank" in result
    assert len(result["album_rerank"]["selected_candidate_ids"]) == 3
    assert (tmp_path / "cases" / "RK-5" / "05_ntrack" / "album_rerank.json").is_file()


def test_requires_two_tracks(tmp_path: Path):
    p = tmp_path / "only.wav"
    p.write_bytes(b"x")
    with pytest.raises(ValueError):
        run_ntrack_ranking("RK-6", tmp_path, [p])
