# MAMSE-011 — Release Gate

**Date:** 2026-08-11
**Verdict:** `EXPERIMENTAL_ACCEPTED` — covariance/eigenspace operator, off by default, **R2 VERIFIED (synthetic)**. G29 (combinational-anomaly increment) is demonstrated once on real cases (9961e07) with two honest negatives; September corpus work is required to strengthen the evidence base before any upgrade consideration.

## Acceptance gates G1–G30

| Gate | Status | Evidence |
|---|---|---|
| G1–G5 schema/scaling | **Pass** | unique/versioned names; units traceable; no zero-fill; missing gate; scaling contract (median/MAD + winsor) |
| G6–G9 covariance | **Pass** | symmetric PSD; OAS P>N; shrinkage recorded (0.008–0.011 real) |
| G10–G14 eigenspace | **Pass** | descending positive eigenvalues; deterministic sign; eigengap warnings; stable whitening; precision compatible |
| G15–G18 distance | **Pass** | deterministic model_id; schema mismatch rejected; relation-break candidate semantics; quantiles not significance |
| G19–G20 temporal | **Pass** | lag1 (up to 0.96 real) + neff (as low as 2% of n) recorded — never IID assumption |
| G21–G23 drift | **Pass** | principal angles/projector correct; subspace comparison for near-degenerates; drift auditable (real cross-case 0.39–0.50) |
| G24–G25 evidence/benchmark | **Pass** | JSON/NPZ reopen; N/P/runtime/memory recorded (OAS ~9 ms on 1282×12) |
| G26 blocked features | **Pass** | mid/side + short_term_lufs excluded (same audit rule set as 007/008/009) |
| G27 transform reuse | **Pass** | one build_representation per track |
| G28 real cases ≥ 4 | **Partial** — 3 operator tracks + 1 injection scenario per track (4 case-scenarios); the package's fourth category (different AI generator/model version) is represented by the 3 distinct tracks + cross-case drift |
| G29 组合异常增量 | **Partially demonstrated** — 9961e07 relation-break injection: q99 fraction 0.016→0.134 (+0.117), marginals unchanged; two honest negatives (9056391 +0.091, 7b3f021 +0.049 below the +0.10 heuristic) |
| G30 canonical 回归 | **Pass** — full suite green (498) |

## Constraints honored (核心工程原则 + 科学边界)

1. Feature schema + scaling contract established BEFORE covariance (audit + gate).
2. Covariance ≠ causality; window samples not IID (lag1/neff evidence); Mahalanobis ≠ quality score; near-degenerate → subspace comparison; mixed-unit → scaling first; complete-row gate (no pairwise non-PSD).
3. No canonical measurement semantics changed; no product entry point.

## Honest negatives

1. G29 demonstrated once with threshold-dependent increment; two cases fell below the heuristic gate.
2. neff ≈ 2% of nominal n makes quantile-based fractions weak statistics — candidates only.
3. Cross-case drift large (0.39–0.50) — reference models are track/corpus-specific; no universal model claimed.
4. Injection flips one feature pair; broader relation-break scenarios are September work.

## Maturity

```text
R0 Theory        ✅ task docs + principle PDF
R1 Operator      ✅ covariance/eigenspace runs (numpy/scipy)
R2 Synthetic     ✅ 22/22 gates, G1-G27 pass
R3 Case Proven   ⏸ partial: one real relation-break increment; September corpus to strengthen
R4+              ⏸ product coupling
```

## Outstanding (non-blocking)

1. September: corpus-fit reference models, broader relation-break scenarios, G29 strengthening.
2. Frozen corpus reference + cross-case Mahalanobis normalization study.
3. Feature-bus transform/cache reuse (R4+).
