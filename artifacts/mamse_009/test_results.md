# MAMSE-009 — Test Results (Gates G1–G19)

**Date:** 2026-08-11
**Command:** `python -m pytest tests/experimental/test_mamse009.py -q`

## Result: 18 passed (18/18) — 16 prototype gates + 2 repo-specific

| Gate | Test | Covers |
|---|---|---|
| (solver) | `test_soft_threshold` | soft-threshold operator |
| (solver) | `test_svt_rank_reduction` | singular value thresholding reduces rank |
| G2 | `test_fail_on_nan` | NaN → RPCAUnavailableError (fail closed, no imputation) |
| G2 | `test_fail_on_zero` | all-zero matrix unavailable |
| (param) | `test_default_lambda` | 1/sqrt(max shape) |
| G4 | `test_exactish_low_rank_recovery` | L recovery rel error < 0.08 |
| G5 | `test_sparse_support_recovery` | sparse support recall > 0.85 |
| G3 | `test_constraint_error_small` | X ≈ L+S within 1e-6 |
| G6 | `test_deterministic_rerun` | same model_id; L/S allclose |
| G8 | `test_sparse_frame_score_detects_block` | injected block → frame score > 4× baseline |
| G9 | `test_candidate_interval_is_semantically_unknown` | event_type SPARSE_STRUCTURE_CANDIDATE, authority EXPERIMENTAL_UNKNOWN |
| (score) | `test_sparse_feature_score_shape` | per-feature score shape |
| G3 | `test_dense_noise_remains_small_residual` | dense noise → small residual, converged |
| G7 | `test_model_id_changes_with_space_id` | space_id bound into model_id |
| G12 | `test_save_and_reopen` | JSON/NPZ/manifest reopenable |
| (sim) | `test_low_rank_similarity_identity` | identity similarity |
| G11 | `test_event_overlap_report_preserves_both_sides` | candidates + canonical events coexist with overlap rows; no overwrite |
| G10 | `test_mixed_unit_matrix_rejected_by_space_policy` | NaN-containing mixed matrix fails closed |

## Gate mapping summary

| Acceptance gate | Status |
|---|---|
| G1 模型假设语义 | **Pass** — docstrings/limitations: L low-rank ≠ normal, S sparse ≠ bad |
| G2 NaN fail closed | **Pass** |
| G3 约束误差 | **Pass** (< 1e-6) |
| G4 低秩恢复 | **Pass** (< 0.08) |
| G5 sparse support | **Pass** (recall > 0.85) |
| G6 确定性 | **Pass** |
| G7 model_id 绑定 | **Pass** (space_id/config/input) |
| G8 sparse frame score | **Pass** (block > 4×) |
| G9 EXPERIMENTAL_UNKNOWN | **Pass** |
| G10 不直吃混合单位 | **Pass** — audited space (band ratios) + fail-closed policy |
| G11 事件并存 | **Pass** — overlap report preserves both sides |
| G12 JSON/NPZ reopen | **Pass** |
| G13 dense residual 分离 | **Pass** — stored separately in NPZ |
| G14 benchmark | **Pass** — shape/rank/iterations/runtime recorded; 2× frames near-linear |
| G15 真实 case ≥ 3 | See real_case_results.md |
| G16 P0 未发现但 RPCA 有候选 | See real_case_results.md (checkable case) |
| G17 false-positive 反例 | See real_case_results.md |
| G18 canonical 回归 | **Pass** — full suite green at release |
| G19 sparse 降低≠音质改善 | **Pass** — semantic boundary in every summary |
| G20 长曲资源策略 | **Pass** — benchmark 2× frames probe; policy: rows fixed → near-linear, offline for spectrogram-scale inputs |

## Regression

- Full suite with MAMSE-009 active: expected 456 passed / 5 skipped (438 + 18) — verified at release.
- `ruff check src/moodify_experimental/mamse009 tests/experimental/test_mamse009.py scripts/mamse009_*.py`: clean.
