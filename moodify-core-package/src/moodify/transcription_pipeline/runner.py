"""Stem-aware transcription orchestrator."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from time import perf_counter

from moodify.transcription import (
    BasicPitchBackend,
    TranscriptionBackend,
    TranscriptionConfig,
    TranscriptionError,
    transcribe_audio,
)

from .midi_cleanup import CleanupConfig, cleanup_midi, merge_to_type1
from .profiles import get_profile
from .stems import UNSUPPORTED_KINDS, StemManifest


@dataclass
class PerStemResult:
    stem_kind: str
    source_path: str
    source_hash: str
    backend: str
    backend_model: str = "spotify-basic-pitch-0.4.0"
    backend_runtime: str = "onnx-cpu"
    config: dict = field(default_factory=dict)
    note_count: int = 0
    elapsed_seconds: float = 0.0
    status: str = "pending"
    error: str = ""
    raw_midi_path: str = ""
    raw_midi_hash: str = ""
    clean_midi_path: str = ""
    clean_midi_hash: str = ""
    cleanup_diff: dict = field(default_factory=dict)


@dataclass
class StemTranscriptionResult:
    manifest: StemManifest
    output_dir: str
    stems: list[PerStemResult] = field(default_factory=list)
    total_elapsed_seconds: float = 0.0
    status: str = "pending"  # success | partial_success | failed
    merged_midi_path: str = ""
    merged_midi_hash: str = ""

    def to_dict(self) -> dict:
        return {
            "output_dir": self.output_dir,
            "status": self.status,
            "total_elapsed_seconds": self.total_elapsed_seconds,
            "merged_midi_path": self.merged_midi_path,
            "merged_midi_hash": self.merged_midi_hash,
            "stems": [asdict(s) for s in self.stems],
        }


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transcribe_stems(
    manifest: StemManifest,
    output_dir: str | Path,
    backend: TranscriptionBackend | None = None,
    config_overrides: dict | None = None,
) -> StemTranscriptionResult:
    """Transcribe multiple stems with per-stem profiles and failure isolation."""
    manifest.validate()
    out = Path(output_dir).resolve()
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(f"Output directory is not empty: {out}")
    raw_dir = out / "raw"
    clean_dir = out / "clean"
    per_stem_dir = out / "per_stem"
    raw_dir.mkdir(parents=True, exist_ok=True)
    clean_dir.mkdir(parents=True, exist_ok=True)
    per_stem_dir.mkdir(parents=True, exist_ok=True)

    selected_backend = backend or BasicPitchBackend()
    overrides = config_overrides or {}
    result = StemTranscriptionResult(
        manifest=manifest, output_dir=str(out), stems=[], status="success",
    )
    t_start = perf_counter()
    any_failure = False
    unsupported_count = 0

    for entry in manifest.stems:
        stem_result = PerStemResult(
            stem_kind=entry.kind.value,
            source_path=str(entry.path),
            source_hash=_hash_file(entry.path),
            backend=selected_backend.name,
            backend_model=getattr(selected_backend, "model_name", selected_backend.name),
            backend_runtime=getattr(selected_backend, "runtime_name", "unknown"),
        )

        if entry.kind in UNSUPPORTED_KINDS:
            stem_result.status = "unsupported"
            stem_result.error = f"{entry.kind.value} transcription is not supported"
            unsupported_count += 1
            result.stems.append(stem_result)
            (per_stem_dir / f"{entry.kind.value}.json").write_text(
                json.dumps(asdict(stem_result), indent=2), encoding="utf-8",
            )
            continue

        profile = get_profile(entry.kind)
        config = TranscriptionConfig(
            onset_threshold=overrides.get("onset_threshold", profile.onset_threshold),
            frame_threshold=overrides.get("frame_threshold", profile.frame_threshold),
            minimum_note_length_ms=overrides.get("minimum_note_length_ms", profile.minimum_note_length_ms),
            minimum_frequency_hz=overrides.get("minimum_frequency_hz", profile.min_frequency_hz),
            maximum_frequency_hz=overrides.get("maximum_frequency_hz", profile.max_frequency_hz),
            multiple_pitch_bends=overrides.get("multiple_pitch_bends", profile.multiple_pitch_bends),
            melodia_trick=overrides.get("melodia_trick", profile.melodia_trick),
            midi_tempo=overrides.get("midi_tempo", 120.0),
        )
        stem_result.config = asdict(config)

        midi_path = raw_dir / f"{entry.kind.value}.mid"
        t_stem = perf_counter()
        try:
            tr = transcribe_audio(entry.path, midi_path, config=config, backend=selected_backend)
            stem_result.note_count = tr.note_count
            stem_result.elapsed_seconds = round(perf_counter() - t_stem, 3)
            stem_result.status = "success"
            stem_result.raw_midi_path = str(midi_path)
            stem_result.raw_midi_hash = _hash_file(midi_path)
        except (TranscriptionError, FileNotFoundError, ValueError, OSError, RuntimeError) as exc:
            if midi_path.exists():
                midi_path.unlink()
            stem_result.elapsed_seconds = round(perf_counter() - t_stem, 3)
            stem_result.status = "failed"
            stem_result.error = str(exc)
            any_failure = True

        result.stems.append(stem_result)

    clean_paths: dict[str, Path] = {}
    for stem_result in result.stems:
        if stem_result.status != "success":
            continue
        clean_path = clean_dir / f"{stem_result.stem_kind}.mid"
        try:
            diff = cleanup_midi(
                stem_result.raw_midi_path,
                clean_path,
                CleanupConfig(),
            )
            stem_result.clean_midi_path = str(clean_path)
            stem_result.clean_midi_hash = _hash_file(clean_path)
            stem_result.cleanup_diff = asdict(diff)
            clean_paths[stem_result.stem_kind] = clean_path
        except (ValueError, OSError, RuntimeError) as exc:
            stem_result.status = "cleanup_failed"
            stem_result.error = f"MIDI cleanup failed: {exc}"
            any_failure = True
            if clean_path.exists():
                clean_path.unlink()

    if clean_paths:
        merged_path = out / "merged.mid"
        try:
            merge_to_type1(clean_paths, merged_path, tempo=overrides.get("midi_tempo", 120.0))
            result.merged_midi_path = str(merged_path)
            result.merged_midi_hash = _hash_file(merged_path)
        except (ValueError, OSError, RuntimeError) as exc:
            any_failure = True
            if merged_path.exists():
                merged_path.unlink()
            for stem_result in result.stems:
                if stem_result.status == "success":
                    stem_result.error = f"Merge failed: {exc}"

    for stem_result in result.stems:
        (per_stem_dir / f"{stem_result.stem_kind}.json").write_text(
            json.dumps(asdict(stem_result), indent=2), encoding="utf-8",
        )

    result.total_elapsed_seconds = round(perf_counter() - t_start, 3)

    successful_clean = bool(clean_paths)
    if any_failure and successful_clean:
        result.status = "partial_success"
    elif unsupported_count > 0 and successful_clean:
        result.status = "partial_success"
    elif not successful_clean and not unsupported_count:
        result.status = "failed"
    elif unsupported_count == len(manifest.stems) and not successful_clean:
        result.status = "failed"

    # Write run manifest
    (out / "run_manifest.json").write_text(
        json.dumps(result.to_dict(), indent=2), encoding="utf-8",
    )

    return result
