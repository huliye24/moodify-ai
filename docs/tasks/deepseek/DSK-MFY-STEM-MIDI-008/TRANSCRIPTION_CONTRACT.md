# TRANSCRIPTION_CONTRACT — DSK-MFY-STEM-MIDI-008

**Status:** Frozen before any code change.

## 1. StemKind Enum (closed)

| Value | Transcription | Profile | Notes |
|---|---|---|---|
| `vocals` | Basic Pitch | melody_focused | Pitch bends enabled |
| `bass` | Basic Pitch | bass | Octave-constrained frequency range |
| `piano` | Basic Pitch | piano | Polyphonic, no pitch bends |
| `guitar` | Basic Pitch | guitar | Polyphonic, mid-frequency range |
| `other` | Basic Pitch | other | Neutral profile, no instrument-specific tuning |
| `drums` | NONE | drums_unsupported | Registered as UNSUPPORTED; no MIDI output |
| `unknown` | NONE | unknown | Cannot determine; flags for human review |

## 2. StemManifest Input

```yaml
stems:
  - kind: vocals
    path: vocals.wav
  - kind: bass
    path: bass.wav
```

Or CLI: `--stem vocals=vocals.wav --stem bass=bass.wav`

Rules:
- Unknown kind rejected (strict enum)
- Duplicate kind rejected
- Path must exist, be regular file, be readable WAV/MP3/FLAC/OGG
- Path traversal (`..`) rejected
- Source files never modified

## 3. Per-Stem Output

```
OUTDIR/
  raw/
    vocals.mid
    bass.mid
    piano.mid
  run_manifest.json
  per_stem/
    vocals.json    # {stem_kind, source_hash, backend, config, note_count, elapsed, status}
    bass.json
```

## 4. Profile Registry

Each profile defines:
- `min_frequency_hz`, `max_frequency_hz`
- `onset_threshold`, `frame_threshold`
- `minimum_note_length_ms`
- `multiple_pitch_bends` (bool)
- `melodia_trick` (bool)
- `description`

Default profiles provided for vocals/bass/piano/guitar/other. Overridable via CLI flags.

## 5. Error Model

| Condition | Status | Exit |
|---|---|---|
| Single stem backend failure | `partial_success`; other stems continue | 0 |
| All stems fail | `failed` | 1 |
| Invalid stem kind | Reject before processing | 2 |
| Path traversal / missing file | Reject before processing | 2 |
| Output dir not empty | Reject | 2 |
| Demucs requested but not installed | Reject with message | 2 |
| Drums stem | `unsupported`; skipped | 0 (if others succeed) |
| No stems specified | Error | 2 |

## 6. Source Integrity

- Every stem file SHA-256 recorded before processing
- Raw MIDI output SHA-256 recorded
- Source files never opened for writing
- `run_manifest.json` includes all hashes
