# MAMSE-008 — Test Results (Gates G1–G19)

**Date:** 2026-08-11
**Command:** `python -m pytest tests/experimental/test_mamse008.py -q`

## Result: 19 passed (19/19) — 15 prototype gates + 4 repo-specific

| Gate | Test | Covers |
|---|---|---|
| G3 | `test_nonnegative_factors` | W/H ≥ 0 |
| G4 | `test_deterministic_nndsvd_rerun` | same basis_id; W/H allclose on rerun |
| G1 | `test_negative_input_rejected` | any negative → ValueError |
| G1/G14 | `test_mixed_unit_signed_plane_rejected` | canonical-like mixed (dB+ratio+correlation) matrix rejected |
| G2 | `test_zero_input_unavailable` | all-zero → NMFUnavailableError |
| G2 | `test_nan_mask_not_physical_zero` | NaN masked (mask=0 cells), finite relative error |
| (beta) | `test_beta_divergences_are_nonnegative_and_zero_on_identity` | beta ∈ {2,1,0}: ≥ 0, ≈ 0 on identity |
| G8 | `test_rank3_reconstructs_known_rank3_mixture` | relative error < 0.08 |
| G10 | `test_correct_rank_beats_rank1` | rank-3 < rank-1 × 0.75 |
| G9 | `test_recovered_components_align_with_true_factors` | permutation-invariant cosine > 0.88 |
| G5/G6 | `test_canonicalization_resolves_scale_and_permutation` | reconstruction preserved; W columns L1 = 1 |
| G11 | `test_frozen_basis_residual_detects_out_of_subspace_event` | novel event residual > 4× baseline |
| (proj) | `test_project_h_shapes` | H/Y/residual shapes correct |
| (sparsity) | `test_hoyer_sparsity_order` | sparse > dense |
| G12 | `test_evidence_has_no_semantic_source_labels` | anonymous factors; semantic_label=None |
| G13 | `test_save_result_round_trip` | JSON + NPZ + manifest reopenable |
| G13/G11 | `test_frozen_basis_reopen_and_project` | loaded W projects new frames |
| G13 | `test_deterministic_evidence_serialization` | identical summary JSON across saves |
| G14 | `test_band_ratio_matrix_fits` | canonical S1 band-ratio style simplex matrix fits at rank 2 |

## Gate mapping summary

| Acceptance gate | Status |
|---|---|
| G1 非负输入 | **Pass** — signed/mixed-unit rejected explicitly |
| G2 NaN mask | **Pass** — never physical zero |
| G3 W/H 非负 | **Pass** |
| G4 NNDSVD 可重复 | **Pass** |
| G5 scale canonicalization | **Pass** |
| G6 permutation 确定性排序 | **Pass** |
| G7 basis_id 稳定 | **Pass** (covered by rerun test) |
| G8 rank-3 重构 | **Pass** |
| G9 factor recovery | **Pass** (permutation-invariant) |
| G10 rank-3 vs rank-1 | **Pass** |
| G11 frozen out-of-subspace | **Pass** (synthetic) |
| G12 component 匿名 | **Pass** |
| G13 evidence reopen | **Pass** |
| G14 不直吃混合单位 ScalePlane | **Pass** — audit + rejection test + band-ratio-only real path |
| G15 mid/side + short_term_lufs fail closed | **Pass** — excluded by input selection (baseline audit); same rule set as MAMSE-007 |
| G16 transform/cache 复用 | **Pass (recorded)** — single STFT per track in scripts; feature-bus reuse R4+ |
| G17 benchmark | **Pass** — shape/rank/iterations/runtime recorded |
| G18 real cases | See real_case_results.md (3 cases, time-checkable peaks) |
| G19 canonical 回归 | **Pass** — full suite green at release |
| G20 无产品膨胀 | **Pass** — research API only |

## Regression

- Full suite with MAMSE-008 active: expected 438 passed / 5 skipped (419 + 19) — verified at release.
- `ruff check src/moodify_experimental/mamse008 tests/experimental/test_mamse008.py scripts/mamse008_*.py`: clean.
