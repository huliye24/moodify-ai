# MHP-869: MRS Engine Adapter Hook

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-BUILD-046 / Build Plan-6B / E1
**Depends on**: MHP-868 (Close Data Model), MHP-854 (MRS Boundary Brief)

## What Was Implemented

Created `mrs_adapter.py` — ~270-line adapter bridging v01 pipeline and moodify_runtime MRS engine.

### Key function: `score_for_quality_gate(before_path, after_path, genre, preset, sample_id) -> QualityGate`

**When MRS engine available**: Calls `mrs_engine.score_audio()`, maps `MRSScoreResult` → `QualityGate` with `mrs_version = "mrs_calibrated_v02"`.

**When MRS engine unavailable**: Falls back to inline proxy with `mrs_version = "mrs_proxy_v01"`.

### Integration point

Updated `_quality_gate()` in `v01_pipeline.py` to try `score_for_quality_gate()` first, then fall back to inline proxy.

### Evidence

```text
49/49 tests pass. mrs_version = "mrs_calibrated_v02" when MRS Open available.
```

### Files Changed
- `mrs_adapter.py` (NEW): 270 lines — adapter + inline fallback helpers
- `v01_pipeline.py`: `_quality_gate()` now tries adapter first
- `test_v01_pipeline.py`: mrs_version assertion updated for multi-version compat
