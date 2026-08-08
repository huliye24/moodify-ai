# 00_IMPLEMENTATION_AUDIT — DSK-MFY-STEM-MIDI-008

**Date:** 2026-08-01 | **HEAD:** df3a8a3

## Environment

| Item | Value |
|---|---|
| Branch | codex/mainline-cloud-dev-20260603 |
| Python 3.11 | `C:\Program Files\Python311\python.exe` (3.11.9) |
| .venv-basic-pitch | Present; Basic Pitch 0.4.0 via ONNX |
| Demucs | NOT installed (no stem separation available) |
| Core tests (transcription) | 3 passed |
| Core tests (full) | Not run (out of scope for Stage 0) |

## Real API Surface

- `transcribe_audio(audio_path, output_path, config, backend)` — single file
- `TranscriptionConfig` — thresholds, frequency range, tempo, pitch bends
- `BasicPitchBackend` — wraps `basic_pitch.inference.predict()`
- `TranscriptionBackend` Protocol — replaceable
- CLI: `moodify transcribe AUDIO --output OUT.mid [options]`

## Dependencies (installed)

```
numpy>=1.24,<2, scipy>=1.11,<1.14, librosa>=0.10,<0.11
mir_eval>=0.8,<0.9, pretty_midi>=0.2.10,<0.3
resampy>=0.4,<0.4.3, scikit-learn>=1.3,<1.6, onnxruntime>=1.16,<2
basic-pitch==0.4.0 (no-deps)
```

## Performance Constraints

| Constraint | Limit |
|---|---|
| RAM | ~8 GB total; single model instance |
| GPU | None (CPU-only ONNX) |
| Parallel loading | Banned (8 GB constraint) |

## Missing Capabilities

| Capability | Status |
|---|---|
| Stem separation | Demucs not installed; `--separate` must error gracefully |
| Drum transcription | UNSUPPORTED; Basic Pitch cannot transcribe drums |
| Key detection | Not in Basic Pitch; would need external |
| Multi-track merge | Not implemented (target for Stage 2) |

## Dirty Worktree

User's pre-existing modified/untracked files in core-package, runtime, bridge, docs, scratch — ALL preserved. Only permitted files touched.
