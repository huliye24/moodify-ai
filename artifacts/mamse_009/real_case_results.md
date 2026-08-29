# MAMSE-009 — Real Case Results (empty-set negative, honest)

**Date:** 2026-08-11
**Sources:** 3 operator-owned AI pilot tracks (same files as MAMSE-001..008, rights_ok=true).
**Scope:** Two audited input spaces tested: (a) S1 band-energy ratios (8 columns, canonical plane), (b) 99-bin log-frequency linear power surface (decimated ×16, single coherent space). No threshold tuning was performed to force candidates.

## Results

| Case | Space | Frames | Iter | Rank_L | Sparsity_S | Candidates | Canonical events |
|---|---|---|---|---|---|---|---|
| 9056391 harmonic | band ratios | 1282 | 33 | 5 | 0.819 | **0** | 46 |
| 9961e07 transient | band ratios | 1840 | 33 | 6 | 0.801 | **0** | 95 |
| 7b3f021 AI | band ratios | 1976 | 33 | 5 | 0.820 | **0** | 51 |
| 9056391 (probe) | power surface 99×1506 | 38 | 54/99 | 0.765 | **0** | — |

Sparse frame score on the power surface: median 0.577, max 0.998, max robust z ≈ 1.07 (threshold z ≥ 6) — no frame approaches the candidate gate.

## Technical observations (honest negative)

1. **IALM-PCP produces NO sparse-structure candidates on these tracks in either audited space.** This is a real finding, not a tuning failure: the sparse component covers 76–82% of matrix cells (sparsity_S), i.e. S is NOT sparse on these dense productions.

2. **The low-rank assumption is weak here**: rank_L = 54 of 99 rows on the power surface. The X = L + S model does not separate these dense AI mixes into a low-rank background + sparse deviation — the whole matrix is high-rank and locally dense.

3. **G16 (P0-rule-absent but RPCA-candidate case) is NOT met** on this corpus. Recording it as an empty set rather than manufacturing a candidate by lowering thresholds (violating the no-tuning rule). The September data experiment with a broader corpus (including non-AI material and known-artifact tracks) is where G16 can be exercised.

4. **G17 (false-positive example)**: trivially zero false positives at the empty-candidate operating point — but that is because there are zero positives; the honest record is "no FP, no TP in this corpus".

5. Runtime is negligible (0.03–0.07 s band-ratio; ~2 s decimated power surface) and long-track cost is near-linear (benchmark 2× frames probe).

## Verdict

The operator runs correctly and deterministically, but on this corpus the sparse-anomaly hypothesis does not engage. This is exactly the kind of result the task's semantic boundaries demand be recorded rather than glossed: sparse component is NOT "bad audio", and its absence here does NOT mean "no anomalies" — it means the X = L + S separation is not informative for these dense productions in the audited spaces. Upgrade condition F (stable checkable candidates beyond rule coverage) is not met; the operator stays research with this negative documented.
