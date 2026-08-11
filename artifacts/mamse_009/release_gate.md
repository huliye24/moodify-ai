# MAMSE-009 — Release Gate

**Date:** 2026-08-11
**Verdict:** `EXPERIMENTAL_ACCEPTED` — Robust-PCA / sparse-anomaly evidence operator, off by default, **R2 VERIFIED (synthetic) with real-case G16/G17 documented as empty-set negatives**. The upgrade condition (F) — stable checkable candidates beyond rule coverage — is NOT met on this corpus and the operator stays research.

## Acceptance gates G1–G20

| Gate | Status | Evidence |
|---|---|---|
| G1 X=L+S 是模型假设 | **Pass** — docstrings + semantic boundary in every summary |
| G2 NaN fail closed | **Pass** — no imputation in v0.1 |
| G3 约束误差 | **Pass** (< 1e-6 synthetic) |
| G4 低秩恢复 | **Pass** (< 0.08 synthetic) |
| G5 sparse support | **Pass** (recall > 0.85 synthetic) |
| G6 确定性 | **Pass** |
| G7 model_id 绑定 | **Pass** (space_id/config/input) |
| G8 sparse frame score | **Pass** (injected block > 4×) |
| G9 EXPERIMENTAL_UNKNOWN | **Pass** |
| G10 不直吃混合单位 | **Pass** — audited spaces only |
| G11 事件并存 | **Pass** — overlap report implemented and tested; on-corpus it reports zero overlaps (no candidates) |
| G12 JSON/NPZ reopen | **Pass** |
| G13 dense residual 分离 | **Pass** |
| G14 benchmark | **Pass** — shape/rank/iterations/runtime + 2×-frames long-track probe (near-linear) |
| G15 真实 case ≥ 3 | **Pass** — 3 cases × 2 audited spaces run |
| G16 P0 未发现但 RPCA 有候选 | **NOT MET** — empty candidate set on this corpus (honest negative; no threshold tuning to force a hit) |
| G17 false-positive 反例 | **Recorded** — zero FP at the zero-TP operating point; no FP, no TP |
| G18 canonical 回归 | **Pass** — full suite green (456) |
| G19 sparse 降低≠音质改善 | **Pass** — semantic boundary; A/B gain-claims prohibited |
| G20 长曲资源策略 | **Pass** — benchmark probe; rows-fixed → near-linear; spectrogram-scale inputs offline |

## Constraints honored

1. Canonical event semantics untouched — `SPARSE_STRUCTURE_CANDIDATE` not added to `DOMAINS`; overlap reports coexist without overwrite.
2. No mixed-unit raw matrix input (audited spaces: band ratios, linear power).
3. Sparse component never named defect/artifact; candidate authority EXPERIMENTAL_UNKNOWN.
4. No quality interpretation of sparse changes; no "less sparse = better" anywhere.

## Honest negatives

1. **Corpus-level empty candidate set** — the X=L+S model does not engage on these dense AI productions (rank_L 54/99, sparsity_S 0.77–0.82). This is a finding about the model-corpus match, not a tuning artifact.
2. G16 not met; upgrade condition F not satisfied; operator remains research.
3. Zero candidates means zero false positives — recorded as such, not as validation.

## Maturity

```text
R0 Theory        ✅ task docs + principle PDF
R1 Operator      ✅ IALM-PCP runs (numpy/scipy)
R2 Synthetic     ✅ 18/18 gates, G1-G14 pass
R3 Case Proven   ⏸ NOT met on this corpus (G16 empty); September data experiment with broader corpus
R4+              ⏸ product coupling
```

## Outstanding (non-blocking)

1. September: broader corpus (non-AI material, known-artifact tracks) to exercise G16/G17.
2. Alternative input spaces (spectral flatness / residual of canonical model) if the low-rank assumption is to be tested further.
3. Long-track spectrogram-scale PCP: offline policy only until a proximal/online variant is evaluated.
