"""Canonical JSON serialization for MoodifyScore v0.1.

Strict typed schema: unknown top-level keys are rejected. Serialization is
deterministic (sorted keys, no timestamps or absolute paths), so identical
input produces byte-identical canonical JSON across runs.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from moodify.score_engine.model import (
    SCHEMA_VERSION,
    Event,
    KeyEntry,
    MoodifyScore,
    Part,
    ScoreMetadata,
    SourceAsset,
    Staff,
    TempoEntry,
    TimeSignatureEntry,
    Timeline,
    Voice,
)

TOP_LEVEL_KEYS = {
    "schema_version",
    "score_id",
    "revision",
    "revision_note",
    "metadata",
    "source_assets",
    "timeline",
    "parts",
    "lyrics_references",
    "evidence",
}


def _event_to_dict(ev: Event) -> dict[str, Any]:
    return {
        "event_id": ev.event_id,
        "event_type": ev.event_type,
        "tick_start": ev.tick_start,
        "tick_end": ev.tick_end,
        "pitch_midi": ev.pitch_midi,
        "velocity": ev.velocity,
        "duration_ticks": ev.duration_ticks(),
        "measure_index": ev.measure_index,
        "position_in_measure": ev.position_in_measure,
        "ties": list(ev.ties),
        "source": ev.source,
        "status": ev.status,
        "confidence": ev.confidence,
        "inference_notes": list(ev.inference_notes),
    }


def _voice_to_dict(voice: Voice) -> dict[str, Any]:
    return {"voice_id": voice.voice_id, "events": [_event_to_dict(e) for e in voice.events]}


def _staff_to_dict(staff: Staff) -> dict[str, Any]:
    return {"staff_id": staff.staff_id, "clef": staff.clef, "voices": [_voice_to_dict(v) for v in staff.voices]}


def _part_to_dict(part: Part) -> dict[str, Any]:
    return {
        "part_id": part.part_id,
        "name": part.name,
        "instrument": part.instrument,
        "channel": part.channel,
        "program": part.program,
        "source_track": part.source_track,
        "staves": [_staff_to_dict(s) for s in part.staves],
    }


def _metadata_to_dict(md: ScoreMetadata) -> dict[str, Any]:
    return {
        "title": md.title,
        "composer": md.composer,
        "lyrics": md.lyrics,
        "language": md.language,
        "comments": md.comments,
        "source_label": md.source_label,
    }


def _timeline_to_dict(tl: Timeline) -> dict[str, Any]:
    return {
        "tempo_map": [{"tick": e.tick, "bpm": e.bpm} for e in tl.tempo_map],
        "time_signature_map": [{"tick": e.tick, "numerator": e.numerator, "denominator": e.denominator} for e in tl.time_signature_map],
        "key_map": [{"tick": e.tick, "fifths": e.fifths, "mode": e.mode} for e in tl.key_map],
        "tempo_known": tl.tempo_known,
        "time_signature_known": tl.time_signature_known,
        "key_known": tl.key_known,
    }


def _source_asset_to_dict(a: SourceAsset) -> dict[str, Any]:
    return {"kind": a.kind, "path": a.path, "sha256": a.sha256, "role": a.role}


def score_to_dict(score: MoodifyScore) -> dict[str, Any]:
    return {
        "schema_version": score.schema_version,
        "score_id": score.score_id,
        "revision": score.revision,
        "revision_note": score.revision_note,
        "metadata": _metadata_to_dict(score.metadata),
        "source_assets": [_source_asset_to_dict(a) for a in score.source_assets],
        "timeline": _timeline_to_dict(score.timeline),
        "parts": [_part_to_dict(p) for p in score.parts],
        "lyrics_references": list(score.lyrics_references),
        "evidence": score.evidence,
    }


def dumps(score: MoodifyScore) -> str:
    """Canonical JSON: sorted keys, compact separators, deterministic."""
    return json.dumps(score_to_dict(score), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def score_id_from_content(score: MoodifyScore) -> str:
    """Stable content-derived score id (first 16 hex chars of canonical hash)."""
    payload = dumps(score)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def with_assigned_id(score: MoodifyScore) -> MoodifyScore:
    """Return a copy whose score_id is derived from canonical content."""
    if score.score_id:
        return score
    return MoodifyScore(
        schema_version=score.schema_version,
        score_id=score_id_from_content(score),
        revision=score.revision,
        revision_note=score.revision_note,
        metadata=score.metadata,
        source_assets=score.source_assets,
        timeline=score.timeline,
        parts=score.parts,
        lyrics_references=score.lyrics_references,
        evidence=score.evidence,
    )


def _reject_unknown_keys(data: dict[str, Any], allowed: set[str], context: str) -> None:
    unknown = set(data) - allowed
    if unknown:
        raise ValueError(f"unknown field(s) in {context}: {sorted(unknown)}")


def _parse_event(data: dict[str, Any]) -> Event:
    _reject_unknown_keys(
        data,
        {
            "event_id", "event_type", "tick_start", "tick_end", "pitch_midi",
            "velocity", "duration_ticks", "measure_index", "position_in_measure",
            "ties", "source", "status", "confidence", "inference_notes",
        },
        "event",
    )
    return Event(
        event_id=str(data["event_id"]),
        event_type=data["event_type"],
        tick_start=int(data["tick_start"]),
        tick_end=int(data["tick_end"]),
        pitch_midi=data["pitch_midi"],
        velocity=data["velocity"],
        measure_index=data["measure_index"],
        position_in_measure=data["position_in_measure"],
        ties=tuple(data.get("ties", ())),
        source=data.get("source", "unknown"),
        status=data.get("status", "raw"),
        confidence=data.get("confidence"),
        inference_notes=tuple(data.get("inference_notes", ())),
    )


def _parse_voice(data: dict[str, Any]) -> Voice:
    _reject_unknown_keys(data, {"voice_id", "events"}, "voice")
    return Voice(
        voice_id=str(data["voice_id"]),
        events=tuple(_parse_event(e) for e in data.get("events", ())),
    )


def _parse_staff(data: dict[str, Any]) -> Staff:
    _reject_unknown_keys(data, {"staff_id", "clef", "voices"}, "staff")
    return Staff(
        staff_id=str(data["staff_id"]),
        clef=data.get("clef"),
        voices=tuple(_parse_voice(v) for v in data.get("voices", ())),
    )


def _parse_part(data: dict[str, Any]) -> Part:
    _reject_unknown_keys(
        data, {"part_id", "name", "instrument", "channel", "program", "source_track", "staves"}, "part"
    )
    return Part(
        part_id=str(data["part_id"]),
        name=data.get("name", ""),
        instrument=data.get("instrument"),
        channel=data.get("channel"),
        program=data.get("program"),
        source_track=data.get("source_track"),
        staves=tuple(_parse_staff(s) for s in data.get("staves", ())),
    )


def _parse_timeline(data: dict[str, Any]) -> Timeline:
    _reject_unknown_keys(
        data,
        {"tempo_map", "time_signature_map", "key_map", "tempo_known", "time_signature_known", "key_known"},
        "timeline",
    )
    tempos = tuple(
        TempoEntry(tick=int(t["tick"]), bpm=float(t["bpm"])) for t in data.get("tempo_map", ())
    )
    sigs = tuple(
        TimeSignatureEntry(tick=int(s["tick"]), numerator=int(s["numerator"]), denominator=int(s["denominator"]))
        for s in data.get("time_signature_map", ())
    )
    keys = tuple(KeyEntry(tick=int(k["tick"]), fifths=int(k["fifths"]), mode=k["mode"]) for k in data.get("key_map", ()))
    return Timeline(
        tempo_map=tempos,
        time_signature_map=sigs,
        key_map=keys,
        tempo_known=bool(data.get("tempo_known", False)),
        time_signature_known=bool(data.get("time_signature_known", False)),
        key_known=bool(data.get("key_known", False)),
    )


def _parse_metadata(data: dict[str, Any]) -> ScoreMetadata:
    _reject_unknown_keys(
        data, {"title", "composer", "lyrics", "language", "comments", "source_label"}, "metadata"
    )
    return ScoreMetadata(
        title=data.get("title", ""),
        composer=data.get("composer"),
        lyrics=data.get("lyrics"),
        language=data.get("language"),
        comments=data.get("comments"),
        source_label=data.get("source_label"),
    )


def _parse_source_asset(data: dict[str, Any]) -> SourceAsset:
    _reject_unknown_keys(data, {"kind", "path", "sha256", "role"}, "source_asset")
    return SourceAsset(
        kind=str(data.get("kind", "")),
        path=str(data.get("path", "")),
        sha256=str(data.get("sha256", "")),
        role=str(data.get("role", "")),
    )


def from_dict(data: dict[str, Any]) -> MoodifyScore:
    """Strict parse: unknown keys raise; returns a MoodifyScore."""
    _reject_unknown_keys(data, TOP_LEVEL_KEYS, "score")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"unsupported schema_version: {data.get('schema_version')}")
    return MoodifyScore(
        schema_version=str(data["schema_version"]),
        score_id=str(data.get("score_id", "")),
        revision=int(data.get("revision", 1)),
        revision_note=data.get("revision_note", ""),
        metadata=_parse_metadata(data.get("metadata", {})),
        source_assets=tuple(_parse_source_asset(a) for a in data.get("source_assets", ())),
        timeline=_parse_timeline(data.get("timeline", {})),
        parts=tuple(_parse_part(p) for p in data.get("parts", ())),
        lyrics_references=tuple(data.get("lyrics_references", ())),
        evidence=data.get("evidence", {}),
    )


def loads(text: str) -> MoodifyScore:
    return from_dict(json.loads(text))
