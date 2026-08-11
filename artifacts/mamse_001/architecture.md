# MAMSE-001 — Architecture (T1/T2/T3/T9)

**Date:** 2026-08-11
**Status:** EXPERIMENTAL research operator — not part of the canonical production loop

## Placement

- Implementation: `moodify-core-package/src/moodify_experimental/mamse001/` (experimental namespace, installs as `moodify_experimental`, does not touch the canonical `moodify` package).
- Evidence: `artifacts/mamse_001/` (audit, synthetic, real-case, benchmark, payload, release gate).
- The task-package prototype (`src/mamse001/`) served as reference; the production implementation diverges where the task spec requires (evidence contract, canonical band import, flux numerical guard).

## Modules

| Module | Responsibility |
|---|---|
| `registry.py` | `ResolutionSpec` + `RESOLUTIONS` (R0 512/128, R1 2048/512, R2 8192/2048, R3 32768/8192, Hann) + deterministic `registry_hash()`. Versioned (`mamse-001-resolutions-v1`). |
| `stft.py` | Frame streaming (`iter_frames` emits only full frames), RFFT power spectrum, deterministic local-peak frequencies. |
| `sketch.py` | Fixed-width streaming sketch per resolution. Bands imported from canonical `moodify.auditory.representation.feature_registry.BANDS` — no competing band set. No dense spectrogram retained. |
| `evidence.py` | Manifest (operator/git/python/numpy/scipy/ffmpeg/FFT backend/registry hash), NPZ planes, cross-resolution evidence with conflict list, save/load/run_case. |
| `events.py` | T9 product-consumable interface: `NARROWBAND_PERSISTENT_STRUCTURE` events. No UI surface. |

## Data flow

```text
Decode once
  │
  ├── R0 frame stream ──RFFT──▶ sketch rows
  ├── R1 frame stream ──RFFT──▶ sketch rows
  ├── R2 frame stream ──RFFT──▶ sketch rows
  └── R3 frame stream ──RFFT──▶ sketch rows
              │
              ▼
       compressed NPZ (mamse001_planes.npz)
              │
              ▼
   cross-resolution evidence (conflicts preserved)
              │
              ▼
      manifest + events (evidence refs)
```

## Authority boundaries

- S-axis (semantic temporal scales S0–S3) untouched: `scales.py`, `build.py`, `feature_registry.py` unmodified.
- R-axis owns FFT kernel, resolution-specific observation, and cross-resolution conflict — it owns no ProductionCase lifecycle and no judgment authority.
- All R features are EXPERIMENTAL descriptors; none register in `measurement_registry_v1.yaml`.
- No execution-graph coupling: `execution/cache.py` exists but MAMSE-001 deliberately does not depend on canonical execution internals (deferred until R4+). FFT backend identity (numpy.fft.rfft + version) is recorded in every manifest.

## Resolution semantics

| R | n_fft | hop | bin (48 kHz) | window | Role |
|---|---|---|---|---|---|
| R0 TRANSIENT | 512 | 128 | 93.75 Hz | 10.7 ms | onsets, clicks, clipping edges |
| R1 LOCAL | 2048 | 512 | 23.4 Hz | 42.7 ms | local spectral state |
| R2 HARMONIC | 8192 | 2048 | 5.9 Hz | 170.7 ms | harmonic/narrowband structure |
| R3 MACRO | 32768 | 8192 | 1.46 Hz | 682.7 ms | low-frequency/close-frequency detail |

`Z(s, r, t, k)` — future combined representation keeps S for semantics and R for spectral kernel; not implemented here (no premature framework).
