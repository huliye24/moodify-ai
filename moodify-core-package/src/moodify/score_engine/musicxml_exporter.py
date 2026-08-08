"""MusicXML 4.x partwise exporter for MoodifyScore.

Exports parts, measures, voices, notes/rests, duration, tie, tempo,
time/key (when known) and lyrics references (when present). MusicXML never
replaces the internal evidence/revision/confidence; unknown structure stays
unknown. The source MIDI is never written by this module.
"""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

from moodify.score_engine.model import Event, MoodifyScore, Part

MUSICXML_VERSION = "4.0"


def _duration_ticks(event: Event) -> int:
    return max(event.duration_ticks(), 1)


def _pitch_to_musicxml(pitch: int) -> tuple[str, str, str]:
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    name = names[pitch % 12]
    step = name[0]
    alter = "1" if "#" in name else "0"
    octave = str(pitch // 12 - 1)
    return step, octave, alter


def _group_events_by_measure(part: Part) -> dict[int, list[tuple[Event, str]]]:
    grouped: dict[int, list[tuple[Event, str]]] = {}
    for staff in part.staves:
        for voice in staff.voices:
            for ev in voice.events:
                key = ev.measure_index if ev.measure_index is not None else 0
                grouped.setdefault(key, []).append((ev, voice.voice_id))
    return grouped


def _append_attributes(measure: ET.Element, measure_index: int, divisions: int, score: MoodifyScore) -> None:
    if measure_index != 0:
        return
    attrs = ET.SubElement(measure, "attributes")
    ET.SubElement(attrs, "divisions").text = str(divisions)
    if score.timeline.time_signature_known and score.timeline.time_signature_map:
        sig = sorted(score.timeline.time_signature_map, key=lambda e: e.tick)[0]
        time_el = ET.SubElement(attrs, "time")
        ET.SubElement(time_el, "beats").text = str(sig.numerator)
        ET.SubElement(time_el, "beat-type").text = str(sig.denominator)
    if score.timeline.key_known and score.timeline.key_map:
        key = sorted(score.timeline.key_map, key=lambda e: e.tick)[0]
        key_el = ET.SubElement(attrs, "key")
        ET.SubElement(key_el, "fifths").text = str(key.fifths)
        ET.SubElement(key_el, "mode").text = key.mode


def _append_note(measure: ET.Element, event: Event, voice_id: str) -> None:
    note_el = ET.SubElement(measure, "note")
    if event.event_type == "rest":
        ET.SubElement(note_el, "rest")
    else:
        if event.pitch_midi is None:
            raise ValueError(f"note event without pitch: {event.event_id}")
        step, octave, alter = _pitch_to_musicxml(event.pitch_midi)
        pitch_el = ET.SubElement(note_el, "pitch")
        ET.SubElement(pitch_el, "step").text = step
        if alter != "0":
            ET.SubElement(pitch_el, "alter").text = alter
        ET.SubElement(pitch_el, "octave").text = octave
        if event.velocity is not None:
            ET.SubElement(note_el, "velocity").text = str(event.velocity)
    ET.SubElement(note_el, "duration").text = str(_duration_ticks(event))
    ET.SubElement(note_el, "voice").text = voice_id.split(":")[-1]
    if event.ties:
        notations = ET.SubElement(note_el, "notations")
        ET.SubElement(notations, "tied", type="start")
        ET.SubElement(note_el, "tie", type="start")


def _append_tempo(measure: ET.Element, bpm: float) -> None:
    direction_el = ET.SubElement(measure, "direction")
    ET.SubElement(direction_el, "direction-type")
    ET.SubElement(direction_el, "sound", tempo=f"{bpm:.2f}")


def _mark_tie_stops(
    part: Part,
    note_by_event: dict[str, ET.Element],
    measure_by_event: dict[str, ET.Element],
) -> None:
    """Add tie 'stop' to the note events referenced by start ties."""
    for staff in part.staves:
        for voice in staff.voices:
            for ev in voice.events:
                if not ev.ties:
                    continue
                target = note_by_event.get(ev.ties[0])
                if target is None:
                    continue
                notations = target.find("notations")
                if notations is None:
                    notations = ET.SubElement(target, "notations")
                ET.SubElement(notations, "tied", type="stop")
                ET.SubElement(target, "tie", type="stop")


def export_musicxml(score: MoodifyScore, target: Path) -> None:
    """Write a partwise MusicXML document to target (never overwrites)."""
    if target.exists():
        raise FileExistsError(f"refusing to overwrite existing file: {target}")

    root = ET.Element("score-partwise", version=MUSICXML_VERSION)
    if score.metadata.title:
        work_el = ET.SubElement(root, "work")
        ET.SubElement(work_el, "work-title").text = score.metadata.title
    part_list_el = ET.SubElement(root, "part-list")
    for part in score.parts:
        score_part_el = ET.SubElement(part_list_el, "score-part", id=part.part_id)
        ET.SubElement(score_part_el, "part-name").text = part.name or part.part_id

    divisions = 480
    for part in score.parts:
        part_el = ET.SubElement(root, "part", id=part.part_id)
        grouped = _group_events_by_measure(part)
        note_by_event: dict[str, ET.Element] = {}
        for measure_index in sorted(grouped):
            measure_el = ET.SubElement(part_el, "measure", number=str(measure_index + 1))
            _append_attributes(measure_el, measure_index, divisions, score)
            if score.timeline.tempo_known and score.timeline.tempo_map and measure_index == 0:
                first_tempo = sorted(score.timeline.tempo_map, key=lambda e: e.tick)[0]
                _append_tempo(measure_el, first_tempo.bpm)
            events = sorted(grouped[measure_index], key=lambda pair: (pair[0].tick_start, pair[0].pitch_midi or 0))
            for ev, voice_id in events:
                _append_note(measure_el, ev, voice_id)
                note_by_event[ev.event_id] = measure_el.findall("note")[-1]
        _mark_tie_stops(part, note_by_event, {})

    ET.ElementTree(root).write(target, encoding="utf-8", xml_declaration=True)
