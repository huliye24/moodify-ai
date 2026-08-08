"""Tests for the MusicXML 4.x partwise exporter."""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from moodify.score_engine.midi_ingest import ingest_midi
from moodify.score_engine.musicxml_exporter import MUSICXML_VERSION, export_musicxml
from moodify.score_engine.serialization import with_assigned_id

from .midi_fixtures import (
    multi_track_midi,
    rest_and_chord_midi,
    single_track_midi,
    tempo_change_midi,
)


def parse_xml(path: Path) -> ET.Element:
    return ET.parse(path).getroot()


def write_tmp(tmp_path: Path, data: bytes) -> Path:
    path = tmp_path / "source.mid"
    path.write_bytes(data)
    return path


class TestExport:
    def test_exports_partwise_v4(self, tmp_path: Path) -> None:
        score = with_assigned_id(ingest_midi(write_tmp(tmp_path, single_track_midi())))
        target = tmp_path / "out.musicxml"
        export_musicxml(score, target)
        root = parse_xml(target)
        assert root.tag == "score-partwise"
        assert root.attrib["version"] == MUSICXML_VERSION

    def test_parts_and_measures(self, tmp_path: Path) -> None:
        score = with_assigned_id(ingest_midi(write_tmp(tmp_path, multi_track_midi())))
        target = tmp_path / "out.musicxml"
        export_musicxml(score, target)
        root = parse_xml(target)
        part_els = root.findall("part")
        assert len(part_els) == 2
        assert part_els[0].attrib["id"] == "P-1"
        assert part_els[1].attrib["id"] == "P-2"
        assert part_els[0].findall("measure")
        assert part_els[1].findall("measure")

    def test_notes_pitch_duration(self, tmp_path: Path) -> None:
        score = with_assigned_id(ingest_midi(write_tmp(tmp_path, single_track_midi())))
        target = tmp_path / "out.musicxml"
        export_musicxml(score, target)
        root = parse_xml(target)
        notes = root.findall(".//note")
        assert len(notes) == 3
        pitches = [(n.findtext("pitch/step"), n.findtext("pitch/octave")) for n in notes]
        assert pitches == [("C", "4"), ("D", "4"), ("E", "4")]
        durations = [n.findtext("duration") for n in notes]
        assert durations == ["240", "240", "240"]

    def test_time_and_tempo_exported(self, tmp_path: Path) -> None:
        score = with_assigned_id(ingest_midi(write_tmp(tmp_path, single_track_midi())))
        target = tmp_path / "out.musicxml"
        export_musicxml(score, target)
        root = parse_xml(target)
        first_measure = root.findall("part/measure")[0]
        assert first_measure.findtext("attributes/time/beats") == "4"
        assert first_measure.findtext("attributes/time/beat-type") == "4"
        assert first_measure.findtext("attributes/key/fifths") == "0"
        assert first_measure.findtext("attributes/key/mode") == "major"
        assert first_measure.find(".//sound") is not None
        assert first_measure.find(".//sound").attrib["tempo"] == "120.00"

    def test_tempo_change_visible_in_musicxml(self, tmp_path: Path) -> None:
        score = with_assigned_id(ingest_midi(write_tmp(tmp_path, tempo_change_midi())))
        target = tmp_path / "out.musicxml"
        export_musicxml(score, target)
        root = parse_xml(target)
        sounds = root.findall(".//sound")
        assert sounds, "no tempo directions exported"
        assert sounds[0].attrib["tempo"] == "100.00"

    def test_chord_notes_and_gap_preserved(self, tmp_path: Path) -> None:
        score = with_assigned_id(ingest_midi(write_tmp(tmp_path, rest_and_chord_midi())))
        target = tmp_path / "out.musicxml"
        export_musicxml(score, target)
        root = parse_xml(target)
        # 4/4 at ppq 480 → 1920 ticks per measure; all four notes land in measure 0
        measure_0 = root.findall("part/measure")[0]
        assert len(measure_0.findall("note")) == 4
        # the 720-tick gap is preserved as position within the measure
        voice = score.parts[0].staves[0].voices[0]
        assert [e.position_in_measure for e in voice.events] == [0, 0, 0, 720]

    def test_refuses_overwrite(self, tmp_path: Path) -> None:
        score = with_assigned_id(ingest_midi(write_tmp(tmp_path, single_track_midi())))
        target = tmp_path / "out.musicxml"
        target.write_bytes(b"existing")
        with pytest.raises(FileExistsError):
            export_musicxml(score, target)

    def test_export_leaves_source_untouched(self, tmp_path: Path) -> None:
        source = write_tmp(tmp_path, single_track_midi())
        before = source.read_bytes()
        score = with_assigned_id(ingest_midi(source))
        export_musicxml(score, tmp_path / "out.musicxml")
        assert source.read_bytes() == before

    def test_velocity_exported_when_present(self, tmp_path: Path) -> None:
        score = with_assigned_id(ingest_midi(write_tmp(tmp_path, single_track_midi())))
        target = tmp_path / "out.musicxml"
        export_musicxml(score, target)
        root = parse_xml(target)
        velocities = [n.findtext("velocity") for n in root.findall(".//note")]
        assert velocities == ["100", "90", "80"]


class TestTie:
    def _tied_score(self, tmp_path: Path):
        from moodify.score_engine.model import (
            Event,
            Part,
            ScoreMetadata,
            SourceAsset,
            Staff,
            Timeline,
            Voice,
            MoodifyScore,
        )

        return MoodifyScore(
            schema_version="moodifyscore/0.1",
            score_id="tie-test",
            revision=1,
            metadata=ScoreMetadata(title="Tie Test"),
            source_assets=(SourceAsset(kind="midi", path="synthetic", sha256="0" * 64, role="fixture"),),
            timeline=Timeline(tempo_known=False, time_signature_known=False, key_known=False),
            parts=(
                Part(
                    part_id="P-1",
                    name="Melody",
                    staves=(
                        Staff(
                            staff_id="s1",
                            voices=(
                                Voice(
                                    voice_id="v1",
                                    events=(
                                        Event(
                                            event_id="n1",
                                            event_type="note",
                                            tick_start=0,
                                            tick_end=240,
                                            pitch_midi=60,
                                            ties=("n2",),
                                        ),
                                        Event(
                                            event_id="n2",
                                            event_type="note",
                                            tick_start=240,
                                            tick_end=480,
                                            pitch_midi=60,
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        )

    def test_tie_start_and_stop(self, tmp_path: Path) -> None:
        score = self._tied_score(tmp_path)
        target = tmp_path / "tie.musicxml"
        export_musicxml(score, target)
        root = parse_xml(target)
        ties = root.findall(".//note/tie")
        assert len(ties) == 2
        assert ties[0].attrib["type"] == "start"
        assert ties[1].attrib["type"] == "stop"
