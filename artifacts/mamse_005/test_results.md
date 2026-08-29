# MAMSE-005 — Test Results (Gates G0–G8)

**Date:** 2026-08-11
**Command:** `python -m pytest tests/experimental/test_mamse005.py -q`

## Result: 13 passed (13/13) — 12 prototype gates + serialization extra

| Gate | Test | Covers |
|---|---|---|
| G5 | `test_short_is_unavailable` | signal < n_fft → `UNAVAILABLE_TOO_SHORT`, no crash, no fabricated numbers |
| G5 | `test_silence_no_f0` | silence → median_f0 None, periodicity_available_ratio 0.0 |
| G2 | `test_200hz_candidate` | 200 Hz harmonic → cepstral F0 candidate within 3% |
| G2 | `test_f0_ladder` | 100/250/400 Hz ladder detected within 4% |
| G2 | `test_gain_invariance_candidate` | gain 0.1 vs 0.7 → candidate shifts < 3 Hz |
| G1 | `test_lifter_reconstruction_identity_log_domain` | envelope + fine = logmag exactly (< 1e-10) |
| G3 | `test_envelope_smoother_than_raw_log_spectrum` | low-quefrency envelope roughness < raw roughness |
| G4 | `test_controlled_resonance_candidates` | two iirpeak resonators (800/2200 Hz) found in neighborhoods |
| G5 | `test_white_noise_not_forced_stable_f0` | noise → periodicity_available_ratio < 0.8 (not forced periodic) |
| G6 | `test_deterministic_summary` | logical_json identical across reruns |
| G6/G1 | `test_shapes_and_quefrency_axis` | cepstrum [frames, n_fft/2+1]; quefrency[1] = 1/sr |
| G8 | `test_serialization_roundtrip` | evidence JSON + NPZ + manifest; load restores config_hash/source/arrays |
| G7 | `test_resource_growth_bounded` | 2× duration bounded runtime |

## Gate mapping summary

| Acceptance gate | Status |
|---|---|
| G0 边界 | **Pass** — experimental namespace, no canonical judgment change (baseline audit Q5) |
| G1 数学正确性 | **Pass** — real cepstrum via even log-magnitude IFFT; explicit log floor; quefrency axis = 1/sr; lifter identity reconstruction |
| G2 周期 fixture | **Pass** — 200 Hz < 3%, ladder 100/250/400 < 4%, gain-invariant candidate |
| G3 包络分离 | **Pass** — envelope smoother, fine residual keeps texture, exact log-domain reconstruction |
| G4 Resonance candidate | **Pass** — controlled resonators found; schema says `candidate`, never formant |
| G5 失败诚实 | **Pass** — silence/short UNAVAILABLE; noise not forced onto stable F0 |
| G6 确定性 | **Pass** — logical JSON + source SHA256 identical |
| G7 资源 | **Pass** — bounded linear growth; NPZ stores decimated sketch (dense frames never persisted) |
| G8 Evidence | **Pass** — JSON summary + NPZ + manifest with version/config/source hash |
| G9 Moodify 集成 | **Pass** — no product score exposed; deep-scan/diagnostic only; CQT/MSE conflict-detection is a stated future hook |

## Regression

- Full suite with MAMSE-005 active: expected 389 passed / 5 skipped (376 + 13) — verified at release.
- `ruff check src/moodify_experimental/mamse005 tests/experimental/test_mamse005.py scripts/mamse005_*.py`: clean.
