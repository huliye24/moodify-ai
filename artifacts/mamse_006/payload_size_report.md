# MAMSE-006 — Payload Size Report

**Date:** 2026-08-11
**Question:** what is persisted per case, and how does that compare with the full-resolution surfaces.

## Full-resolution surfaces (analysis only, never persisted)

| Array | Shape (full) | Bytes |
|---|---|---|
| auditory_surface_db [99 bands × up to 37110 frames] | float64 | ~29 MB |
| joint_power / dynamic_joint_power [99 × 512] | fixed by config window | ~0.8 MB each |
| time_s / log_frequency_hz vectors | | < 1 MB |
| **Total** | | **~31 MB** |

The joint plane size is fixed by the modulation window (4 s × 128 Hz frame rate = 512 frames); only the surface and segment count grow with duration.

## Persisted NPZ (v0.1 final)

`save_evidence` decimates the auditory surface along time to ≤ 2048 frames, recording `auditory_surface_decimation` and `auditory_surface_full_frames`:

| Case | NPZ | Total per case |
|---|---|---|
| case_9056391_harmonic | surface (99, 2008), decim 12 | 2.41 MB |
| case_9961e07_transient | surface (99, 2033), decim 17 | 2.47 MB |
| case_7b3f021_ai | surface (99, 1954), decim 19 | 2.42 MB |

Ratio vs full-resolution: **~13× smaller** (~31 MB → ~2.4 MB). The joint planes and marginals are stored at full resolution (they are config-fixed and small). JSON holds the summary; the manifest carries profile_hash/source/runtime identity.

## Notes

- Decimation is uniform along time only; the log-frequency axis stays complete.
- All modulation analysis runs on the full-resolution surface before persistence — the sketch is a cacheable summary, not a lossy authority; re-running is deterministic.
- Benchmark (10/30/45 s) NPZ outputs go to the benchmark workdir only and are excluded from committed artifacts.
