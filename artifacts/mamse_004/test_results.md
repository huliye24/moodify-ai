# MAMSE-004 — Test Results (Gates A–E)

**Date:** 2026-08-11
**Command:** `python -m pytest tests/experimental/test_mamse004.py -q`

## Result: 13 passed (13/13) — 10 required gates + 3 extras

| Gate | Test | Covers |
|---|---|---|
| A1/A2/A3 | `test_g1_pure_delay_constant_group_delay` | rad/s axis, seconds output; pure delay 1.75 ms recovered within 2 µs |
| A5 | `test_g2_wrap_invariance` | adding 2π to phase bins does not change group delay |
| A4 | `test_g3_linear_phase_curvature_near_zero` | linear phase → curvature < 1e-12 (99th pct) |
| B1 | `test_g4_low_magnitude_mask` | bins 100 dB below peak masked; frames with zero energy fully masked |
| C2 | `test_g5_stereo_delay_recovers_sign_and_magnitude` | 0.5 ms right-channel delay recovered (positive, ±0.12 ms) |
| C2 (scale) | `test_g5b_larger_delay_magnitude_scales` | 2.5 ms delay recovered (±0.3 ms) |
| C3 | `test_g6_gcc_phat_known_delay` | GCC-PHAT recovers 31-sample delay within 1 sample |
| C1/C4 | `test_g7_mono_unavailable_stereo` | mono input: ipd_available=False, all stereo values None |
| D4 | `test_g8_deterministic` | logical_json identical; arrays allclose (NaN-aware) |
| D3 | `test_g9_serialization_roundtrip` | evidence JSON + NPZ + manifest; load_result restores config_hash/source/gd arrays |
| D5 | `test_g10_runtime_roughly_bounded_linear` | 2× duration < 6× runtime bound |
| B3/B4 | `test_silence_honesty` | silence: valid_bin_ratio ≈ 0, medians None — nothing fabricated |
| B3 | `test_short_signal_behavior` | signal shorter than n_fft: UNAVAILABLE with reason, no crash |

## Gate mapping summary

| Acceptance gate | Status |
|---|---|
| A. 数学正确性 (A1–A5) | **Pass** — rad/s axis, unwrap-before-derivative, delay tolerance, curvature ≈ 0, wrap invariance |
| B. 可靠性 (B1–B4) | **Pass** — relative floor mask + zero-energy frames masked, valid ratio always explicit, silence/short/mono UNAVAILABLE semantics, None in JSON (never 0) |
| C. Stereo cross-check (C1–C4) | **Pass** — R*conj(L) convention fixed, positive delay recovered at two magnitudes, GCC-PHAT agrees, disagreement field exists and is never silently resolved |
| D. Engineering (D1–D6) | **Pass** — canonical stereo.py untouched (baseline audit), experimental namespace, JSON+NPZ roundtrip, deterministic, linear runtime, no NN dependency |
| E. Evidence | See release gate + real cases |

## Regression

- Full suite with MAMSE-004 active: expected 376 passed / 5 skipped (363 + 13) — verified at release.
- `ruff check src/moodify_experimental/mamse004 tests/experimental/test_mamse004.py scripts/mamse004_*.py`: clean.
