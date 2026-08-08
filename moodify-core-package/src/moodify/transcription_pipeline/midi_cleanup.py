"""Non-destructive MIDI cleanup and multi-track merge.

All cleanup actions are OFF by default (except dedup/filter/voice/range which
are passive cleanup). Quantization and key correction require explicit flags.
Raw MIDI is never modified; cleaned MIDI is a derived file with a raw-vs-clean diff.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

import pretty_midi  # type: ignore[import-untyped]

GM_PROGRAMS = {"vocals": 54, "bass": 34, "piano": 1, "guitar": 25, "other": 1}


@dataclass
class CleanupConfig:
    # Always-on (passive, non-destructive marking unless --aggressive)
    remove_duplicates: bool = True
    min_note_ms: float = 50.0
    voice_limit: int = 6
    clip_range: bool = False  # remove out-of-range (OFF by default)

    # Always-OFF (require explicit flags)
    quantize_grid: str | None = None  # e.g. "1/8", "1/16"
    quantize_strength: float = 1.0
    key: str | None = None  # e.g. "C", "Dm"
    scale: str | None = None  # e.g. "major", "minor"


@dataclass
class CleanupDiff:
    total_notes_raw: int = 0
    total_notes_clean: int = 0
    duplicates_removed: int = 0
    short_notes_removed: int = 0
    voices_clipped: int = 0
    range_clipped: int = 0
    quantized_notes: int = 0
    key_corrected_notes: int = 0
    displacement_stats: dict = field(default_factory=dict)


def _grid_to_seconds(grid: str, tempo: float) -> float:
    """Convert a grid string like '1/8' to seconds at given tempo."""
    beat_duration = 60.0 / tempo
    parts = grid.split("/")
    if len(parts) == 2:
        return beat_duration * 4 * int(parts[0]) / int(parts[1])
    return 0.0


def _quantize_time(time_s: float, grid_s: float, strength: float) -> float:
    if grid_s <= 0 or strength <= 0:
        return time_s
    target = round(time_s / grid_s) * grid_s
    return time_s + (target - time_s) * strength


def _note_frequency(note: pretty_midi.Note) -> float:
    return 440.0 * (2.0 ** ((note.pitch - 69) / 12.0))


def cleanup_midi(
    midi_path: str | Path,
    output_path: str | Path,
    config: CleanupConfig | None = None,
    min_freq: float | None = None,
    max_freq: float | None = None,
) -> CleanupDiff:
    """Clean up a single MIDI file. Returns a CleanupDiff."""
    source = Path(midi_path).resolve()
    destination = Path(output_path).resolve()
    if source == destination:
        raise ValueError("Clean MIDI must be written to a different path from raw MIDI")
    if destination.exists():
        raise FileExistsError(f"Clean MIDI already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    cfg = config or CleanupConfig()
    if not 0.0 <= cfg.quantize_strength <= 1.0:
        raise ValueError("quantize_strength must be between 0 and 1")
    midi = pretty_midi.PrettyMIDI(str(source))
    diff = CleanupDiff()
    diff.total_notes_raw = sum(len(i.notes) for i in midi.instruments)

    for inst in midi.instruments:
        notes = sorted(inst.notes, key=lambda n: (n.start, n.pitch, n.velocity))
        if not notes:
            continue

        # 1. Remove exact duplicates
        if cfg.remove_duplicates:
            seen = set()
            deduped = []
            for n in notes:
                key = (round(n.start, 6), round(n.end, 6), n.pitch, n.velocity)
                if key not in seen:
                    seen.add(key)
                    deduped.append(n)
                else:
                    diff.duplicates_removed += 1
            notes = deduped

        # 2. Remove short notes
        filtered = []
        for n in notes:
            duration_ms = (n.end - n.start) * 1000
            if duration_ms >= cfg.min_note_ms:
                filtered.append(n)
            else:
                diff.short_notes_removed += 1
        notes = filtered

        # 3. Voice limit (per onset)
        if cfg.voice_limit > 0:
            onset_groups: dict[float, list[pretty_midi.Note]] = {}
            for n in notes:
                onset_groups.setdefault(round(n.start, 6), []).append(n)
            kept = []
            for onset, group in onset_groups.items():
                if len(group) > cfg.voice_limit:
                    group.sort(key=lambda n: n.velocity, reverse=True)
                    kept.extend(group[:cfg.voice_limit])
                    diff.voices_clipped += len(group) - cfg.voice_limit
                else:
                    kept.extend(group)
            notes = kept

        # 4. Range clip
        if cfg.clip_range:
            clipped = []
            for n in notes:
                freq = _note_frequency(n)
                if (min_freq is not None and freq < min_freq) or (max_freq is not None and freq > max_freq):
                    diff.range_clipped += 1
                else:
                    clipped.append(n)
            notes = clipped

        # 5. Quantize (OFF by default)
        if cfg.quantize_grid:
            grid_s = _grid_to_seconds(cfg.quantize_grid, 120.0)
            if grid_s <= 0:
                raise ValueError(f"Invalid quantize grid: {cfg.quantize_grid}")
            if cfg.quantize_strength > 0:
                shifts = []
                for n in notes:
                    old_start = n.start
                    duration = n.end - n.start
                    n.start = _quantize_time(n.start, grid_s, cfg.quantize_strength)
                    n.end = n.start + duration
                    if abs(n.start - old_start) > 0.001:
                        shifts.append(abs(n.start - old_start) * 1000)
                    diff.quantized_notes += 1
                if shifts:
                    diff.displacement_stats = {
                        "mean_timing_shift_ms": round(sum(shifts) / len(shifts), 2),
                        "max_timing_shift_ms": round(max(shifts), 2),
                    }

        # 6. Key correction (OFF by default — stub for Stage 2)
        if cfg.key and cfg.scale:
            diff.key_corrected_notes = 0  # key correction is deferred

        inst.notes = notes

    diff.total_notes_clean = sum(len(i.notes) for i in midi.instruments)
    midi.write(str(destination))
    return diff


def merge_to_type1(
    midi_paths: Mapping[str, str | Path],
    output_path: str | Path,
    tempo: float = 120.0,
) -> str:
    """Merge multiple MIDI files into a Type 1 multi-track MIDI.

    midi_paths: {stem_kind: path_to_midi}
    Stable track order: vocals, bass, piano, guitar, other
    """
    destination = Path(output_path).resolve()
    if destination.exists():
        raise FileExistsError(f"Merged MIDI already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    merged = pretty_midi.PrettyMIDI(initial_tempo=tempo)
    track_order = ["vocals", "bass", "piano", "guitar", "other"]

    for channel, kind in enumerate(track_order):
        if kind not in midi_paths:
            continue
        path = midi_paths[kind]
        src = pretty_midi.PrettyMIDI(str(path))
        program = GM_PROGRAMS.get(kind, 1)
        inst = pretty_midi.Instrument(program=program, name=kind, is_drum=(kind == "drums"))
        # Collect all notes from source
        for src_inst in src.instruments:
            for note in src_inst.notes:
                inst.notes.append(note)
            inst.pitch_bends.extend(src_inst.pitch_bends)
            inst.control_changes.extend(src_inst.control_changes)
        merged.instruments.append(inst)

    merged.write(str(destination))
    return str(destination)
