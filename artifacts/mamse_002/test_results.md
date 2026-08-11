# MAMSE-002 — Test Results (T5)

**Date:** 2026-08-11
**Command:** `python -m pytest tests/experimental/test_mamse002.py -q`

## Result: 12 passed (12/12) — 10 required gates + 2 extras

| Gate | Test | Covers |
|---|---|---|
| A | `test_frequency_grid_constant_ratio` | f[k+1]/f[k] = 2^(1/24), rtol 1e-9 |
| A | `test_octave_and_semitone_spacing` | octave = 24 bins, semitone = 2 bins |
| A | `test_nominal_window_support_decreases_with_frequency` | support low > A4 > high |
| B | `test_a4_440hz_localization_within_35_cents` | 440 Hz within 35 cents |
| B | `test_a3_to_a4_octave_shift_24_bins` | 220→440 peak shift ≈ 24 bins |
| B | `test_440_to_a_sharp_4_shift_2_bins` | 440→466.16 shift ≈ 2 bins |
| B | `test_a1_a_sharp1_low_register_pair` | 55 + 58.27 Hz both resolved in low register |
| B | `test_silence_honesty` | SILENCE status, no dominant claim, all-NaN sketch |
| B | `test_deterministic_rerun` | identical power arrays + stable config hash |
| B | `test_serialization_round_trip` | manifest + NPZ + evidence restore identical |
| B | `test_tuning_offset_ladder_consistent` | +10-cent offset estimated closer to +10 than -10 |
| B | `test_low_register_resolution_beats_linear_bin` | 55/58.27 separated by CQT where 93.75 Hz linear bins cannot |

## Regression

- Full suite: see release gate (run with MAMSE-002 active).
- `ruff check src/moodify_experimental tests/experimental`: expected clean (verified per commit).
- MAMSE-001 suite unaffected: 15 tests remain green.
