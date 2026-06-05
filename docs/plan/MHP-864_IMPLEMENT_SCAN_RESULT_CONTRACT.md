# MHP-864: Implement Scan Result Contract

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-BUILD-046 / Build Plan-6A / E2
**Depends on**: MHP-863 (Data Model), MHP-851 (Scan Gap Brief)

## What Was Implemented

Extended `ScanResult` dataclass with 6 acoustic surface fields and updated `scan_audio()` to compute them in a single pass.

### New ScanResult fields (all Optional/zero-default for backwards compat)

| Field | Type | Computation |
|-------|------|-------------|
| `loudness_lufs` | float\|None | RMS → LUFS approximation |
| `transient_ratio` | float\|None | peak / moving-RMS mean (100ms windows) |
| `stereo_width` | float\|None | 1 - abs(correlation_lr) |
| `spectral_centroid_hz` | float\|None | FFT weighted mean frequency |
| `dc_offset` | float\|None | signal mean |
| `clip_count` | int | count of samples >= 0.999 |

### Verification

```text
vocal_folk.wav: loudness_lufs=-21.4, transient_ratio=7.35,
  stereo_width=0.278, centroid=4659Hz, dc=-9.6e-05, clips=0
```

### Files Modified

- `moodify-core-package/src/moodify/v01_types.py`: ScanResult +6 fields, to_dict() updated
- `moodify-core-package/src/moodify/v01_pipeline.py`: scan_audio() +40 lines (acoustic computation)

### Tests

12/12 existing tests pass (7 pipeline + 5 API v01).
