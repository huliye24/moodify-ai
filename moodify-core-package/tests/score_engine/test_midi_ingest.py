"""Tests for MIDI ingest and MoodifyScore model."""

from __future__ import annotations

from pathlib import Path

import pytest

from moodify.score_engine.midi_ingest import MidiParseError, ingest_midi, parse_midi
from moodify.score_engine.model import SCHEMA_VERSION, Event, MoodifyScore, ScoreMetadata, Timeline

from .midi_fixtures import (
    TrackBuilder,
    build_midi,
    empty_track_midi,
    multi_track_midi,
    rest_and_chord_midi,
    single_track_midi,
    tempo_change_midi,
    time_signature_change_midi,
    unicode_track_midi,
)


def write_tmp(tmp_path: Path, data: bytes) -> Path:
    path = tmp_path / "source.mid"
    path.write_bytes(data)
    return path


class TestParseHeader:
    def test_invalid_header_rejected(self, tmp_path: Path) -> None:
        path = write_tmp(tmp_path, b"NOTMIDI" + b"\x00" * 20)
        with pytest.raises(MidiParseError, match="MThd"):
            parse_midi(path)

    def test_truncated_rejected(self, tmp_path: Path) -> None:
        path = write_tmp(tmp_path, b"MThd\x00\x00\x00\x06\x00\x00")
        with pytest.raises(MidiParseError):
            parse_midi(path)

    def test_unsupported_format_rejected(self, tmp_path: Path) -> None:
        path = write_tmp(tmp_path, b"MThd\x00\x00\x00\x06\x00\x02\x00\x01\x01\xe0")
        with pytest.raises(MidiParseError, match="format"):
            parse_midi(path)

    def test_smpte_rejected(self, tmp_path: Path) -> None:
        path = write_tmp(tmp_path, b"MThd\x00\x00\x00\x06\x00\x00\x00\x01\x80\x00")
        with pytest.raises(MidiParseError, match="SMPTE"):
            parse_midi(path)

    def test_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            parse_midi(tmp_path / "nope.mid")


class TestIngest:
    def test_single_track_preserves_raw_ticks(self, tmp_path: Path) -> None:
        score = ingest_midi(write_tmp(tmp_path, single_track_midi()))
        assert score.schema_version == SCHEMA_VERSION
        assert len(score.parts) == 1
        voice = score.parts[0].staves[0].voices[0]
        events = voice.events
        assert len(events) == 3
        assert [e.tick_start for e in events] == [0, 240, 480]
        assert [e.pitch_midi for e in events] == [60, 62, 64]
        assert all(e.event_type == "note" for e in events)
        # raw pitch/tick with inferred measure layout (time signature present)
        assert all(e.source == "midi_ingest" for e in events)
        assert all(e.measure_index is not None for e in events)
        assert all(e.confidence == 0.9 for e in events)

    def test_tempo_and_time_signature_preserved(self, tmp_path: Path) -> None:
        score = ingest_midi(write_tmp(tmp_path, single_track_midi()))
        assert score.timeline.tempo_known
        assert len(score.timeline.tempo_map) == 1
        assert score.timeline.tempo_map[0].bpm == pytest.approx(120.0)
        assert score.timeline.time_signature_known
        assert score.timeline.time_signature_map[0].numerator == 4
        assert score.timeline.time_signature_map[0].denominator == 4
        assert score.timeline.key_known
        assert score.timeline.key_map[0].fifths == 0

    def test_multi_track_parts_and_program(self, tmp_path: Path) -> None:
        score = ingest_midi(write_tmp(tmp_path, multi_track_midi()))
        assert len(score.parts) == 2
        assert score.parts[0].name == "Vocals"
        assert score.parts[0].program == 53
        assert score.parts[0].channel == 0
        assert score.parts[1].name == "Bass"
        assert score.parts[1].program == 33
        assert score.parts[1].channel == 1

    def test_tempo_change_map(self, tmp_path: Path) -> None:
        score = ingest_midi(write_tmp(tmp_path, tempo_change_midi()))
        assert [e.bpm for e in score.timeline.tempo_map] == pytest.approx([100.0, 140.0], rel=1e-4)
        assert [e.tick for e in score.timeline.tempo_map] == [0, 480]

    def test_time_signature_change_map(self, tmp_path: Path) -> None:
        score = ingest_midi(write_tmp(tmp_path, time_signature_change_midi()))
        assert [(e.numerator, e.denominator) for e in score.timeline.time_signature_map] == [
            (4, 4),
            (3, 4),
        ]

    def test_chord_notes_all_preserved(self, tmp_path: Path) -> None:
        score = ingest_midi(write_tmp(tmp_path, rest_and_chord_midi()))
        events = score.parts[0].staves[0].voices[0].events
        pitches = [e.pitch_midi for e in events]
        assert pitches == [60, 64, 67, 72]

    def test_unicode_track_name(self, tmp_path: Path) -> None:
        score = ingest_midi(write_tmp(tmp_path, unicode_track_midi()))
        assert score.parts[0].name == "旋律 メロディー 🎵"

    def test_empty_track_yields_empty_part(self, tmp_path: Path) -> None:
        score = ingest_midi(write_tmp(tmp_path, empty_track_midi()))
        assert len(score.parts) == 1
        assert score.parts[0].staves[0].voices[0].events == ()

    def test_source_sha256_recorded(self, tmp_path: Path) -> None:
        path = write_tmp(tmp_path, single_track_midi())
        score = ingest_midi(path)
        import hashlib

        assert score.source_assets[0].sha256 == hashlib.sha256(path.read_bytes()).hexdigest()
        assert score.source_assets[0].role == "input"
        assert score.source_assets[0].kind == "midi"

    def test_ingest_never_writes_source(self, tmp_path: Path) -> None:
        path = write_tmp(tmp_path, single_track_midi())
        before = path.read_bytes()
        ingest_midi(path)
        assert path.read_bytes() == before

    def test_measure_inference_from_time_signature(self, tmp_path: Path) -> None:
        score = ingest_midi(write_tmp(tmp_path, single_track_midi()))
        events = score.parts[0].staves[0].voices[0].events
        # 4/4 at ppq 480 → measure = 4*480 ticks; notes at 0,240,480 in measure 0
        assert events[0].measure_index == 0
        assert events[0].position_in_measure == 0
        assert events[2].measure_index == 0
        assert events[2].position_in_measure == 480

    def test_no_measure_inference_without_time_signature(self, tmp_path: Path) -> None:
        tb = TrackBuilder()
        tb.track_name(0, "NoSig")
        tb.note(0, 0, 60, 100, 240)
        score = ingest_midi(write_tmp(tmp_path, build_midi([tb])))
        events = score.parts[0].staves[0].voices[0].events
        assert events[0].measure_index is None
        assert events[0].status == "raw"


class TestModelValidation:
    def test_event_duration(self) -> None:
        ev = Event(
            event_id="x",
            event_type="note",
            tick_start=100,
            tick_end=340,
            pitch_midi=60,
        )
        assert ev.duration_ticks() == 240

    def test_rest_event(self) -> None:
        ev = Event(
            event_id="r1",
            event_type="rest",
            tick_start=0,
            tick_end=0,
        )
        assert ev.event_type == "rest"
        assert ev.pitch_midi is None

    def test_score_id_filled_by_serialization(self) -> None:
        from moodify.score_engine.serialization import with_assigned_id

        score = MoodifyScore(
            schema_version=SCHEMA_VERSION,
            score_id="",
            revision=1,
            metadata=ScoreMetadata(),
            source_assets=(),
            timeline=Timeline(),
            parts=(),
        )
        assigned = with_assigned_id(score)
        assert len(assigned.score_id) == 16
