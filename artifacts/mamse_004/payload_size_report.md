# MAMSE-004 — Payload Size Report (E4)

**Date:** 2026-08-11
**Question:** what is persisted per case, and how does that compare with the full-resolution arrays the operator computes.

## Full-resolution intermediates (analysis only, never persisted)

For a 128–198 s track at 48 kHz, n_fft 8192 / hop 2048, band 80–18000 Hz (~3059 bins):

| Array [frames × bins] | Frames | Bytes (float64) |
|---|---|---|
| group_delay_s | 3009–4636 × 3059 | 74–113 MB |
| phase_curvature_s2 | same | 74–113 MB |
| ipd_rad (stereo) | same | 74–113 MB |
| interchannel_delay_s (stereo) | same | 74–113 MB |
| valid masks | same | 9–14 MB |
| **Total** | | **~310–470 MB** |

An early draft persisted these as-is → **420 MB NPZ per case** (uncompressed ~630 MB). That violates the MAMSE-series dense-not-persisted principle (MAMSE-002 5 MB, MAMSE-003 33 KB payloads).

## Persisted sketch (v0.1 final)

`save_result` decimates every 2D array to ≤ 512 frames × ≤ 1024 bins and stores float32 (masks stay bool), recording `sketch_full_shape` and `decimation` factors in the NPZ so the sketch is self-describing:

| Case | NPZ (decimated sketch) | JSON (manifest + evidence) | Total |
|---|---|---|---|
| case_9056391_harmonic | 7.37 MB | 3.4 KB | 7.37 MB |
| case_9961e07_transient | 7.11 MB | 3.4 KB | 7.11 MB |
| case_7b3f021_ai | 6.87 MB | 3.4 KB | 6.87 MB |

Ratio vs full-resolution: **~45× smaller** (420 MB → 7 MB). JSON carries all statistics (valid ratio, medians, MAD, p95, curvature, GCC-PHAT, disagreement); the NPZ carries the decimated 2D sketch for machine reuse.

## Notes

- Decimation is uniform (every k-th frame/bin); no aggregation bias is hidden, the factors are explicit in the NPZ.
- If a case ever needs full-resolution phase evidence, re-running the operator is deterministic (same input + config → same result); the sketch is a cacheable summary, not a lossy authority.
- Benchmark (10/30/45 s) NPZ outputs land in the benchmark workdir only when explicitly requested; the benchmark JSON itself is < 3 KB.
