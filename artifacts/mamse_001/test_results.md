# MAMSE-001 — Test Results (T6)

**Date:** 2026-08-11
**Command:** `python -m pytest tests/experimental/test_mamse001.py -q`

## Result: 15 passed (15/15)

| Gate | Test | Covers |
|---|---|---|
| A | `test_bin_hz_traceable` | bin = sr / n_fft |
| A | `test_frame_center_maps_to_sample_clock` | frame centers on sample clock |
| A | `test_short_source_does_not_fake_r3` | short source → 0 frames, no fabricated R3 |
| A | `test_zero_padding_not_sold_as_resolution` | no dense retention |
| B | `test_stationary_1000hz_localization_r3_better_than_r0` | R3 err < R0 err |
| B | `test_close_tone_peak_gap_r3_better_than_r0` | 30 Hz gap resolved better at R3 |
| B | `test_impulse_temporal_localization_r0_better_than_r3` | R0 err < R3 err |
| B | `test_chirp_monotonic_trajectory_consistent_across_r` | rising trajectory at all R |
| B | `test_hf_cutoff_ladder_r2_r3_stable_response` | sharper cutoff → lower flatness (both R) |
| B | `test_silence_no_nan_inf_contamination` | no NaN/Inf, empty semantics |
| B | `test_deterministic_rerun` | byte-identical rerun + stable registry hash |
| B | `test_serialization_round_trip` | JSON/NPZ restore identical arrays |
| C | `test_no_dense_spectrogram_retained` | sketch bounded, no dense planes |
| C | `test_cross_resolution_conflicts_preserved_not_averaged` | conflicts listed, per-band spread |
| C | `test_resolution_ids_and_feature_schema_versioned` | R0–R3 ids, versioned schemas, canonical band source |

## Regression

- `tests/auditory/test_multiscale_representation.py`: **15 passed** (S-axis authority unaffected).
- `ruff check src/moodify_experimental tests/experimental`: **All checks passed**.
- Full suite: run as part of the release gate step (F-section).

## Fixes during test development

1. Impulse localization metric switched from spectral-flatness argmin to RMS argmax (impulse flatness is high, not low — the original assertion selected the wrong feature).
2. HF-cutoff assertion direction corrected: geometric-mean flatness *drops* as the cutoff sharpens (out-of-band bins approach zero).
3. Relative spectral flux exploded (~2.4e18) when the previous frame is silent; silent-prev → flux 0 guard added (found on real cases, T7 §5).
