# MAMSE-003 — Payload Size Report (Gate D/E)

**Date:** 2026-08-11
**Question:** how much is persisted per case, and how does that compare with the dense wavelet cube the operator computes in memory.

## Per-case persisted artifact (fixed-width sketch only)

| Case | manifest.json | texture.json | texture.npz | Total | Frames (500 ms / 250 ms hop) |
|---|---|---|---|---|---|
| case_9056391_harmonic (128.5 s) | 2.0 KB | 1.8 KB | 19.9 KB | **23.7 KB** | 513 |
| case_9961e07_transient (184.3 s) | 2.0 KB | 1.8 KB | 27.6 KB | **31.4 KB** | 736 |
| case_7b3f021_ai (198.0 s) | 2.0 KB | 1.8 KB | 29.4 KB | **33.2 KB** | 790 |

NPZ content: first-order distribution (27), temporal CV (27), modulation distribution (5), frame texture matrix (N×4), frame starts/ends, carrier centers, modulation rates.

## Dense vs sketch

The operator's in-memory intermediate is the complex carrier cube `(27 bands × N samples) @ complex128`:

| Case | Dense intermediate | Persisted sketch | Ratio |
|---|---|---|---|
| 9056391 | ~1,271 MB | 23.7 KB | ~54,000× |
| 9961e07 | ~1,822 MB | 31.4 KB | ~57,000× |
| 7b3f021 | ~1,957 MB | 39.6 KB (max run) | ~49,000× |

The dense cube is never written to disk (Gate B: "full wavelet cube 非默认 artifact"). The persisted sketch is a fixed-width summary whose size scales with frames × 4 features, not with n_fft or bandwidth.

## Notes

- Frame positions are stored on the original sample clock, so overlaying on S1/S2 windows costs nothing extra.
- Benchmark and pair artifacts (JSON only) add < 20 KB per run.
- If full NPZ frame matrices ever need denser time resolution, the size grows linearly with frame count (e.g., doubling frames doubles the NPZ); no superlinear growth exists in the persisted path.
