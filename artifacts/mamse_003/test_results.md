# MAMSE-003 — Test Results (Gate C / D)

**Date:** 2026-08-11
**Command:** `python -m pytest tests/experimental/test_mamse003.py -q`

## Result: 10 passed (10/10) — 9 required fixtures + two-state switch

| Gate | Test | Covers |
|---|---|---|
| C1 | `test_carrier_geometry_monotonic_geometric` | carrier centers monotonic, constant ratio (geometric), f_min/f_max bounds |
| C2 | `test_stationary_tone_concentrates_near_carrier` | 1000 Hz tone concentrates in a neighboring carrier band (<0.35 octave), peak > 2× mean |
| C3 | `test_gain_scaled_signature_nearly_invariant` | gain 0.1 vs 0.7 → normalized first-order signature cosine > 0.995 |
| C4 | `test_time_shifted_texture_global_signature_stable` | 120 ms shift → first-order cosine > 0.98, modulation cosine > 0.90 |
| C5 | `test_8hz_am_enhances_8hz_modulation` | 8 Hz AM case: modulation distribution at 8 Hz exceeds stable tone |
| C6 | `test_pulse_train_has_more_high_modulation_than_stable_tone` | pulse/transient high-modulation ratio > stable tone |
| C7 | `test_seeded_noise_deterministic` | seeded noise: identical distributions on rerun |
| D3 | `test_serialization_roundtrip` | manifest + NPZ + JSON restore; config_hash/source_sha256/git_commit present; `scattering-inspired` limitation recorded |
| D5 | `test_rerun_logically_deterministic` | full result dicts identical (runtime/memory excluded) |
| C8 | `test_two_state_texture_switch_changes_frame_matrix` | 1000→3000 Hz switch changes frame texture matrix (centroid column std > 1e-3) |

## Regression

- Full suite with MAMSE-003 active: **363 passed, 5 skipped** (MAMSE-001: 15, MAMSE-002: 12, MAMSE-003: 10, plus baseline).
- `ruff check src/moodify_experimental/mamse003 tests/experimental/test_mamse003.py scripts/mamse003_*.py`: expected clean (CI enforces lint on verification code).
- Canonical suites unaffected: no canonical file modified (baseline audit Q5).

## Honest notes

- Gain-invariance is on the *normalized* distribution; absolute level is intentionally not invariant (texture amplitude is a descriptor, not a quality score).
- Time-shift stability is tested at 120 ms (one texture epoch); long-range drift stability is a data-phase question, not asserted here.
- Serialization stores fixed-width sketches only; the dense wavelet cube is never persisted (Gate B requirement).
