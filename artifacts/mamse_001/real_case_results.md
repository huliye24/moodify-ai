# MAMSE-001 — Real Case Results (T7)

**Date:** 2026-08-11
**Sources:** 3 operator-owned AI pilot tracks (rights_ok=true), full-length, 48 kHz stereo, downloaded from the Aliyun data node and verified via case manifest sha256 linkage (source files: `outputs/mamse001_sources/*.wav`; evidence: `artifacts/mamse_001/real_cases/`).

Selection based on pre-existing before-scan metrics (LRA / spectral centroid):

| Case | Profile | LRA (LU) | Centroid (Hz) | Duration (s) |
|---|---|---|---|---|
| case_9961e07_transient | transient-rich candidate | 9.0 | 823.6 | 184.3 |
| case_9056391_harmonic | sustained harmonic/vocal candidate | 4.53 | 504.5 | 128.5 |
| case_7b3f021_ai | AI track, high centroid | 6.75 | 979.3 | 198.0 |

## 1. Payload: sketch vs dense

Frame counts and compressed payload (fixed-width sketch, no dense spectrogram retained):

| Case | R0 frames / bytes | R1 | R2 | R3 frames / bytes |
|---|---|---|---|---|
| 9961e07 | 69117 / 5.25 MB | 17277 / 1.31 MB | 4317 / 328 KB | 1077 / 82 KB |
| 9056391 | 48192 / 3.66 MB | 12045 / 915 KB | 3009 / 229 KB | 750 / 57 KB |
| 7b3f021 | 74232 / 5.64 MB | 18555 / 1.41 MB | 352 KB | 1156 / 88 KB |

A dense R3 spectrogram would be ~32768 bins × 1156 frames ≈ 37.9M floats (~150 MB uncompressed); the sketch is ~2.3 MB per case total. Sketch cost is bounded by frames × 17 features, independent of n_fft.

## 2. Cross-resolution observations (technical only)

**Dominant-frequency median per resolution** reveals low-frequency structure invisible at fine resolution:

| Case | R0 dom (Hz) | R1 | R2 | R3 dom (Hz) |
|---|---|---|---|---|
| 9961e07 | 375.0 | 257.8 | 257.8 | 205.1 |
| 9056391 | 281.2 | 257.8 | 246.1 | 260.7 |
| 7b3f021 | 375.0 | 234.4 | 158.2 | 89.4 |

The AI case shows the largest spread (375 → 89 Hz): R3 resolves a low-frequency sustained component that R0's 93.75 Hz bin cannot represent meaningfully. This is incremental information over any single-resolution path.

**Max spectral-flux time localization** (after the silence-reference fix; see §5):

| Case | R0 time (ms) | R2 time (ms) | R3 time (ms) |
|---|---|---|---|
| 9961e07 | 18181 | 25813 | 512 |
| 9056391 | 128163 | 42368 | 41813 |
| 7b3f021 | 24325 | 30677 | 23211 |

Short windows localize sharp onsets (R0 18.2 s in the transient case); long windows anchor macro structure (R3 0.5 s in 9961e07 is the start-of-signal energy onset). The flux maxima do not coincide across resolutions — evidence that onset structure is resolution-dependent, not an artifact.

**Cross-resolution conflicts** (fine vs coarse dominant disagree by >500 Hz while the fine frame is energetic): 290 / 82 / 318 per case. Preserved as structured lists in `cross_resolution_evidence.json`; not averaged.

**Band-level cross-resolution spread** (median relative std across 4 resolutions on the coarsest timeline): sub band 0.69–0.90 in all cases — the lowest bands are the least stable across resolutions, consistent with bin-width effects at low frequency.

**Narrowband events (T9 interface output):** all three cases emit one `NARROWBAND_PERSISTENT_STRUCTURE` event spanning nearly the whole track (flatness < 0.15 threshold is loose for these dense AI productions; median dominant 89–258 Hz). Technical observation; threshold calibration is deferred to data-phase analysis, not claimed as a quality statement.

## 3. Incremental-value argument

- R3 reveals a dominant at 89 Hz (case 7b3f021) that no fine-resolution plane reports — a single-resolution system would miss or mislabel the low-frequency anchor.
- R0 localizes onsets at frame-granularity (~2.7 ms) while R3 frames span 683 ms — the two answer different questions; neither subsumes the other.
- Conflict counts (82–318/case) show fine/coarse disagreement is common, so collapsing to one spectrogram parameter would hide real structure.

No claim of artistic quality is made for any case.

## 4. Determinism and serialization

All evidence re-derived with the same code path; `mamse001_manifest.json` records git commit, Python/numpy/scipy/ffmpeg versions, FFT backend identity, resolution registry hash, window, and feature schema version. NPZ round-trip verified by test suite (T6 gate 8).

## 5. Numerical issue found and fixed during T7

Relative spectral flux exploded to ~2.4e18 in case 9056391: when the previous frame is silent, `sum(prev_mag) ≈ 0` makes the relative ratio meaningless. Fixed in `sketch.py` (silent previous frame → flux = 0; energy reference guard `1e-9`). All synthetic gates still pass; real-case values are now bounded (< 900 for the loudest onset).

## Verdict

Real-case evidence supports **R3 Case Proven**: the R-axis adds information over single-resolution paths, payload is bounded, and cross-resolution structure is preserved as evidence. No schema-breaking observations for the canonical S-axis.
