# MHP-053: Real Audio Integration Test — End-to-End with Live DSP

**Status**: proposed
**Direction**: 6-Step Plan — E1 (Execution)
**Depends on**: MHP-050 evidence (107 tests, no real audio E2E)
**Protocol**: 泫榛 6-Step Plan Protocol

## Evidence

- 107 tests pass, but NONE exercise the real audio DSP pipeline
- `run_operator_job --live` has guards but is untested with actual processing
- All existing tests use `_write_manifest()` to inject synthetic data
- The `moodify` CLI (`moodify process --preset warm_vocal`) works manually but has no automated test
- MRS metrics (`compute_mrs_open_v031`) are computed during real runs but never verified in tests

## Goal

Create a `@pytest.mark.slow` test that runs the full pipeline with real audio:
1. Create job from baseline test WAV
2. Plan runtime (registry → queue)
3. Execute `run_operator_job --live` (real DSP processing)
4. Verify manifest.csv is produced with non-empty rows
5. Verify MRS scores are computed (not None/empty)
6. Verify gate decisions are based on real data
7. Verify report bundle contains real content

## Acceptance Criteria

- At least 1 test exercises real audio DSP processing
- Test is marked `@pytest.mark.slow` (skipped in normal CI)
- Test verifies: manifest exists, MRS scores present, gate decisions made, report generated
- Test completes in under 5 minutes
- Existing 107 tests still pass (slow test excluded by default)

## Test Plan
```bash
python3 -m pytest moodify_runtime/tests/test_real_audio.py -v -m slow
```
