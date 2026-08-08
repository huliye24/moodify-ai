"""Clean Basic Pitch MIDI files for MuseScore asset generation.

The source MIDI files use a 120 BPM timing base.  The song's notation pulse is
treated as 68 BPM, so event times are first rescaled by 68/120 and then
quantized on the target notation grid.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


TPQ = 480
SOURCE_BPM = 120
TARGET_BPM = 68
GRID = 120  # sixteenth note at the target notation tempo


@dataclass
class Note:
    start: int
    end: int
    pitch: int
    velocity: int


def read_vlq(data: bytes, index: int) -> tuple[int, int]:
    value = 0
    while True:
        byte = data[index]
        index += 1
        value = (value << 7) | (byte & 0x7F)
        if byte < 0x80:
            return value, index


def write_vlq(value: int) -> bytes:
    parts = [value & 0x7F]
    value >>= 7
    while value:
        parts.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(parts))


def parse_notes(path: Path) -> list[Note]:
    data = path.read_bytes()
    header_len = int.from_bytes(data[4:8], "big")
    track_count = int.from_bytes(data[10:12], "big")
    index = 8 + header_len
    notes: list[Note] = []

    for _ in range(track_count):
        length = int.from_bytes(data[index + 4 : index + 8], "big")
        track = data[index + 8 : index + 8 + length]
        index += 8 + length
        cursor = 0
        tick = 0
        running = None
        active: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)

        while cursor < len(track):
            delta, cursor = read_vlq(track, cursor)
            tick += delta
            status = track[cursor]
            if status < 0x80:
                status = running
            else:
                cursor += 1
                running = status if status < 0xF0 else None

            if status == 0xFF:
                cursor += 1
                size, cursor = read_vlq(track, cursor)
                cursor += size
                running = None
            elif status in (0xF0, 0xF7):
                size, cursor = read_vlq(track, cursor)
                cursor += size
                running = None
            else:
                message = status & 0xF0
                channel = status & 0x0F
                if message in (0xC0, 0xD0):
                    cursor += 1
                    continue
                pitch = track[cursor]
                velocity = track[cursor + 1]
                cursor += 2
                key = (channel, pitch)
                if message == 0x90 and velocity:
                    active[key].append((tick, velocity))
                elif message == 0x80 or (message == 0x90 and not velocity):
                    if active[key]:
                        start, start_velocity = active[key].pop(0)
                        notes.append(Note(start, tick, pitch, start_velocity))
    return notes


def target_tick(source_tick: int, grid: int = GRID) -> int:
    scaled = source_tick * TARGET_BPM / SOURCE_BPM
    return round(scaled / grid) * grid


def quantize(
    notes: list[Note],
    minimum_pitch: int,
    maximum_pitch: int,
    grid: int = GRID,
) -> list[Note]:
    cleaned: dict[tuple[int, int], Note] = {}
    for note in notes:
        if note.end - note.start < 60:
            continue
        if not minimum_pitch <= note.pitch <= maximum_pitch:
            continue
        start = target_tick(note.start, grid)
        end = max(start + grid, target_tick(note.end, grid))
        candidate = Note(start, end, note.pitch, note.velocity)
        key = (start, note.pitch)
        previous = cleaned.get(key)
        if previous is None or candidate.velocity > previous.velocity:
            cleaned[key] = candidate
    return sorted(cleaned.values(), key=lambda n: (n.start, n.pitch, n.end))


def chordal_simplify(notes: list[Note], limit: int, grid: int) -> list[Note]:
    groups: list[list[Note]] = []
    for note in notes:
        if not groups or note.start != groups[-1][0].start:
            groups.append([note])
        else:
            groups[-1].append(note)

    result: list[Note] = []
    for index, group in enumerate(groups):
        next_start = groups[index + 1][0].start if index + 1 < len(groups) else None
        ranked = sorted(group, key=lambda n: (-n.velocity, -(n.end - n.start)))
        selected: list[Note] = []
        for candidate in ranked:
            if all(abs(candidate.pitch - kept.pitch) >= 3 for kept in selected):
                selected.append(candidate)
            if len(selected) == limit:
                break
        selected.sort(key=lambda n: n.pitch)
        for note in selected:
            end = note.end
            if next_start is not None:
                end = min(end, next_start)
            end = max(note.start + grid, end)
            result.append(Note(note.start, end, note.pitch, note.velocity))
    return sorted(result, key=lambda n: (n.start, n.pitch))


def monophonic(notes: list[Note], prefer: str) -> list[Note]:
    groups: list[list[Note]] = []
    for note in notes:
        if not groups or note.start != groups[-1][0].start:
            groups.append([note])
        else:
            groups[-1].append(note)

    result: list[Note] = []
    previous_pitch = None
    for group in groups:
        if prefer == "fundamental":
            choice = min(group, key=lambda n: (n.pitch, -n.velocity))
        else:
            choice = max(
                group,
                key=lambda n: (
                    n.velocity
                    - (0 if previous_pitch is None else abs(n.pitch - previous_pitch) * 2),
                    n.end - n.start,
                ),
            )
        if result and choice.start < result[-1].end:
            result[-1].end = max(result[-1].start + GRID, choice.start)
        if not result or choice.start >= result[-1].start + GRID:
            result.append(choice)
            previous_pitch = choice.pitch
    return result


def drum_skeleton(notes: list[Note]) -> list[Note]:
    result: dict[tuple[int, int], Note] = {}
    for note in notes:
        if note.pitch <= 34:
            pitch = 36  # kick
        elif note.pitch <= 43:
            pitch = 38  # snare
        elif note.pitch <= 48:
            pitch = 45  # low tom
        else:
            pitch = 42  # closed hi-hat
        candidate = Note(note.start, note.start + GRID, pitch, note.velocity)
        result[(candidate.start, pitch)] = candidate
    return sorted(result.values(), key=lambda n: (n.start, n.pitch))


def build_midi(notes: list[Note], title: str, program: int, drum: bool) -> bytes:
    events: list[tuple[int, int, bytes]] = []

    def add(tick: int, order: int, payload: bytes) -> None:
        events.append((tick, order, payload))

    title_bytes = title.encode("utf-8")
    add(0, 0, b"\xff\x03" + write_vlq(len(title_bytes)) + title_bytes)
    add(0, 0, b"\xff\x51\x03" + round(60_000_000 / TARGET_BPM).to_bytes(3, "big"))
    add(0, 0, b"\xff\x58\x04\x04\x02\x18\x08")  # 4/4
    add(0, 0, b"\xff\x59\x02\xff\x00")  # one flat, major
    channel = 9 if drum else 0
    if not drum:
        add(0, 0, bytes([0xC0 | channel, program]))

    for note in notes:
        add(note.start, 2, bytes([0x90 | channel, note.pitch, max(30, min(110, note.velocity))]))
        add(note.end, 1, bytes([0x80 | channel, note.pitch, 0]))

    events.sort(key=lambda item: (item[0], item[1]))
    track = bytearray()
    last_tick = 0
    for tick, _, payload in events:
        track += write_vlq(max(0, tick - last_tick)) + payload
        last_tick = tick
    track += b"\x00\xff\x2f\x00"
    header = (
        b"MThd"
        + (6).to_bytes(4, "big")
        + (0).to_bytes(2, "big")
        + (1).to_bytes(2, "big")
        + TPQ.to_bytes(2, "big")
    )
    return header + b"MTrk" + len(track).to_bytes(4, "big") + track


PROFILES = {
    "bass": dict(program=33, pitch=(24, 55), mono="fundamental", drum=False, grid=120, poly=None),
    "vocals": dict(program=53, pitch=(45, 88), mono="melody", drum=False, grid=120, poly=None),
    "drums": dict(program=0, pitch=(0, 127), mono=None, drum=True, grid=120, poly=None),
    "strings": dict(program=48, pitch=(29, 88), mono=None, drum=False, grid=240, poly=3),
    "synthesizer": dict(program=89, pitch=(26, 88), mono=None, drum=False, grid=240, poly=3),
    "full_mix": dict(program=0, pitch=(24, 96), mono=None, drum=False, grid=240, poly=4),
    "accompaniment": dict(program=0, pitch=(24, 96), mono=None, drum=False, grid=240, poly=4),
}


def clean_file(source: Path, destination: Path, profile_name: str) -> tuple[int, int]:
    profile = PROFILES[profile_name]
    raw = parse_notes(source)
    notes = quantize(raw, *profile["pitch"], grid=profile["grid"])
    if profile["drum"]:
        notes = drum_skeleton(notes)
    elif profile["mono"]:
        notes = monophonic(notes, profile["mono"])
    elif profile["poly"]:
        notes = chordal_simplify(notes, profile["poly"], profile["grid"])
    destination.write_bytes(
        build_midi(notes, f"{profile_name.replace('_', ' ').title()} Clean", profile["program"], profile["drum"])
    )
    return len(raw), len(notes)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("profile", choices=sorted(PROFILES))
    args = parser.parse_args()
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    raw_count, clean_count = clean_file(args.source, args.destination, args.profile)
    print(f"{args.profile}: {raw_count} raw notes -> {clean_count} cleaned notes")


if __name__ == "__main__":
    main()
