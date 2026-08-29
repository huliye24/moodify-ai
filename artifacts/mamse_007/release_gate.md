# MAMSE-007 — Release Gate

**Date:** 2026-08-11
**Verdict:** `EXPERIMENTAL_ACCEPTED` — PCA/SVD auditory state decomposition operator, off by default, **R2 VERIFIED** (per the task completion definition). R3 requires real ProductionCase evidence with a frozen corpus basis (September data experiment); R4 is product adoption.

## Acceptance gates G1–G14

| Gate | Status | Evidence |
|---|---|---|
| G1 数学正确性 | **Pass** — exact SVD, non-increasing singular values, valid ratios | tests |
| G2 低秩恢复 | **Pass** — rank-3 synthetic cum > 0.90 | tests |
| G3 重构单调性 | **Pass** | tests |
| G4 单位尺度 | **Pass** — robust scaling versioned; no Hz domination | tests |
| G5 Missing honesty | **Pass** — explicit imputation mask; threshold drop; NaN never → 0 | tests |
| G6 Degenerate feature | **Pass** — constant columns dropped | tests |
| G7 Deterministic sign | **Pass** — largest-abs-loading-positive rule in basis metadata | tests |
| G8 Basis identity | **Pass** — deterministic basis_id; schema mismatch fails closed | tests |
| G9 Frozen projection | **Pass** — projection never refits center/scale/components | tests |
| G10 Out-of-subspace | **Pass** — synthetic orthogonal anomaly > 2× median residual; CANDIDATE semantics only | tests |
| G11 Semantic preflight | **Pass** — both audited blockers (S1 mid/side energy, S2 short_term_lufs) identified and excluded in repo + real cases | tests + `real_case_results.md` |
| G12 Serialization | **Pass** — JSON basis round-trip, NPZ reload, manifest with runtime identity | tests |
| G13 Resource | **Pass** — exact SVD on D≤14 in ms; benchmark records N/D/K/time/memory/artifact size | `benchmark.json` |
| G14 Product boundary | **Pass** — research API only; no quality score; no canonical authority change | operator limitations |

## Constraints honored (CODEX MUST NOT / MUST)

1. `ProductionCase` lifecycle untouched; no second lifecycle.
2. PCA explained variance never a quality score; PCA never replaces true-peak/clipping/phase-risk authorities.
3. CASE_LOCAL coordinates never compared across cases (marked `cross-case non-comparable` in interpretation limits).
4. Frozen projection never silently refits.
5. NaN never becomes physical 0 (mask + imputation evidence).
6. The audited representation semantic conflicts are **recorded and excluded, not fixed** (baseline audit + preflight rules; separate canonical change program required).
7. No synthetic threshold written into production judgment.
8. Exact NumPy SVD = v0.1 reference; deterministic sign canonicalization; feature schema + order + version bound by hash; all imputation/drop/scale-fallback decisions leave evidence.
9. Operator in experimental namespace, off the canonical default path.

## Honest negatives

1. No CORPUS_FROZEN basis exists yet — cross-case projection is deferred to September.
2. Real-case residuals are unthresholded (G10 semantics validated synthetically only).
3. Band-ratio simplex constraints recorded, not CLR-transformed (Risk C).
4. The AI case's multi-dimensional state space (PC1 35.7%) is descriptive; no AI-detection claim.
5. 8/12 retained features are UNRESOLVED semantics (allowed exploratory with recorded UNIT_UNRESOLVED); a frozen corpus basis must only accept confirmed-semantics columns.

## Maturity

```text
R0 Theory        ✅ task docs + principle PDF + repo integration audit
R1 Operator      ✅ experimental implementation runs (numpy/scipy, no new dep)
R2 Verified      ✅ 16/16 gates, G1-G13 pass -> R2 VERIFIED
R3 Case Proven   ⏸ September: frozen corpus basis + calibrated residuals
R4+              ⏸ product coupling (research API only today)
```

## Outstanding (non-blocking)

1. September: corpus-fit frozen basis, 10-song pilot projection, residual calibration, cross-operator tables.
2. Canonical semantic patch for S1 mid/side energy and S2 short_term_lufs (separate change program, per CODEX).
3. CLR/ILR handling for compositional band ratios if corpus analysis demands it.
