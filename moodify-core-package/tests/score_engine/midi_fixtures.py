"""Deterministic synthetic MIDI builders for score engine tests."""

from __future__ import annotations


def write_vlq(value: int) -> bytes:
    parts = [value & 0x7F]
    value >>= 7
    while value:
        parts.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(parts))


class TrackBuilder:
    def __init__(self) -> None:
        self._events: list[tuple[int, int, bytes]] = []

    def add(self, tick: int, order: int, payload: bytes) -> None:
        self._events.append((tick, order, payload))

    def meta(self, tick: int, meta_type: int, body: bytes) -> None:
        self.add(tick, 0, b"\xff" + bytes([meta_type]) + write_vlq(len(body)) + body)

    def track_name(self, tick: int, name: str) -> None:
        self.meta(tick, 0x03, name.encode("utf-8"))

    def tempo(self, tick: int, bpm: int) -> None:
        micros = round(60_000_000 / bpm)
        self.meta(tick, 0x51, micros.to_bytes(3, "big"))

    def time_signature(self, tick: int, numerator: int, denominator_pow: int) -> None:
        self.meta(tick, 0x58, bytes([numerator, denominator_pow, 24, 8]))

    def key_signature(self, tick: int, fifths: int, minor: bool = False) -> None:
        self.meta(tick, 0x59, bytes([fifths & 0xFF, 1 if minor else 0]))

    def program_change(self, tick: int, channel: int, program: int) -> None:
        self.add(tick, 0, bytes([0xC0 | channel, program]))

    def note(self, tick: int, channel: int, pitch: int, velocity: int, duration: int) -> None:
        self.add(tick, 2, bytes([0x90 | channel, pitch, velocity]))
        self.add(tick + duration, 1, bytes([0x80 | channel, pitch, 0]))

    def note_off_vel(self, tick: int, channel: int, pitch: int) -> None:
        self.add(tick, 1, bytes([0x80 | channel, pitch, 0]))

    def sysex(self, tick: int, body: bytes) -> None:
        self.add(tick, 0, b"\xf0" + write_vlq(len(body)) + body)

    def build(self) -> bytes:
        self._events.sort(key=lambda item: (item[0], item[1]))
        track = bytearray()
        last_tick = 0
        for tick, _, payload in self._events:
            track += write_vlq(max(0, tick - last_tick)) + payload
            last_tick = tick
        track += b"\x00\xff\x2f\x00"
        return b"MTrk" + len(track).to_bytes(4, "big") + track


def build_midi(
    tracks: list[TrackBuilder],
    format_code: int = 1,
    ppq: int = 480,
) -> bytes:
    header = (
        b"MThd"
        + (6).to_bytes(4, "big")
        + format_code.to_bytes(2, "big")
        + len(tracks).to_bytes(2, "big")
        + ppq.to_bytes(2, "big")
    )
    chunks = [header]
    for builder in tracks:
        chunks.append(builder.build())
    return b"".join(chunks)


def single_track_midi() -> bytes:
    t = TrackBuilder()
    t.track_name(0, "Melody")
    t.tempo(0, 120)
    t.time_signature(0, 4, 2)
    t.key_signature(0, 0, False)  # C major
    t.program_change(0, 0, 40)
    t.note(0, 0, 60, 100, 240)
    t.note(240, 0, 62, 90, 240)
    t.note(480, 0, 64, 80, 240)
    return build_midi([t], format_code=0)


def multi_track_midi() -> bytes:
    t1 = TrackBuilder()
    t1.track_name(0, "Vocals")
    t1.tempo(0, 90)
    t1.time_signature(0, 3, 1)
    t1.program_change(0, 0, 53)
    t1.note(0, 0, 72, 100, 240)
    t1.note(240, 0, 74, 90, 240)

    t2 = TrackBuilder()
    t2.track_name(0, "Bass")
    t2.program_change(0, 1, 33)
    t2.note(0, 1, 36, 110, 480)
    t2.note(480, 1, 38, 105, 480)
    return build_midi([t1, t2])


def tempo_change_midi() -> bytes:
    t = TrackBuilder()
    t.track_name(0, "Tempo Test")
    t.tempo(0, 100)
    t.time_signature(0, 4, 2)
    t.tempo(480, 140)
    t.note(0, 0, 60, 100, 240)
    t.note(480, 0, 62, 90, 240)
    return build_midi([t], format_code=0)


def time_signature_change_midi() -> bytes:
    t = TrackBuilder()
    t.track_name(0, "Sig Test")
    t.tempo(0, 120)
    t.time_signature(0, 4, 2)
    t.time_signature(960, 3, 2)
    t.note(0, 0, 60, 100, 240)
    t.note(960, 0, 62, 90, 240)
    return build_midi([t], format_code=0)


def rest_and_chord_midi() -> bytes:
    t = TrackBuilder()
    t.track_name(0, "Chord")
    t.tempo(0, 120)
    t.time_signature(0, 4, 2)
    # chord: three simultaneous notes
    t.note(0, 0, 60, 100, 240)
    t.note(0, 0, 64, 95, 240)
    t.note(0, 0, 67, 90, 240)
    # rest: gap until 720
    t.note(720, 0, 72, 88, 240)
    return build_midi([t], format_code=0)


def unicode_track_midi() -> bytes:
    t = TrackBuilder()
    t.track_name(0, "旋律 メロディー 🎵")
    t.tempo(0, 120)
    t.time_signature(0, 4, 2)
    t.note(0, 0, 60, 100, 240)
    return build_midi([t], format_code=0)


def empty_track_midi() -> bytes:
    t = TrackBuilder()
    t.track_name(0, "Empty")
    return build_midi([t], format_code=0)
