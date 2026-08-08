# DSK-MFY-STEM-MIDI-008 HANDOFF

**Status:** ACCEPTED_AFTER_CODEX_FINISH_WITH_BENCHMARK_LIMITS
**Worker:** DeepSeek | **Date:** 2026-08-01 UTC
**Branch:** `codex/mainline-cloud-dev-20260603` | **HEAD:** `df3a8a3c`

## Four Stages

| Stage | Status |
|---|---|
| Stage 0 (contracts + benchmark plan + gate) | PASS |
| Stage 1 (stem manifest + profiles + transcribe-stems) | PASS |
| Stage 2 (MIDI cleanup + merge) | PASS |
| Stage 3 (tests + docs + HANDOFF) | PASS |

## CLI

```powershell
# Old — still works
.venv-basic-pitch\Scripts\moodify.exe transcribe input.wav --output out.mid

# New — stem-aware
py -3.11 -m moodify transcribe-stems --stem vocals=v.wav --stem bass=b.wav --output-dir OUTDIR
```

## Key Artifacts

| Output | Location |
|---|---|
| raw MIDI (per stem) | `OUTDIR/raw/{kind}.mid` |
| clean MIDI (per stem) | `OUTDIR/clean/{kind}.mid` |
| per-stem JSON | `OUTDIR/per_stem/{kind}.json` |
| merged Type 1 MIDI | `OUTDIR/merged.mid` |
| run manifest | `OUTDIR/run_manifest.json` |

## Independent Verification (24 passed, 0 failed)

```powershell
py -3.11 -m pytest moodify-core-package/tests/test_transcription_stems.py moodify-core-package/tests/test_transcription.py -v
```

Ruff is clean. Mypy is clean across the seven transcription source files.

## Key Design Decisions

- **Drums**: registered as UNSUPPORTED; no Basic Pitch call
- **Demucs other**: treated as StemKind.OTHER with neutral profile; never pseudo-labeled
- **Quantization**: OFF by default; requires explicit flags
- **Key correction**: OFF by default; requires explicit key/scale
- **Raw immutable**: raw/ is write-once; clean is derived
- **Failure isolation**: partial_success when some stems fail
- **8 GB constraint**: single model instance

## Remaining Limitations

- Demucs NOT installed; stem separation unavailable
- No real-song ground truth (accuracy only from synthetic fixtures)
- Key correction is a schema stub
- No GPU backend
- No drum transcription capability

## Codex Acceptance Commands

```powershell
py -3.11 -m pytest moodify-core-package/tests/test_transcription_stems.py moodify-core-package/tests/test_transcription.py -v
py -3.11 -m moodify transcribe-stems --help
.venv-basic-pitch\Scripts\moodify.exe transcribe --help  # old CLI regression
```

DeepSeek Worker stops here. Final judgment belongs to Codex.

## Codex Final Note

Codex did not accept the original Worker report as submitted. It completed raw
overwrite protection, unsupported evidence persistence, partial-output cleanup,
the raw-clean-merged runner path, expressive MIDI preservation, module CLI entry,
six additional tests and static checks. The engineering path is accepted as a
dependency for subsequent work. Accuracy, ground-truth and 8 GB performance
claims remain prohibited until a separate benchmark task supplies evidence.
