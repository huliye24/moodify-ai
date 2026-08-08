from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import uuid

from .models import AuditoryObservation
from .note_evidence import annotate_note_evidence
from .provenance import canonical_json_hash, sha256_file
from .quality_gate import evaluate_report


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalise_timeline(report: dict[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []

    for segment in report.get("segments") or []:
        events.append(
            {
                "event_type": "energy_segment",
                "start_s": segment.get("start"),
                "end_s": segment.get("end"),
                "payload": segment,
                "source": "ocean.structure",
            }
        )

    for stem, spans in (report.get("stemTimeline") or {}).items():
        for span in spans or []:
            start, end = span if isinstance(span, list) and len(span) >= 2 else (None, None)
            events.append(
                {
                    "event_type": "stem_activity",
                    "start_s": start,
                    "end_s": end,
                    "payload": {"stem": stem},
                    "source": "ocean.stems",
                }
            )

    lyrics = report.get("lyrics") or {}
    if isinstance(lyrics, dict):
        for segment in lyrics.get("segments") or []:
            events.append(
                {
                    "event_type": "lyric_segment",
                    "start_s": segment.get("start"),
                    "end_s": segment.get("end"),
                    "payload": {
                        "text": segment.get("text"),
                        "language": lyrics.get("language"),
                        "source": lyrics.get("source"),
                    },
                    "source": "ocean.lyrics",
                }
            )

    for segment in report.get("voiceSegments") or []:
        events.append(
            {
                "event_type": "voice_texture_segment",
                "start_s": segment.get("start"),
                "end_s": segment.get("end"),
                "payload": segment,
                "source": "ocean.voice",
                "status": "experimental",
            }
        )

    for window in report.get("phraseDynamics") or []:
        events.append(
            {
                "event_type": "phrase_dynamics",
                "start_s": window.get("start"),
                "end_s": window.get("end"),
                "payload": window,
                "source": "ocean.dynamics",
            }
        )

    def sort_key(event: dict[str, Any]) -> tuple[float, str]:
        start = event.get("start_s")
        return (
            float(start) if isinstance(start, (int, float)) else float("inf"),
            str(event.get("event_type", "")),
        )

    return sorted(events, key=sort_key)


def map_ocean_report(
    report: dict[str, Any],
    *,
    source_audio: str | Path,
    run_id: str,
    upstream_commit: str | None,
    module_manifest: dict[str, Any] | None = None,
    raw_report_path: str | Path | None = None,
    deep_expected: bool = False,
) -> dict[str, Any]:
    source_path = Path(source_audio)
    if not source_path.is_file():
        raise FileNotFoundError(f"Source audio does not exist: {source_path}")

    source_hash = sha256_file(source_path)
    report_hash = canonical_json_hash(report)
    observation_id = str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            f"moodify:ocean:{source_hash}:{report_hash}:{upstream_commit or 'unknown'}",
        )
    )

    gate = evaluate_report(report, deep_expected=deep_expected)

    classification = dict(report.get("classification") or {})
    if classification:
        classification["status"] = "observed"
        classification["authority"] = "sensor_only"

    notes = annotate_note_evidence(list(report.get("notes") or []))

    stem_notes: dict[str, list[dict[str, Any]]] = {}
    for stem, stem_note_list in (report.get("stemNotes") or {}).items():
        annotated = annotate_note_evidence(list(stem_note_list or []))
        for note in annotated:
            note.setdefault("stem", stem)
        stem_notes[stem] = annotated

    artifacts: list[dict[str, Any]] = []
    if raw_report_path is not None and Path(raw_report_path).is_file():
        artifacts.append(
            {
                "artifact_type": "raw_ocean_report",
                "path": str(Path(raw_report_path)),
                "sha256": sha256_file(raw_report_path),
                "media_type": "application/json",
                "role": "source_evidence",
            }
        )

    spectrogram = report.get("spectrogram")
    if spectrogram and Path(spectrogram).is_file():
        artifacts.append(
            {
                "artifact_type": "spectrogram",
                "path": str(Path(spectrogram)),
                "sha256": sha256_file(spectrogram),
                "media_type": "image/png",
                "role": "visual_evidence",
            }
        )

    observation = AuditoryObservation(
        schema_version="moodify.auditory-observation/1.0",
        observation_id=observation_id,
        run_id=run_id,
        created_at=_now_iso(),
        source={
            "path": str(source_path.resolve()),
            "sha256": source_hash,
            "size_bytes": source_path.stat().st_size,
            "name": report.get("name") or source_path.stem,
            "duration_s": report.get("duration"),
        },
        analyzer={
            "name": "Ocean Listen",
            "adapter": "moodify-ocean-bridge",
            "upstream_commit": upstream_commit,
            "shallow_version": report.get("shallowVersion"),
            "deep_version": report.get("deepVersion"),
        },
        classification=classification,
        global_features={
            "bpm": report.get("bpm"),
            "key": report.get("key"),
            "brightness_trend": report.get("brightnessTrend"),
            "percussive_ratio": report.get("percussiveRatio"),
            "vocal_coverage": report.get("vocalCoverage"),
            "energy_segments": report.get("segments") or [],
            "chroma_by_segment": report.get("chromaBySegment") or [],
            "instruments": report.get("instruments") or {},
        },
        stems={
            "activity_timeline": report.get("stemTimeline") or {},
            "notes": stem_notes,
            "total_stem_notes": report.get("totalStemNotes"),
            "unified_timeline": report.get("unifiedTimeline") or [],
            "harmonic_filter_stats": (
                report.get("harmonicFilterStats")
                or report.get("filterStats")
                or {}
            ),
        },
        notes=notes,
        voice={
            "profile": report.get("voiceProfile") or {},
            "f0": report.get("f0Data") or {},
            "vibrato": report.get("vibrato") or {},
            "segments": report.get("voiceSegments") or [],
            "timbre": report.get("voiceTimbre") or {},
            "texture": report.get("voiceTexture") or {},
            "speech": report.get("speechAnalysis") or {},
            "vocal_parts": report.get("vocalParts") or [],
            "status": "experimental",
        },
        lyrics=report.get("lyrics") or {},
        timeline=_normalise_timeline(report),
        artifacts=artifacts,
        uncertainty=[
            {
                "code": "SENSOR_NOT_JUDGMENT",
                "message": (
                    "Ocean output is an observation source. It is not a Moodify "
                    "artistic or production judgment."
                ),
            },
            {
                "code": "UPSTREAM_THRESHOLDS_EXPERIMENTAL",
                "message": (
                    "Classifier, vocal segmentation, timbre and harmonic-filter "
                    "thresholds require Moodify benchmark validation."
                ),
            },
            {
                "code": "VELOCITY_NOT_LOUDNESS",
                "message": (
                    "basic-pitch velocity is retained as model confidence proxy; "
                    "RMS-derived dynamics is the acoustic energy evidence."
                ),
            },
        ],
        provenance={
            "raw_report_sha256": report_hash,
            "upstream_module_manifest": module_manifest or {},
        },
        quality_gate=gate.to_dict(),
    )
    return observation.to_dict()


def map_report_file(
    report_path: str | Path,
    *,
    source_audio: str | Path,
    run_id: str,
    upstream_commit: str | None,
    module_manifest: dict[str, Any] | None = None,
    output_path: str | Path | None = None,
    deep_expected: bool = False,
) -> dict[str, Any]:
    path = Path(report_path)
    report = json.loads(path.read_text(encoding="utf-8"))
    mapped = map_ocean_report(
        report,
        source_audio=source_audio,
        run_id=run_id,
        upstream_commit=upstream_commit,
        module_manifest=module_manifest,
        raw_report_path=path,
        deep_expected=deep_expected,
    )
    if output_path is not None:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(mapped, ensure_ascii=False, indent=2, allow_nan=False),
            encoding="utf-8",
        )
    return mapped
