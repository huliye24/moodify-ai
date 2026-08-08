# VALIDATION_REPORT — DSK-MFY-STEM-MIDI-008

**Status:** ACCEPTED_AFTER_CODEX_FINISH_WITH_BENCHMARK_LIMITS

## Test Results

| Suite | Result |
|---|---|
| test_transcription_stems.py (21 tests) | 21 passed |
| test_transcription.py (3 tests) | 3 passed |
| **Total** | **24 passed, 0 failed** |
| Ruff | clean |
| Mypy | clean across 7 source files |

## Test Coverage

- StemKind enum + validation
- StemManifest: from_cli_pairs, duplicates, unknown kind
- Path safety: traversal rejection, missing file
- Profile registry: all kinds, reasonable values, drums excluded
- Runner: fake backend, drums skip, failure isolation
- API-level non-empty output rejection and partial-file cleanup
- Unsupported-stem per-track evidence
- Default cleanup timing preservation and raw immutability
- Default cleanup event idempotence
- Explicit quantization with duration preservation
- Type 1 merge, stable track names, pitch bend/control change preservation
- Old API: FakeBackend, threshold rejection, format rejection

## Implementation Correctness

- raw MIDI: write-once, never modified; CLI and library both reject non-empty output
- clean MIDI: derived per stem with CleanupDiff and hashes
- merged MIDI: derived Type 1 file with hash in run manifest
- Drums: UNSUPPORTED, no Basic Pitch call
- Vocals: pitch bends enabled, melodia_trick disabled
- Bass: octave-constrained frequency range
- Failure isolation: one stem fails, others continue
- Quantization/key correction: OFF by default

## Limitations

- Demucs not installed; no stem separation
- No scored synthetic audio ground truth fixtures yet (deferred)
- No real-song accuracy metrics (no ground truth)
- No performance benchmarks (8 GB machine constraint noted)
- No Demucs separator or pitched drum transcription

These limits block accuracy/performance claims, not the accepted deterministic
raw-clean-merged engineering path.
