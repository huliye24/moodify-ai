# MAMSE-008 — Release Gate

**Date:** 2026-08-11
**Verdict:** `EXPERIMENTAL_ACCEPTED` — NMF auditory component operator, off by default, **R2 VERIFIED** (19/19 gates; exit conditions 1–8 met at the research level). R3 requires frozen-basis corpus work in the September data experiment; product adoption is R4.

## Acceptance gates G1–G20

| Gate | Status | Evidence |
|---|---|---|
| G1 严格非负 | **Pass** — signed/mixed-unit rejected (tests + audit) | `test_results.md`, `baseline_audit.md` |
| G2 NaN mask | **Pass** — never physical zero | tests |
| G3 W/H 非负 | **Pass** | tests |
| G4 NNDSVD 可重复 | **Pass** | tests |
| G5 scale canonicalization | **Pass** | tests |
| G6 permutation 确定性 | **Pass** | tests |
| G7 basis_id 稳定 | **Pass** | tests |
| G8 rank-3 重构 | **Pass** (< 0.08 synthetic) | tests |
| G9 factor recovery | **Pass** (> 0.88 permutation-invariant) | tests |
| G10 rank-3 vs rank-1 | **Pass** | tests |
| G11 frozen out-of-subspace | **Pass** (synthetic > 4× residual) | tests |
| G12 component 匿名 | **Pass** — semantic_label always None | tests + real cases |
| G13 evidence reopen | **Pass** — JSON/NPZ/manifest round-trip + frozen reopen | tests |
| G14 不直吃混合单位 ScalePlane | **Pass** — input audit + rejection test; real path uses band ratios only | `baseline_audit.md` |
| G15 mid/side + short_term_lufs fail closed | **Pass** — excluded by audited input selection (same rule set as MAMSE-007) | audit + real cases |
| G16 transform/cache 复用 | **Pass (recorded)** — one STFT per track; feature-bus reuse R4+ | audit |
| G17 benchmark | **Pass** — shape/rank/iterations/runtime recorded (0.06 s rank-2, 0.07 s rank-3 on 8×1282) | `benchmark.json` |
| G18 real cases ≥ 3 | **Pass** — 3 cases, time-checkable activation peaks | `real_case_results.md` |
| G19 canonical 回归 | **Pass** — full suite green (438) | release |
| G20 无产品膨胀 | **Pass** — research API only, no UI |

## Constraints honored (CODEX 第一原则 + 退出条件)

1. 先审计输入语义，再写 NMF — `MAMSE008_INPUT_AUDIT` in baseline audit; only linear nonnegative surfaces admitted.
2. Input semantics clear (band ratios, simplex caveat recorded); basis versioned (ALGORITHM_VERSION + basis_id); deterministic rerun; frozen basis reopenable; residual evidence on synthetic + real; factors never mislabeled as sources; resource cost recorded; canonical measurement semantics untouched.
3. No new dependency (numpy/scipy); beta ∈ {2,1,0}; NNDSVD deterministic init; NaN mask; rank never claimed as source count.

## Honest negatives

1. 8-band simplex input yields residual 0.30–0.42 (higher-rank structure than 3 factors) — recorded, not glossed.
2. No CORPUS_FROZEN cross-case projection on real data yet (September).
3. Residual ratios unthresholded; no anomaly judgment.
4. Peak-time checkability ≠ perceptual salience.

## Maturity

```text
R0 Theory        ✅ task docs + principle PDF
R1 Operator      ✅ experimental implementation runs (numpy/scipy)
R2 Verified      ✅ 19/19 gates -> R2 VERIFIED
R3 Case Proven   ⏸ September: frozen corpus basis + fine-grained power-spectrogram path
R4+              ⏸ product coupling
```

## Outstanding (non-blocking)

1. Fine-grained NMF on a power-spectrogram surface (beyond the 8-band simplex) for spectral component studies.
2. Corpus-fit frozen basis + cross-case out-of-subspace evaluation (September).
3. Feature-bus transform/cache reuse (R4+).
