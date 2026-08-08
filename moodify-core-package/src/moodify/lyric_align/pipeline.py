from __future__ import annotations

import inspect
import json
import subprocess
from hashlib import sha256
from pathlib import Path
from statistics import median

from moodify.lyric_align.audio import (
    detect_active_intervals,
    ffprobe_duration,
    normalize_audio,
    separate_vocals_demucs,
)
from moodify.lyric_align.backends import HeuristicBackend, WhisperXBackend
from moodify.lyric_align.config import AlignConfig
from moodify.lyric_align.exporters import write_outputs
from moodify.lyric_align.lyrics import clean_lyrics_file
from moodify.lyric_align.models import AlignmentResult
from moodify.lyric_align.quality import apply_rerun_delta, evaluate


def file_sha256(path: str | Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(payload: dict[str, object]) -> str:
    """Canonical JSON hash: sorted keys, stable separators — reproducible across reruns."""
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return sha256(raw).hexdigest()


def _run_backend(
    backend_name: str,
    normalized: Path,
    lyric_lines: list[str],
    language: str,
    audio_duration: float,
    active_intervals: list[tuple[float, float]],
    translations: list[str] | None,
    device: str,
) -> AlignmentResult:
    if backend_name == "heuristic":
        backend = HeuristicBackend()
    elif backend_name == "whisperx":
        backend = WhisperXBackend(device=device)
    else:
        raise ValueError(f"Unknown backend: {backend_name}")
    return backend.align(
        normalized,
        lyric_lines,
        language,
        audio_duration,
        active_intervals,
        translations,
    )


def _median_boundary_delta(first: AlignmentResult, second: AlignmentResult) -> float:
    deltas: list[float] = []
    for left, right in zip(first.lines, second.lines):
        deltas.append(abs(left.start - right.start))
        deltas.append(abs(left.end - right.end))
    return median(deltas) if deltas else 0.0


def run_alignment(
    audio_path: str | Path,
    lyrics_path: str | Path,
    output_dir: str | Path,
    language: str,
    backend_name: str,
    translation_path: str | Path | None = None,
    separate_vocals: str = "auto",
    device: str = "cpu",
    config_path: str | Path | None = None,
    granularity: str | None = None,
) -> dict[str, object]:
    config = AlignConfig.from_file(config_path) if config_path else AlignConfig()
    if separate_vocals == "auto":
        separate_vocals = config.separate_vocals
    audio = Path(audio_path).resolve()
    lyrics = Path(lyrics_path).resolve()
    output = Path(output_dir).resolve()
    work = output / "evidence"
    work.mkdir(parents=True, exist_ok=True)

    lyric_lines = clean_lyrics_file(lyrics)
    translations = clean_lyrics_file(translation_path) if translation_path else None
    if translations is not None and len(translations) != len(lyric_lines):
        raise ValueError(
            f"Translation line count {len(translations)} does not match lyric line count {len(lyric_lines)}."
        )

    original_duration = ffprobe_duration(audio)
    analysis_source = audio
    separation_warning: str | None = None
    if separate_vocals in {"auto", "always"}:
        try:
            analysis_source = separate_vocals_demucs(audio, work, model=config.demucs_model)
        except (RuntimeError, FileNotFoundError, ModuleNotFoundError, subprocess.CalledProcessError) as exc:
            if separate_vocals == "always":
                raise
            separation_warning = f"Vocal separation skipped: {exc}"
            analysis_source = audio

    normalized = normalize_audio(analysis_source, work / "analysis_16k_mono.wav", sample_rate=config.sample_rate)
    active_intervals = detect_active_intervals(
        normalized,
        frame_ms=config.active_frame_ms,
        hop_ms=config.active_hop_ms,
        threshold_ratio=config.active_threshold_ratio,
        merge_gap_seconds=config.merge_gap_seconds,
        min_active_seconds=config.min_active_seconds,
    )
    (work / "active_intervals.json").write_text(
        json.dumps(active_intervals, indent=2), encoding="utf-8"
    )

    result = _run_backend(
        backend_name, normalized, lyric_lines, language,
        original_duration, active_intervals, translations, device,
    )
    if separation_warning:
        result = type(result)(
            backend=result.backend,
            backend_version=result.backend_version,
            language=result.language,
            audio_path=result.audio_path,
            audio_duration=result.audio_duration,
            status=result.status,
            lines=result.lines,
            warnings=result.warnings + (separation_warning,),
            provenance=result.provenance,
        )
    rerun = _run_backend(
        backend_name, normalized, lyric_lines, language,
        original_duration, active_intervals, translations, device,
    )
    rerun_delta_ms = _median_boundary_delta(result, rerun) * 1000.0

    quality = evaluate(result, gate=config.publish_gate, active_intervals=active_intervals)
    quality = apply_rerun_delta(quality, rerun_delta_ms, config.publish_gate)

    (work / "backend_raw.json").write_text(
        json.dumps(result.provenance, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_outputs(result, quality, output)

    backend_cls = HeuristicBackend if backend_name == "heuristic" else WhisperXBackend
    backend_module = Path(inspect.getfile(backend_cls))
    manifest = {
        "audio_sha256": file_sha256(audio),
        "lyrics_sha256": file_sha256(lyrics),
        "translation_sha256": file_sha256(translation_path) if translation_path else None,
        "score_sha256": None,
        "midi_sha256": None,
        "backend": result.backend,
        "backend_version": result.backend_version,
        "backend_sha256": file_sha256(backend_module),
        "backend_raw_sha256": file_sha256(work / "backend_raw.json"),
        "config_sha256": canonical_sha256(json.loads(config.model_dump_json())),
        "alignment_sha256": canonical_sha256(
            json.loads((output / "alignment.json").read_text(encoding="utf-8"))
        ),
        "granularity": granularity,
        "rerun_delta_ms": quality.rerun_delta_ms,
        "status": quality.status,
        "output_dir": str(output),
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest
