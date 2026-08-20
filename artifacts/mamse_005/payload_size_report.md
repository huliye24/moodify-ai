# MAMSE-005 — Payload Size Report

**Date:** 2026-08-11
**Question:** what is persisted per case, and how does that compare with the full-resolution per-frame arrays.

## Full-resolution per-frame arrays (analysis only, never persisted)

For a 128–198 s track at 48 kHz, n_fft 4096 / hop 1024 (9280 frames max):

| Array [frames × bins] | Full size (float64) |
|---|---|
| cepstrum [9280 × 2049] | 152 MB |
| envelope_logmag [9280 × 2049] | 152 MB |
| fine_logmag [9280 × 2049] | 152 MB |
| f0/score/available/rms vectors | < 1 MB |
| **Total** | **~456 MB** |

## Persisted sketch (v0.1 final)

`save_result` decimates per-frame 2D arrays to ≤ 512 rows (float32; quefrency axis kept full for periodicity readability), recording `sketch_full_rows` and `decimation_rows` in the NPZ:

| Case | NPZ (decimated sketch) | JSON (manifest + evidence) | Total |
|---|---|---|---|
| case_9056391_harmonic | 10.75 MB | ~3 KB | 10.75 MB |
| case_9961e07_transient | 10.75 MB | ~3 KB | 10.75 MB |
| case_7b3f021_ai | 10.75 MB | ~3 KB | 10.75 MB |

Ratio vs full-resolution: **~42× smaller** (456 MB → ~11 MB). JSON carries the summary (availability, F0 candidate, periodicity ratio, roughness, fine/env ratio, resonance candidates); NPZ carries the decimated cepstrum/envelope/fine sketch for machine reuse.

## Notes

- The 2.5 ms lifter cutoff is the modeling boundary of the envelope/fine split and is part of the versioned config (config_hash).
- Decimation is uniform; factors are explicit in the NPZ (`decimation_rows`), no aggregation bias is hidden.
- Re-running is deterministic (same input + config → same result), so full-resolution evidence is always reproducible; the sketch is a cacheable summary.
- Benchmark (10/30/45 s) NPZ outputs are written only to the benchmark workdir and are excluded from the committed artifacts.
