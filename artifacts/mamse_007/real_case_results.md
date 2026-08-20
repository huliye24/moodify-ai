# MAMSE-007 — Real Case Results (CASE_LOCAL, recording only)

**Date:** 2026-08-11
**Sources:** 3 operator-owned AI pilot tracks (same files as MAMSE-001..006, rights_ok=true).
**Scope:** CASE_LOCAL PCA on canonical S1 planes (read-only via `build_representation`), semantic preflight applied, descriptors recorded only. No threshold, no cross-case comparison, no canonical judgment.

## Descriptors (S1 plane, 12 semantically-kept features, 3 PCs, CASE_LOCAL)

| Case | N windows | PC1 | PC2 | PC3 | Cum3 | Mean residual | Max residual | Runtime |
|---|---|---|---|---|---|---|---|---|
| 9056391 harmonic | 1282 | 0.934 | 0.038 | 0.014 | 0.986 | 5.76 | 100.6 | 7 ms |
| 9961e07 transient | 1840 | **0.999** | 0.000 | 0.000 | 1.000 | 4.85 | 28.6 | 9 ms |
| 7b3f021 AI | 1976 | **0.357** | 0.278 | 0.158 | 0.793 | 3.73 | 30.4 | 8 ms |

Semantic preflight excluded `mid_energy` and `side_energy` (SEMANTIC_CONFLICT: linear mean-square energy vs registry ratio semantics) in every case; the exclusion is recorded in each summary.

## Technical observations (recording only)

1. **CASE_LOCAL PC structure differs strongly across cases** — exactly why CASE_LOCAL bases are not cross-case comparable:
   - 9056391: single-dimension dominated (PC1 93.4%).
   - 9961e07: almost perfectly one-dimensional (PC1 99.9%) — its window-level state space is dominated by one latent direction (consistent with a level/energy axis; band ratios and RMS are highly collinear in a transient-dense track).
   - 7b3f021: genuinely multi-dimensional (PC1 35.7%, cum3 79.3%) — its 12-feature state space is more spread; no single axis explains the windows.

2. **The AI case's multi-dimensionality is a descriptive observation, not a detection claim.** One track cannot support any AI-vs-human statement (prohibited by the operator's limitations and CODEX §14 product boundary).

3. **Residuals** (standardized units): mean 3.7–5.8, max 28–101 (one harmonic-case spike segment). No threshold interpretation at v0.1; out-of-subspace semantics were validated only synthetically (G10).

4. **Runtime and payload are negligible**: ~8 ms SVD, 0.4–0.6 MB evidence per case (basis JSON + NPZ + manifest).

## Honest negatives

1. No frozen corpus basis exists yet — CORPUS_FROZEN projection across cases is deferred to the September data experiment (needs corpus-fit basis + schema governance).
2. Imputed cells = 0 in all cases (S1 planes have no missing values in these tracks); the imputation path is validated synthetically only.
3. mean/max residuals are recorded without thresholds; anomaly semantics need the September calibration.
4. The 12 kept features include 8 band ratios with compositional (simplex) constraints — recorded (Risk C), not CLR-transformed.

## Verdict

The operator integrates cleanly with the canonical representation layer (read-only), the semantic preflight correctly gates the audited conflicts, and runtime is negligible. Standing at **R2 VERIFIED**; R3 (case-proven) requires the September data experiment with a frozen corpus basis and calibrated residual thresholds.
