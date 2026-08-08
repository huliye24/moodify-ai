"""MIDI ingest — parse SMF into MoodifyScore events with full provenance.

Raw tick/time, track/channel/program, tempo and time signature are preserved.
Key/voice/measure that cannot be inferred reliably stay unknown. The source
MIDI is read-only; its SHA-256 is recorded in evidence.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from moodify.score_engine.model import (
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

MIDI_EVENT_DELTA_SYSEX = 0xF0
MIDI_EVENT_SYSEX_CONT = 0xF7
MIDI_EVENT_META = 0xFF
META_TRACK_NAME = 0x03
META_TEMPO = 0x51
META_TIME_SIGNATURE = 0x58
META_KEY_SIGNATURE = 0x59
META_END_OF_TRACK = 0x2F


class MidiParseError(ValueError):
    """Raised when the source file is not a valid/parseable MIDI file."""


@dataclass(frozen=True)
class MidiHeader:
    format: int
    track_count: int
    division: int
    smpte: bool = False


@dataclass
class NoteOn:
    tick: int
    channel: int
    pitch: int
    velocity: int
    tick_end: int | None = None


@dataclass
class MidiTrack:
    index: int
    name: str = ""
    channel: int | None = None
    program: int | None = None
    notes: list[NoteOn] = field(default_factory=list)
    tempo_map: list[TempoEntry] = field(default_factory=list)
    time_signature_map: list[TimeSignatureEntry] = field(default_factory=list)
    key_map: list[KeyEntry] = field(default_factory=list)


@dataclass
class MidiData:
    header: MidiHeader
    tracks: list[MidiTrack]
    tempo_map: list[TempoEntry]
    time_signature_map: list[TimeSignatureEntry]
    key_map: list[KeyEntry]
    ppq: int


def _read_vlq(data: bytes, index: int) -> tuple[int, int]:
    value = 0
    while True:
        if index >= len(data):
            raise MidiParseError("truncated VLQ")
        byte = data[index]
        index += 1
        value = (value << 7) | (byte & 0x7F)
        if byte < 0x80:
            return value, index


def _parse_header(data: bytes) -> tuple[MidiHeader, int]:
    if len(data) < 14 or data[:4] != b"MThd":
        raise MidiParseError("missing MThd header")
    length = int.from_bytes(data[4:8], "big")
    if length < 6:
        raise MidiParseError(f"invalid MThd length {length}")
    fmt = int.from_bytes(data[8:10], "big")
    ntrack = int.from_bytes(data[10:12], "big")
    division = int.from_bytes(data[12:14], "big")
    smpte = bool(division & 0x8000)
    return MidiHeader(format=fmt, track_count=ntrack, division=division, smpte=smpte), 8 + length


def _parse_track(data: bytes, start: int, track_index: int, ppq: int) -> MidiTrack:
    if data[start : start + 4] != b"MTrk":
        raise MidiParseError("missing MTrk")
    length = int.from_bytes(data[start + 4 : start + 8], "big")
    payload = data[start + 8 : start + 8 + length]
    track = MidiTrack(index=track_index)
    cursor = 0
    tick = 0
    running: int | None = None
    active: dict[tuple[int, int], NoteOn] = {}

    while cursor < len(payload):
        delta, cursor = _read_vlq(payload, cursor)
        tick += delta
        if cursor >= len(payload):
            break
        status = payload[cursor]
        if status < 0x80:
            if running is None:
                raise MidiParseError("running status with no prior status byte")
            status = running
        else:
            cursor += 1
            running = status if status < 0xF0 else None

        if status == MIDI_EVENT_META:
            meta_type = payload[cursor]
            cursor += 1
            size, cursor = _read_vlq(payload, cursor)
            body = payload[cursor : cursor + size]
            cursor += size
            if meta_type == META_END_OF_TRACK:
                pass
            elif meta_type == META_TRACK_NAME:
                try:
                    track.name = body.decode("utf-8")
                except UnicodeDecodeError:
                    track.name = body.decode("latin-1", errors="replace")
            elif meta_type == META_TEMPO:
                if len(body) != 3:
                    raise MidiParseError("invalid tempo meta length")
                micros = int.from_bytes(body, "big")
                track.tempo_map.append(TempoEntry(tick=tick, bpm=60_000_000 / micros))
            elif meta_type == META_TIME_SIGNATURE:
                if len(body) < 2:
                    raise MidiParseError("invalid time signature meta length")
                track.time_signature_map.append(
                    TimeSignatureEntry(tick=tick, numerator=body[0], denominator=2 ** body[1])
                )
            elif meta_type == META_KEY_SIGNATURE:
                if len(body) < 2:
                    raise MidiParseError("invalid key signature meta length")
                track.key_map.append(
                    KeyEntry(
                        tick=tick,
                        fifths=int.from_bytes(body[:1], "big", signed=True),
                        mode="major" if body[1] == 0 else "minor",
                    )
                )
        elif status in (MIDI_EVENT_DELTA_SYSEX, MIDI_EVENT_SYSEX_CONT):
            size, cursor = _read_vlq(payload, cursor)
            cursor += size
        else:
            message = status & 0xF0
            channel = status & 0x0F
            if message in (0xC0, 0xD0):
                track.program = payload[cursor]
                track.channel = channel
                cursor += 1
            elif message in (0x90, 0x80):
                if cursor + 2 > len(payload):
                    raise MidiParseError("truncated note event")
                pitch = payload[cursor]
                velocity = payload[cursor + 1]
                cursor += 2
                if message == 0x90 and velocity > 0:
                    note = NoteOn(tick=tick, channel=channel, pitch=pitch, velocity=velocity)
                    active[(channel, pitch)] = note
                    track.channel = channel
                else:
                    if (channel, pitch) in active:
                        note = active.pop((channel, pitch))
                        note.tick_end = tick
                        track.notes.append(note)
            else:
                if cursor + 2 > len(payload):
                    raise MidiParseError("truncated channel event")
                cursor += 2
    return track


def parse_midi(path: Path) -> MidiData:
    """Parse a standard MIDI file; format 0/1 supported, SMPTE rejected."""
    if not path.exists():
        raise FileNotFoundError(f"MIDI file not found: {path}")
    data = path.read_bytes()
    header, body_start = _parse_header(data)
    if header.smpte:
        raise MidiParseError("SMPTE timecode division is not supported")
    ppq = header.division
    if ppq <= 0:
        raise MidiParseError("non-positive PPQ division")
    if header.format not in (0, 1):
        raise MidiParseError(f"unsupported MIDI format {header.format}")

    tracks: list[MidiTrack] = []
    cursor = body_start
    for i in range(header.track_count):
        if cursor + 8 > len(data):
            raise MidiParseError("truncated track header")
        tracks.append(_parse_track(data, cursor, i, ppq))
        cursor += 8 + int.from_bytes(data[cursor + 4 : cursor + 8], "big")
    if tracks:
        # Track 0 carries global tempo/time-signature in format 0/1; merge all
        # track-level maps deterministically (sorted by tick).
        tempo_map = sorted(
            (e for t in tracks for e in t.tempo_map),
            key=lambda e: (e.tick,),
        )
        time_map = sorted(
            (e for t in tracks for e in t.time_signature_map),
            key=lambda e: (e.tick,),
        )
        key_map = sorted(
            (e for t in tracks for e in t.key_map),
            key=lambda e: (e.tick,),
        )
    else:
        tempo_map = time_map = key_map = []
    return MidiData(
        header=header,
        tracks=tracks,
        tempo_map=tempo_map,
        time_signature_map=time_map,
        key_map=key_map,
        ppq=ppq,
    )


def _measure_layout(timeline: Timeline, ppq: int) -> list[tuple[int, int]]:
    """Infer measure boundaries from time signatures (tick, measure_index)."""
    if not timeline.time_signature_known or not timeline.time_signature_map:
        return []
    boundaries: list[tuple[int, int]] = [(0, 0)]
    current_tick = 0
    measure_index = 0
    sigs = sorted(timeline.time_signature_map, key=lambda e: e.tick)
    for i, sig in enumerate(sigs):
        next_tick = sigs[i + 1].tick if i + 1 < len(sigs) else None
        tick = max(sig.tick, current_tick)
        if next_tick is None:
            break
        length = ppq * 4 * sig.numerator // sig.denominator
        while tick < next_tick:
            measure_index += 1
            tick += length
            boundaries.append((tick, measure_index))
        current_tick = tick
    return boundaries


def _assign_measures(events: list[Event], boundaries: list[tuple[int, int]]) -> list[Event]:
    if not boundaries:
        return events
    result: list[Event] = []
    for ev in events:
        measure_index = None
        position = None
        for i in range(len(boundaries) - 1, -1, -1):
            b_tick, b_index = boundaries[i]
            if ev.tick_start >= b_tick:
                measure_index = b_index
                position = ev.tick_start - b_tick
                break
        if measure_index is not None:
            ev = Event(
                event_id=ev.event_id,
                event_type=ev.event_type,
                tick_start=ev.tick_start,
                tick_end=ev.tick_end,
                pitch_midi=ev.pitch_midi,
                velocity=ev.velocity,
                measure_index=measure_index,
                position_in_measure=position,
                ties=ev.ties,
                source=ev.source,
                status="inferred" if ev.status == "raw" else ev.status,
                confidence=ev.confidence if ev.confidence is not None else 0.9,
                inference_notes=ev.inference_notes + ("measure layout inferred from time signature",),
            )
        result.append(ev)
    return result


def ingest_midi(path: Path) -> MoodifyScore:
    """Ingest a MIDI file into a MoodifyScore document (source MIDI untouched)."""
    sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    midi = parse_midi(path)
    timeline = Timeline(
        tempo_map=tuple(midi.tempo_map),
        time_signature_map=tuple(midi.time_signature_map),
        key_map=tuple(midi.key_map),
        tempo_known=bool(midi.tempo_map),
        time_signature_known=bool(midi.time_signature_map),
        key_known=bool(midi.key_map),
    )
    boundaries = _measure_layout(timeline, midi.ppq)

    parts: list[Part] = []
    for track in midi.tracks:
        events: list[Event] = []
        for i, note in enumerate(sorted(track.notes, key=lambda n: (n.tick, n.pitch))):
            if note.tick_end is None:
                continue  # unterminated note
            ev = Event(
                event_id=f"{track.index}:{i}",
                event_type="note",
                tick_start=note.tick,
                tick_end=note.tick_end,
                pitch_midi=note.pitch,
                velocity=note.velocity,
                ties=(),
                source="midi_ingest",
                status="raw",
            )
            events.append(ev)
        events = _assign_measures(events, boundaries)
        staff = Staff(staff_id=f"{track.index}:staff-1", clef=None, voices=(Voice(voice_id=f"{track.index}:voice-1", events=tuple(events)),))
        parts.append(
            Part(
                part_id=f"P-{track.index + 1}",
                name=track.name or f"Track {track.index + 1}",
                instrument=None,
                channel=track.channel,
                program=track.program,
                source_track=track.index,
                staves=(staff,),
            )
        )

    source = SourceAsset(kind="midi", path=str(path), sha256=sha256, role="input")
    return MoodifyScore(
        schema_version="moodifyscore/0.1",
        score_id="",  # assigned by serialization
        revision=1,
        metadata=ScoreMetadata(title=path.stem),
        source_assets=(source,),
        timeline=timeline,
        parts=tuple(parts),
        evidence={"import": {"ppq": midi.ppq, "format": midi.header.format, "track_count": len(midi.tracks)}},
    )
