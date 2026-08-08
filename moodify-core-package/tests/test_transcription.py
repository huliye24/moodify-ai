from pathlib import Path

import pytest

from moodify.transcription import TranscriptionConfig, transcribe_audio


class FakeBackend:
    name = "fake"

    def transcribe(self, audio_path: Path, output_path: Path, config: TranscriptionConfig) -> int:
        output_path.write_bytes(b"MThd")
        return 7


def test_transcribe_audio_uses_replaceable_backend(tmp_path):
    source = tmp_path / "phrase.wav"
    source.write_bytes(b"RIFF")
    result = transcribe_audio(source, tmp_path / "nested" / "phrase.mid", backend=FakeBackend())
    assert result.backend == "fake"
    assert result.note_count == 7
    assert Path(result.output_midi).read_bytes() == b"MThd"


def test_rejects_invalid_threshold(tmp_path):
    source = tmp_path / "phrase.wav"
    source.write_bytes(b"RIFF")
    with pytest.raises(ValueError, match="onset_threshold"):
        transcribe_audio(source, tmp_path / "phrase.mid", TranscriptionConfig(onset_threshold=1.2), FakeBackend())


def test_rejects_non_midi_output(tmp_path):
    source = tmp_path / "phrase.wav"
    source.write_bytes(b"RIFF")
    with pytest.raises(ValueError, match=".mid"):
        transcribe_audio(source, tmp_path / "phrase.wav", backend=FakeBackend())
