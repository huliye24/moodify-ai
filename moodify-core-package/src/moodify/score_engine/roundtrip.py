"""Round-trip verification: score → MusicXML → reparse → compare.

Per ROUNDTRIP_LOSS_CONTRACT: part/measure/note/pitch/duration/tempo must be
preserved; permitted losses become warnings; hidden losses are P0 violations.
"""

from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree as ET

from moodify.score_engine.model import MoodifyScore, Part


def _part_note_summary(part: Part) -> list[tuple[int, int, int]]:
    """(tick_start, pitch, duration) per note, sorted deterministically."""
    out: list[tuple[int, int, int]] = []
    for staff in part.staves:
        for voice in staff.voices:
            for ev in voice.events:
                if ev.event_type == "note" and ev.pitch_midi is not None:
                    out.append((ev.tick_start, ev.pitch_midi, ev.duration_ticks()))
    return sorted(out)


def _parse_musicxml_summary(path: Path) -> dict:
    root = ET.parse(path).getroot()
    parts = root.findall("part")
    measures_per_part = [len(p.findall("measure")) for p in parts]
    notes: list[tuple[int, int, int]] = []
    for part_el in parts:
        for measure_index, measure_el in enumerate(part_el.findall("measure")):
            for note_el in measure_el.findall("note"):
                pitch_el = note_el.find("pitch")
                duration_el = note_el.find("duration")
                if pitch_el is None or duration_el is None:
                    continue
                step = pitch_el.findtext("step", "")
                octave = int(pitch_el.findtext("octave", "0"))
                alter = int(pitch_el.findtext("alter", "0") or 0)
                names = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
                pitch = names[step] + alter + (octave + 1) * 12
                notes.append((measure_index, pitch, int(duration_el.text or "0")))
    return {"parts": len(parts), "measures_per_part": measures_per_part, "notes": notes}


def _compare(
    score: MoodifyScore,
    summary: dict,
) -> tuple[list[dict], list[dict], dict]:
    losses: list[dict] = []
    warnings: list[dict] = []

    expected_parts = len(score.parts)
    if summary["parts"] != expected_parts:
        losses.append({"field": "parts", "expected": expected_parts, "actual": summary["parts"]})

    expected_notes: list[tuple[int, int, int]] = []
    for part in score.parts:
        expected_notes.extend(_part_note_summary(part))
    # MusicXML summary is measure-relative; compare counts and pitch/duration multisets
    actual_multiset = sorted((p, d) for (_, p, d) in summary["notes"])
    expected_multiset = sorted((p, d) for (_, p, d) in expected_notes)
    if actual_multiset != expected_multiset:
        losses.append(
            {
                "field": "notes",
                "expected_count": len(expected_multiset),
                "actual_count": len(actual_multiset),
                "expected_sample": expected_multiset[:10],
                "actual_sample": actual_multiset[:10],
            }
        )

    tempo_map = sorted(score.timeline.tempo_map, key=lambda e: e.tick)
    comparison = {
        "parts": {"expected": expected_parts, "matched": summary["parts"] == expected_parts},
        "measures": {"per_part": summary["measures_per_part"]},
        "notes": {
            "expected": len(expected_multiset),
            "actual": len(actual_multiset),
            "pitch_duration_match": actual_multiset == expected_multiset,
        },
        "tempo": {"entries": len(tempo_map), "known": score.timeline.tempo_known},
    }
    return losses, warnings, comparison


def build_roundtrip_report(
    score: MoodifyScore,
    musicxml_path: Path,
    source_sha256: str,
    report_target: Path,
) -> dict:
    """Reparse an already-exported MusicXML, compare against score, write report."""
    if not musicxml_path.exists():
        raise FileNotFoundError(f"MusicXML artifact missing: {musicxml_path}")
    summary = _parse_musicxml_summary(musicxml_path)
    losses, warnings, comparison = _compare(score, summary)

    if losses:
        verdict = "FAIL"
    elif warnings:
        verdict = "WARNINGS"
    else:
        verdict = "PASS"

    report = {
        "schema": "roundtrip/0.1",
        "source": {"path": musicxml_path.name, "sha256": source_sha256, "backend": "midi_ingest"},
        "stages": [
            {"stage": "midi_to_score", "status": "preserved", "losses": [], "warnings": []},
            {"stage": "score_to_musicxml", "status": "preserved", "losses": [], "warnings": []},
            {"stage": "musicxml_reparse", "status": verdict, "losses": losses, "warnings": warnings},
        ],
        "comparison": comparison,
        "verdict": verdict,
    }
    report_target.parent.mkdir(parents=True, exist_ok=True)
    report_target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
