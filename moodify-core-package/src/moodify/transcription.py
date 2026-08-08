"""Audio-to-MIDI transcription with a replaceable model backend."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Any, Protocol


class TranscriptionError(RuntimeError):
    """Raised when audio transcription cannot be completed."""


@dataclass(frozen=True)
class TranscriptionConfig:
    onset_threshold: float = 0.5
    frame_threshold: float = 0.3
    minimum_note_length_ms: float = 127.7
    minimum_frequency_hz: float | None = None
    maximum_frequency_hz: float | None = None
    multiple_pitch_bends: bool = False
    melodia_trick: bool = True
    midi_tempo: float = 120.0

    def validate(self) -> None:
        for name, value in (("onset_threshold", self.onset_threshold), ("frame_threshold", self.frame_threshold)):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if self.minimum_note_length_ms <= 0:
            raise ValueError("minimum_note_length_ms must be greater than 0")
        if self.midi_tempo <= 0:
            raise ValueError("midi_tempo must be greater than 0")
        if (self.minimum_frequency_hz is not None and self.maximum_frequency_hz is not None
                and self.minimum_frequency_hz >= self.maximum_frequency_hz):
            raise ValueError("minimum_frequency_hz must be below maximum_frequency_hz")


@dataclass(frozen=True)
class TranscriptionResult:
    input_audio: str
    output_midi: str
    backend: str
    note_count: int
    elapsed_seconds: float
    config: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TranscriptionBackend(Protocol):
    name: str

    def transcribe(self, audio_path: Path, output_path: Path, config: TranscriptionConfig) -> int: ...


class BasicPitchBackend:
    """Spotify Basic Pitch adapter using its selected local model runtime."""

    name = "spotify-basic-pitch"

    def transcribe(self, audio_path: Path, output_path: Path, config: TranscriptionConfig) -> int:
        try:
            from basic_pitch.inference import predict  # type: ignore[import-untyped]
        except ImportError as exc:
            raise TranscriptionError(
                "Basic Pitch is not installed. Run scripts/install_transcription.ps1."
            ) from exc
        try:
            _, midi_data, note_events = predict(
                audio_path,
                onset_threshold=config.onset_threshold,
                frame_threshold=config.frame_threshold,
                minimum_note_length=config.minimum_note_length_ms,
                minimum_frequency=config.minimum_frequency_hz,
                maximum_frequency=config.maximum_frequency_hz,
                multiple_pitch_bends=config.multiple_pitch_bends,
                melodia_trick=config.melodia_trick,
                midi_tempo=config.midi_tempo,
            )
            midi_data.write(str(output_path))
        except Exception as exc:
            raise TranscriptionError(f"Basic Pitch transcription failed: {exc}") from exc
        return len(note_events)


def transcribe_audio(
    audio_path: str | Path,
    output_path: str | Path,
    config: TranscriptionConfig | None = None,
    backend: TranscriptionBackend | None = None,
) -> TranscriptionResult:
    """Transcribe one audio file and write a Standard MIDI File."""
    source = Path(audio_path).expanduser().resolve()
    destination = Path(output_path).expanduser().resolve()
    settings = config or TranscriptionConfig()
    settings.validate()
    if not source.is_file():
        raise FileNotFoundError(f"Audio file not found: {source}")
    if source.suffix.lower() not in {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aif", ".aiff"}:
        raise ValueError(f"Unsupported audio format: {source.suffix or '(none)'}")
    if destination.suffix.lower() not in {".mid", ".midi"}:
        raise ValueError("output_path must end in .mid or .midi")
    destination.parent.mkdir(parents=True, exist_ok=True)
    selected_backend = backend or BasicPitchBackend()
    started = perf_counter()
    note_count = selected_backend.transcribe(source, destination, settings)
    elapsed = perf_counter() - started
    if not destination.is_file() or destination.stat().st_size == 0:
        raise TranscriptionError("Backend returned without writing a MIDI file")
    return TranscriptionResult(
        input_audio=str(source), output_midi=str(destination), backend=selected_backend.name,
        note_count=note_count, elapsed_seconds=round(elapsed, 3), config=asdict(settings),
    )
