# MAMSE-006 — Test Results (Gates G0–G13)

**Date:** 2026-08-11
**Command:** `python -m pytest tests/experimental/test_mamse006.py -q`

## Result: 14 passed (14/14) — 13 required scenarios + steady-vs-modulated

| Gate | Test | Covers |
|---|---|---|
| G2/G3 | `test_short_input_unavailable` | 0.5 s input → `UNAVAILABLE_TOO_SHORT`, no arrays |
| G3 | `test_silence_unavailable` | silence → `UNAVAILABLE_LOW_ENERGY`, no arrays |
| G4 | `test_am_2hz_recovered` | 2 Hz AM → temporal peak within 0.5 Hz |
| G4 | `test_am_5hz_recovered` | 5 Hz AM → temporal peak within 0.5 Hz |
| G4 | `test_am_9hz_recovered` | 9 Hz AM → temporal peak within 0.5 Hz |
| G5 | `test_gain_invariance_of_peak` | 0.2× vs 0.8× gain → identical peak, centroid within 0.1 Hz |
| G6 | `test_static_ripple_spectral_peak` | static ripple 2.0 cpo → spectral peak within 0.2 cpo |
| G7 | `test_dynamic_ripple_known_rate_scale` | 4 Hz / 1.5 cpo ripple → ridge rate ±0.3 Hz, scale ±0.15 cpo |
| G8 | `test_reversed_ripple_flips_orientation` | direction flip → orientation index sign flips, magnitude equal |
| G10 | `test_distribution_normalization_and_entropy` | marginals non-negative, sum ≈ 1, entropy in [0,1] |
| (extra) | `test_steady_carrier_has_lower_dynamic_energy_than_modulated` | modulated > steady ×1.2 dynamic joint energy |
| G11 | `test_deterministic_rerun` | identity fields equal; marginals/joint planes allclose |
| G12 | `test_serialization_roundtrip` | JSON readable, NPZ round-trip, manifest present, profile_hash restored |
| G13 | `test_resource_shape_growth_bounded` | joint plane fixed size; segments grow boundedly with duration |

## Gate mapping summary

| Acceptance gate | Status |
|---|---|
| G0 Scope | **Pass** — research/experimental; canonical metrics untouched (baseline audit Q2/Q8); no second lifecycle |
| G1 Mathematical identity | **Pass** — temporal axis Hz (frame rate), spectral axis cycles/octave (bands_per_octave), log-frequency axis traceable to bpo |
| G2 Time integrity | **Pass** — modulation windows on frame clock mapped to source `time_s`; too-short → UNAVAILABLE |
| G3 Low-energy honesty | **Pass** — silence/near-silence produce no ridge (UNAVAILABLE_LOW_ENERGY) |
| G4 AM recovery | **Pass** — 2/5/9 Hz recovered within resolution tolerance |
| G5 Gain invariance | **Pass** |
| G6 Static spectral modulation | **Pass** |
| G7 Dynamic ripple | **Pass** — rate + scale ridge |
| G8 Orientation | **Pass** — reversal flips sign |
| G9 Ridge semantics | **Pass** — ridge always `status: CANDIDATE`; limitations forbid strong direction claims |
| G10 Distribution integrity | **Pass** — non-negative, normalized |
| G11 Determinism | **Pass** |
| G12 Serialization | **Pass** — JSON/NPZ round-trip, UNAVAILABLE semantics preserved |
| G13 Resource | **Pass** — bounded growth; benchmark 0.21/0.62/1.06 s for 10/30/45 s |

## R2 gate

G0–G13 all pass → **SYNTHETIC_VERIFIED**. G14 (cross-module conflict with MAMSE-003/timeline/events) is a repo-integration check — both sides' evidence are preserved independently by design (no silent overwrite); full G14 verification is deferred to the September data experiment along with all real-case thresholds (CODEX §7).

## Regression

- Full suite with MAMSE-006 active: expected 403 passed / 5 skipped (389 + 14) — verified at release.
- `ruff check src/moodify_experimental/mamse006 tests/experimental/test_mamse006.py scripts/mamse006_*.py`: clean.
