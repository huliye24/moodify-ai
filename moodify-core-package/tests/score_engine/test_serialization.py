"""Tests for canonical JSON serialization of MoodifyScore."""

from __future__ import annotations

from pathlib import Path

import pytest

from moodify.score_engine.midi_ingest import ingest_midi
from moodify.score_engine.serialization import (
    dumps,
    loads,
    score_id_from_content,
    with_assigned_id,
)

from .midi_fixtures import multi_track_midi, single_track_midi


def write_tmp(tmp_path: Path, data: bytes) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "source.mid"
    path.write_bytes(data)
    return path


class TestDeterminism:
    def test_double_run_same_bytes(self, tmp_path: Path) -> None:
        source = write_tmp(tmp_path, multi_track_midi())
        s1 = with_assigned_id(ingest_midi(source))
        s2 = with_assigned_id(ingest_midi(source))
        assert dumps(s1) == dumps(s2)
        assert s1.score_id == s2.score_id

    def test_different_input_different_id(self, tmp_path: Path) -> None:
        p1 = write_tmp(tmp_path / "a", single_track_midi())
        p2 = write_tmp(tmp_path / "b", multi_track_midi())
        id1 = with_assigned_id(ingest_midi(p1)).score_id
        id2 = with_assigned_id(ingest_midi(p2)).score_id
        assert id1 != id2

    def test_score_id_stable_across_reload(self, tmp_path: Path) -> None:
        source = write_tmp(tmp_path, single_track_midi())
        original = with_assigned_id(ingest_midi(source))
        reloaded = with_assigned_id(loads(dumps(original)))
        assert reloaded.score_id == original.score_id
        assert dumps(reloaded) == dumps(original)

    def test_canonical_no_timestamps_or_abs_paths(self, tmp_path: Path) -> None:
        source = write_tmp(tmp_path, single_track_midi())
        text = dumps(with_assigned_id(ingest_midi(source)))
        assert "2026-" not in text
        assert "tmp_path" not in text


class TestStrictParse:
    def test_unknown_top_level_key_rejected(self) -> None:
        raw = (
            '{"schema_version":"moodifyscore/0.1","score_id":"","revision":1,'
            '"metadata":{},"source_assets":[],"timeline":{},"parts":[],'
            '"lyrics_references":[],"evidence":{},"surprise_field":1}'
        )
        with pytest.raises(ValueError, match="surprise_field"):
            loads(raw)

    def test_unknown_event_key_rejected(self, tmp_path: Path) -> None:
        source = write_tmp(tmp_path, single_track_midi())
        canonical = dumps(with_assigned_id(ingest_midi(source)))
        data = loads(canonical)
        parts = list(data.parts)
        part = parts[0]
        staves = list(part.staves)
        staff = staves[0]
        voices = list(staff.voices)
        voice = voices[0]
        events = list(voice.events)
        first = events[0]
        bad = {
            "event_id": first.event_id,
            "event_type": first.event_type,
            "tick_start": first.tick_start,
            "tick_end": first.tick_end,
            "pitch_midi": first.pitch_midi,
            "velocity": first.velocity,
            "duration_ticks": first.duration_ticks(),
            "measure_index": first.measure_index,
            "position_in_measure": first.position_in_measure,
            "ties": list(first.ties),
            "source": first.source,
            "status": first.status,
            "confidence": first.confidence,
            "inference_notes": list(first.inference_notes),
            "bogus": 1,
        }
        from moodify.score_engine.serialization import _parse_event

        with pytest.raises(ValueError, match="bogus"):
            _parse_event(bad)

    def test_unsupported_schema_version_rejected(self) -> None:
        with pytest.raises(ValueError, match="schema_version"):
            loads('{"schema_version":"moodifyscore/9.9","score_id":"","revision":1,'
                  '"metadata":{},"source_assets":[],"timeline":{},"parts":[],'
                  '"lyrics_references":[],"evidence":{}}')

    def test_roundtrip_loads_preserves_content(self, tmp_path: Path) -> None:
        source = write_tmp(tmp_path, multi_track_midi())
        original = with_assigned_id(ingest_midi(source))
        restored = loads(dumps(original))
        assert restored.schema_version == original.schema_version
        assert restored.revision == original.revision
        assert restored.timeline == original.timeline
        assert len(restored.parts) == len(original.parts)
        assert restored.source_assets[0].sha256 == original.source_assets[0].sha256


class TestScoreId:
    def test_id_is_16_hex(self, tmp_path: Path) -> None:
        source = write_tmp(tmp_path, single_track_midi())
        score = with_assigned_id(ingest_midi(source))
        assert len(score.score_id) == 16
        int(score.score_id, 16)

    def test_id_from_content(self, tmp_path: Path) -> None:
        source = write_tmp(tmp_path, single_track_midi())
        score = ingest_midi(source)
        assert score_id_from_content(score) == score_id_from_content(ingest_midi(source))
