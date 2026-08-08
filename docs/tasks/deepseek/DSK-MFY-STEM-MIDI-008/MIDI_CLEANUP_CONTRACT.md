# MIDI_CLEANUP_CONTRACT — DSK-MFY-STEM-MIDI-008

**Status:** Frozen before any code change.

## 1. Core Principle

Raw MIDI is immutable. Clean MIDI is a derived artifact. Every cleanup action must be:
- Explicitly enabled (default OFF for quantization, key correction)
- Reversible (raw always preserved)
- Documented (raw-vs-clean diff produced)

## 2. Cleanup Actions

### 2.1 Duplicate Removal (default ON)
- Remove notes with identical (start_time, pitch, velocity) within same track
- "Near-duplicate": same pitch, overlapping >50% → mark as WARN, do NOT delete

### 2.2 Minimum Note Filter (default ON)
- Remove notes shorter than `min_note_ms` (from profile, default 50ms)
- Report count of removed notes

### 2.3 Voice Limit (default ON)
- Per track: if >N notes at same onset → keep loudest N (N from profile, default 6)
- Report clipped voices

### 2.4 Range Clip (default ON)
- Per profile: notes outside [min_freq, max_freq] → marked in diff, NOT removed
- If `--clip-range` flag set → out-of-range notes removed

### 2.5 Quantization (default OFF)
- Requires `--quantize GRID` (e.g., 1/8, 1/16, 1/32)
- Requires `--quantize-strength` (0.0-1.0, default 1.0)
- Strength 0.0 = no quantization (passthrough)
- Reports per-note displacement statistics

### 2.6 Key Correction (default OFF)
- Requires `--key KEY` (e.g., C, Dm) and `--scale SCALE` (major, minor, etc.)
- Produces candidates: {original_pitch, candidate_pitch, distance_semitones, rule}
- Never modifies pitch without explicit key/scale
- Never modifies pitch bends or vocal slides

## 3. Raw-vs-Clean Diff

```json
{
  "total_notes_raw": N,
  "total_notes_clean": M,
  "actions": {
    "duplicates_removed": 0,
    "short_notes_removed": 0,
    "voices_clipped": 0,
    "range_clipped": 0,
    "quantized_notes": 0,
    "key_corrected_notes": 0
  },
  "displacement_stats": {
    "mean_timing_shift_ms": 0.0,
    "max_timing_shift_ms": 0.0
  }
}
```

## 4. Multi-Track Merge (Type 1)

- Stable track order: vocals, bass, piano, guitar, other
- Track names from stem kind
- GM program numbers: vocals=54, bass=34, piano=1, guitar=25, other=1
- Unified tempo from first track; configurable via `--tempo`
- Channels: sequential (1, 2, 3, ...)
- Drums: channel 10, GM drum kit, but ONLY if drum MIDI exists (which it won't from Basic Pitch)

## 5. Idempotence

Running cleanup twice on same input produces identical output. No randomness.
