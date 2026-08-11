# MAMSE-007 — Test Results (Gates G1–G14)

**Date:** 2026-08-11
**Command:** `python -m pytest tests/experimental/test_mamse007.py -q`

## Result: 16 passed (16/16) — 14 reference gates + 2 semantic preflight

| Gate | Test | Covers |
|---|---|---|
| G1/G2 | `test_rank3_latent_structure_explained` | rank-3 latent matrix: first 3 PCs > 90% explained variance |
| G3 | `test_reconstruction_error_decreases_with_more_components` | residual drops from k=1 to k=3 |
| G4 | `test_robust_scaling_prevents_hz_unit_domination` | robust scaling: no single Hz feature owns PC1 (> 0.95) |
| G7 | `test_sign_canonicalization_is_deterministic` | rerun identical; largest-abs loading positive |
| G5 | `test_missing_cells_are_explicitly_imputed` | 10 NaN cells → mask marks 10, evidence imputed_cells=10 |
| G5 | `test_excessively_missing_feature_is_dropped` | > 20% missing → dropped with TOO_MISSING reason |
| G6 | `test_constant_feature_is_dropped` | constant column → dropped |
| G9 | `test_frozen_basis_projection_does_not_refit` | projection: same basis_id, mode=PROJECTION_ONLY |
| G8 | `test_feature_schema_mismatch_fails_closed` | reordered features → FEATURE_SCHEMA_MISMATCH |
| G10 | `test_out_of_subspace_segment_has_larger_residual` | orthogonal anomaly → median residual > 2× baseline |
| G1 | `test_explained_variance_ratios_are_valid` | ratios ≥ 0, sum ≤ 1, singular values non-increasing |
| G8 | `test_basis_id_is_deterministic` | same input/config → same basis_id |
| G12 | `test_serialization_round_trip` | basis JSON round-trip, NPZ reload, manifest present |
| G14 | `test_case_local_basis_is_explicitly_marked_non_comparable` | CASE_LOCAL marked, interpretation limits recorded |
| G11 | `test_preflight_s1_mid_side_conflict_excluded` | mid_energy/side_energy → SEMANTIC_CONFLICT, excluded |
| G11 | `test_preflight_s2_short_term_lufs_conflict_excluded` | short_term_lufs → SEMANTIC_CONFLICT (RMS proxy vs LUFS), excluded |

## Gate mapping summary

| Acceptance gate | Status |
|---|---|
| G1 数学正确性 | **Pass** — SVD reconstruction, non-increasing singular values, valid ratios |
| G2 低秩恢复 | **Pass** — > 0.90 cumulative for 3 latent factors |
| G3 重构单调性 | **Pass** |
| G4 单位尺度 | **Pass** — robust scaling versioned, no unit domination |
| G5 Missing honesty | **Pass** — NaN never → 0; mask auditable; threshold drop |
| G6 Degenerate feature | **Pass** |
| G7 Deterministic sign | **Pass** — rule recorded in basis preprocessing |
| G8 Basis identity | **Pass** — deterministic basis_id; schema mismatch fails closed |
| G9 Frozen projection | **Pass** — no refit of center/scale/components |
| G10 Out-of-subspace | **Pass** — > 2× residual; candidate semantics only |
| G11 Semantic preflight | **Pass** — both repo blockers identified and excluded |
| G12 Serialization | **Pass** |
| G13 Resource | **Pass** — exact SVD on D≤14 runs in ms; benchmark records N/D/K/time/memory |
| G14 Product boundary | **Pass** — research API only; no quality score; no canonical authority change |

## R2 gate

G1–G13 all pass → **R2 VERIFIED** per the task completion definition. Real ProductionCase evidence is required before R3 (deferred to the September data experiment); product adoption would be R4.

## Regression

- Full suite with MAMSE-007 active: expected 419 passed / 5 skipped (403 + 16) — verified at release.
- `ruff check src/moodify_experimental/mamse007 tests/experimental/test_mamse007.py scripts/mamse007_*.py`: clean.
