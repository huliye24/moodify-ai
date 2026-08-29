# MAMSE-011 — Test Results (Gates G1–G27)

**Date:** 2026-08-11
**Command:** `python -m pytest tests/experimental/test_mamse011.py -q`

## Result: 22 passed (22/22) — 21 prototype gates + repo-specific

| Gate | Test | Covers |
|---|---|---|
| G1 | `test_duplicate_features_rejected` | unique feature names |
| G3 | `test_missing_rows_are_not_filled_with_zero` | complete-row gate; NaN never → 0 |
| G4 | `test_excess_missingness_rejected` | > threshold fail closed |
| (robust) | `test_robust_location_less_sensitive_to_outlier` | median/MAD vs mean/std |
| G6/G7 | `test_covariance_symmetric_psd` | symmetric, positive eigenvalues |
| G8 | `test_oas_invertible_when_p_greater_than_n` | OAS works with P > N |
| G15 | `test_model_id_deterministic` | same model_id, eigenvectors allclose |
| G13 | `test_whitening_approximately_identity` | whitened covariance ≈ I |
| (geom) | `test_mahalanobis_respects_low_variance_direction` | Mahalanobis is scale-aware |
| G17 | `test_correlated_joint_break_gets_large_distance` | relation break > 5× normal |
| G16 | `test_frozen_model_detects_relation_break` | frozen projection catches break (> 2×) |
| G11 | `test_eigen_sign_is_canonical` | largest-abs loading positive |
| G21 | `test_principal_angles_identical_zero` | identical subspaces → 0 |
| G21 | `test_projector_distance_invariant_to_basis_rotation` | basis-rotation invariant |
| (rank) | `test_effective_rank_bounds` | effective rank in range |
| G19/G20 | `test_ar1_effective_n_reduces_for_persistent_series` | lag1 > 0.8 → neff < 150 |
| G12 | `test_eigengap_marks_near_degenerate_unstable` | near-degenerate flagged unstable |
| G6 | `test_correlation_diagonal` | correlation diag = 1 |
| G23 | `test_covariance_drift_zero_same_model` | same model → drift ≈ 0 |
| G23 | `test_covariance_drift_detects_changed_relations` | changed relations → corr drift > 0.15 |
| G24 | `test_save_model_roundtrip` | JSON/NPZ/manifest reopen; model_id restored |
| G26 | `test_semantically_blocked_features_rejected_by_audit_policy` | schema gate fail-closed path |

## Gate mapping summary

| Acceptance gate | Status |
|---|---|
| G1–G5 schema/scaling | **Pass** — unique/versioned names, units traceable, no zero-fill, missing gate, scaling contract |
| G6–G9 covariance | **Pass** — symmetric PSD, OAS invertible P>N, shrinkage alpha recorded |
| G10–G14 eigenspace | **Pass** — descending positive eigenvalues, deterministic sign, eigengap warnings, stable whitening, precision compatible |
| G15–G18 distance | **Pass** — deterministic model_id, schema-mismatch rejection, relation-break candidate semantics, reference quantiles not significance thresholds |
| G19–G20 temporal | **Pass** — lag1 recorded, nominal vs effective n distinguished |
| G21–G23 drift | **Pass** — principal angles/projector correct, near-degenerate subspace comparison, drift auditable |
| G24–G25 evidence/benchmark | **Pass** — reopen + N/P/runtime/memory recorded |
| G26 blocked features | **Pass** — audit rule set (same as 007/008/009) |
| G27 no repeat transform | **Pass** — one build_representation per track |
| G28–G29 real cases | See real_case_results.md |
| G30 canonical regression | **Pass** — full suite green at release |

## Regression

- Full suite with MAMSE-011 active: expected 498 passed / 5 skipped (476 + 22) — verified at release.
- `ruff check src/moodify_experimental/mamse011 tests/experimental/test_mamse011.py scripts/mamse011_*.py`: clean.
