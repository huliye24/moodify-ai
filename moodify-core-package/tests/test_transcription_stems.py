"""Tests for stem-aware transcription pipeline."""
from __future__ import annotations

import json
import struct
from pathlib import Path

import pytest

# pretty_midi is a transcription-extra test dependency (installed in
# .venv-basic-pitch). When absent, tests that need it skip explicitly instead
# of failing collection — optional-capability degradation at the boundary.
pretty_midi = pytest.importorskip("pretty_midi")

from moodify.transcription_pipeline.profiles import PROFILES, StemKind, get_profile
from moodify.transcription_pipeline.stems import (
    TRANSCRIBABLE_KINDS,
    StemEntry,
    StemManifest,
)


class TestStemKind:
    def test_enum_values(self) -> None:
        assert {k.value for k in StemKind} == {
            "vocals", "bass", "piano", "guitar", "other", "drums", "unknown",
        }

    def test_transcribable_kinds(self) -> None:
        assert StemKind.VOCALS in TRANSCRIBABLE_KINDS
        assert StemKind.BASS in TRANSCRIBABLE_KINDS
        assert StemKind.PIANO in TRANSCRIBABLE_KINDS
        assert StemKind.GUITAR in TRANSCRIBABLE_KINDS
        assert StemKind.OTHER in TRANSCRIBABLE_KINDS
        assert StemKind.DRUMS not in TRANSCRIBABLE_KINDS
        assert StemKind.UNKNOWN not in TRANSCRIBABLE_KINDS

    def test_reject_unknown_kind(self) -> None:
        with pytest.raises(ValueError):
            StemKind("nonexistent")


class TestStemManifest:
    def test_validate_duplicate_kinds(self) -> None:
        m = StemManifest(stems=[
            StemEntry(kind=StemKind.VOCALS, path=Path("/tmp/a.wav")),
            StemEntry(kind=StemKind.VOCALS, path=Path("/tmp/b.wav")),
        ])
        with pytest.raises(ValueError, match="Duplicate"):
            m.validate()

    def test_empty_manifest_rejected(self) -> None:
        with pytest.raises(ValueError, match="at least one"):
            StemManifest().validate()

    def test_from_cli_pairs(self) -> None:
        m = StemManifest.from_cli_pairs([("vocals", "/tmp/v.wav")])
        assert len(m.stems) == 1
        assert m.stems[0].kind == StemKind.VOCALS

    def test_from_cli_pairs_reject_unknown(self) -> None:
        with pytest.raises(ValueError, match="Unknown stem kind"):
            StemManifest.from_cli_pairs([("flute", "/tmp/f.wav")])

    def test_path_traversal_rejected(self) -> None:
        entry = StemEntry(kind=StemKind.VOCALS, path=Path("../etc/passwd"))
        with pytest.raises(ValueError, match="Path traversal"):
            entry.validate()

    def test_missing_file_rejected(self) -> None:
        entry = StemEntry(kind=StemKind.VOCALS, path=Path("/nonexistent/file.wav"))
        with pytest.raises(FileNotFoundError):
            entry.validate()


class TestProfiles:
    def test_all_transcribable_kinds_have_profile(self) -> None:
        for kind in TRANSCRIBABLE_KINDS:
            assert kind in PROFILES, f"Missing profile for {kind}"

    def test_profile_values_are_reasonable(self) -> None:
        vocals = get_profile(StemKind.VOCALS)
        assert vocals.min_frequency_hz == 80.0
        assert vocals.max_frequency_hz == 1200.0
        assert vocals.multiple_pitch_bends is True

        bass = get_profile(StemKind.BASS)
        assert bass.min_frequency_hz == 30.0
        assert bass.max_frequency_hz == 500.0

    def test_drums_not_in_profiles(self) -> None:
        assert StemKind.DRUMS not in PROFILES


class TestRunner:
    def test_transcribe_stems_with_fake_backend(self, tmp_path: Path) -> None:
        from moodify.transcription_pipeline.runner import transcribe_stems

        # Create fake WAV files
        v_path = tmp_path / "vocals.wav"
        b_path = tmp_path / "bass.wav"
        v_path.write_bytes(b"RIFF")
        b_path.write_bytes(b"RIFF")

        manifest = StemManifest(stems=[
            StemEntry(kind=StemKind.VOCALS, path=v_path),
            StemEntry(kind=StemKind.BASS, path=b_path),
        ])

        class FakeBackend:
            name = "fake"
            def transcribe(self, audio_path, output_path, config):
                _write_test_midi(output_path)
                return 5

        out = tmp_path / "output"
        result = transcribe_stems(manifest, out, backend=FakeBackend())

        assert result.status == "success"
        assert len(result.stems) == 2
        assert result.stems[0].status == "success"
        assert result.stems[1].status == "success"
        assert (out / "raw" / "vocals.mid").exists()
        assert (out / "raw" / "bass.mid").exists()
        assert (out / "clean" / "vocals.mid").exists()
        assert (out / "clean" / "bass.mid").exists()
        assert (out / "merged.mid").exists()
        assert (out / "run_manifest.json").exists()

        manifest_data = json.loads((out / "run_manifest.json").read_text())
        assert manifest_data["status"] == "success"

    def test_drums_stem_skipped(self, tmp_path: Path) -> None:
        from moodify.transcription_pipeline.runner import transcribe_stems

        v_path = tmp_path / "vocals.wav"
        v_path.write_bytes(b"RIFF")
        manifest = StemManifest(stems=[
            StemEntry(kind=StemKind.VOCALS, path=v_path),
            StemEntry(kind=StemKind.DRUMS, path=v_path),
        ])

        class FakeBackend:
            name = "fake"
            def transcribe(self, audio_path, output_path, config):
                _write_test_midi(output_path)
                return 3

        result = transcribe_stems(manifest, tmp_path / "out", backend=FakeBackend())
        assert result.status == "partial_success"  # drums skipped = partial
        assert result.stems[1].status == "unsupported"
        evidence = json.loads((tmp_path / "out" / "per_stem" / "drums.json").read_text())
        assert evidence["status"] == "unsupported"

    def test_single_stem_failure_isolated(self, tmp_path: Path) -> None:
        from moodify.transcription_pipeline.runner import transcribe_stems

        v_path = tmp_path / "vocals.wav"
        b_path = tmp_path / "bass.wav"
        v_path.write_bytes(b"RIFF")
        b_path.write_bytes(b"RIFF")

        manifest = StemManifest(stems=[
            StemEntry(kind=StemKind.VOCALS, path=v_path),
            StemEntry(kind=StemKind.BASS, path=b_path),
        ])

        class PartialBackend:
            name = "partial"
            def transcribe(self, audio_path, output_path, config):
                if "bass" in str(audio_path):
                    raise RuntimeError("Bass failed")
                _write_test_midi(output_path)
                return 3

        result = transcribe_stems(manifest, tmp_path / "out", backend=PartialBackend())
        assert result.status == "partial_success"
        assert result.stems[0].status == "success"
        assert result.stems[1].status == "failed"
        assert (tmp_path / "out" / "raw" / "vocals.mid").exists()
        assert not (tmp_path / "out" / "raw" / "bass.mid").exists()

    def test_library_rejects_nonempty_output(self, tmp_path: Path) -> None:
        from moodify.transcription_pipeline.runner import transcribe_stems

        source = tmp_path / "vocals.wav"
        source.write_bytes(b"RIFF")
        out = tmp_path / "out"
        out.mkdir()
        sentinel = out / "keep.txt"
        sentinel.write_text("user data")
        manifest = StemManifest(stems=[StemEntry(StemKind.VOCALS, source)])

        with pytest.raises(FileExistsError):
            transcribe_stems(manifest, out, backend=object())
        assert sentinel.read_text() == "user data"


def _write_test_midi(path: Path, *, pitch: int = 60, bends: bool = False) -> None:
    midi = pretty_midi.PrettyMIDI(initial_tempo=120)
    inst = pretty_midi.Instrument(program=0)
    inst.notes.append(pretty_midi.Note(velocity=90, pitch=pitch, start=0.13, end=1.13))
    if bends:
        inst.pitch_bends.append(pretty_midi.PitchBend(pitch=1024, time=0.5))
        inst.control_changes.append(pretty_midi.ControlChange(number=64, value=127, time=0.4))
    midi.instruments.append(inst)
    midi.write(str(path))


class TestMidiCleanup:
    def test_default_cleanup_preserves_note_timing_and_raw(self, tmp_path: Path) -> None:
        from moodify.transcription_pipeline.midi_cleanup import cleanup_midi

        raw = tmp_path / "raw.mid"
        clean = tmp_path / "clean.mid"
        _write_test_midi(raw)
        before = raw.read_bytes()
        diff = cleanup_midi(raw, clean)

        assert raw.read_bytes() == before
        note = pretty_midi.PrettyMIDI(str(clean)).instruments[0].notes[0]
        assert note.start == pytest.approx(0.13, abs=0.002)
        assert note.end == pytest.approx(1.13, abs=0.002)
        assert diff.quantized_notes == 0
        assert diff.key_corrected_notes == 0

    def test_cleanup_cannot_overwrite_raw_or_existing_output(self, tmp_path: Path) -> None:
        from moodify.transcription_pipeline.midi_cleanup import cleanup_midi

        raw = tmp_path / "raw.mid"
        _write_test_midi(raw)
        with pytest.raises(ValueError):
            cleanup_midi(raw, raw)
        existing = tmp_path / "existing.mid"
        existing.write_bytes(b"keep")
        with pytest.raises(FileExistsError):
            cleanup_midi(raw, existing)
        assert existing.read_bytes() == b"keep"

    def test_default_cleanup_is_event_idempotent(self, tmp_path: Path) -> None:
        from moodify.transcription_pipeline.midi_cleanup import cleanup_midi

        raw = tmp_path / "raw.mid"
        clean1 = tmp_path / "clean1.mid"
        clean2 = tmp_path / "clean2.mid"
        _write_test_midi(raw)
        cleanup_midi(raw, clean1)
        cleanup_midi(clean1, clean2)

        def events(path: Path) -> list[tuple[int, float, float, int]]:
            midi = pretty_midi.PrettyMIDI(str(path))
            return [
                (note.pitch, round(note.start, 6), round(note.end, 6), note.velocity)
                for inst in midi.instruments
                for note in inst.notes
            ]

        assert events(clean1) == events(clean2)

    def test_quantization_is_explicit_and_preserves_duration(self, tmp_path: Path) -> None:
        from moodify.transcription_pipeline.midi_cleanup import CleanupConfig, cleanup_midi

        raw = tmp_path / "raw.mid"
        clean = tmp_path / "clean.mid"
        _write_test_midi(raw)
        cleanup_midi(raw, clean, CleanupConfig(quantize_grid="1/8"))
        note = pretty_midi.PrettyMIDI(str(clean)).instruments[0].notes[0]
        assert note.start == pytest.approx(0.25, abs=0.002)
        assert note.end - note.start == pytest.approx(1.0, abs=0.002)

    def test_merge_is_type1_and_preserves_expression(self, tmp_path: Path) -> None:
        from moodify.transcription_pipeline.midi_cleanup import merge_to_type1

        vocals = tmp_path / "vocals.mid"
        bass = tmp_path / "bass.mid"
        merged = tmp_path / "merged.mid"
        _write_test_midi(vocals, bends=True)
        _write_test_midi(bass, pitch=40)
        merge_to_type1({"vocals": vocals, "bass": bass}, merged)

        header = merged.read_bytes()[:14]
        assert header[:4] == b"MThd"
        assert struct.unpack(">H", header[8:10])[0] == 1
        result = pretty_midi.PrettyMIDI(str(merged))
        assert [inst.name for inst in result.instruments] == ["vocals", "bass"]
        assert result.instruments[0].pitch_bends
        assert result.instruments[0].control_changes
