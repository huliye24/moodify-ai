# MAMSE-010 — Release Gate

**Date:** 2026-08-11
**Verdict:** `EXPERIMENTAL_ACCEPTED` — auditory tensor view layer, off by default, **R2 VERIFIED (synthetic) with real-case value claims recorded as open**. The upgrade condition (multiway > multiple 2D tables on real cases) is NOT demonstrated on this corpus; the layer stays research.

## Acceptance gates G1–G24

| Gate | Status | Evidence |
|---|---|---|
| G1 axis 名称/长度 | **Pass** | AxisSpec contract + tests |
| G2 shape 一致 | **Pass** | TensorField shape check |
| G3 重复 axis 拒绝 | **Pass** | test |
| G4 unavailable ≠ zero | **Pass** | valid mask; NaN preserved |
| G5 tensor_id 稳定 | **Pass** | deterministic hash |
| G6 区间对齐 | **Pass** | interval_overlap_weighted; not index-based |
| G7 缺失保留 mask | **Pass** | sfv valid 0.386 on real cases |
| G8 不 stack 异质 plane | **Pass** | build_scale_feature_tensor aligned only |
| G9 unfold/fold | **Pass** | round-trip |
| G10 n-mode product | **Pass** | shape test |
| G11 HOSVD 重构 | **Pass** | exact on multilinear-rank fixture (< 1e-10) |
| G12 符号规范化 | **Pass** | deterministic model_id/core |
| G13 frozen basis 暴露新结构 | **Pass** (synthetic: > 5× residual) | test |
| G14 高 residual ≠ 坏 | **Pass** | semantics + real-case denominator effect documented |
| G15 JSON/NPZ reopen | **Pass** | test |
| G16 dense 可预估 | **Pass** | estimate_dense_bytes |
| G17 tile 完整 | **Pass** | coverage test |
| G18 shared transform 复用 | **Pass (recorded)** | channel view computes one STFT per source; feature-bus reuse R4+ |
| G19 materialization guard | **Pass** | guard raises; 5D probe 6.1 GB > 1 GB |
| G20 canonical 不替换 | **Pass** | AuditoryRepresentation untouched |
| G21 语义冲突不放大 | **Pass** | multilinear only on homogeneous power tensor; conflict columns not interpreted |
| G22 真实 case ≥ 3 + 定位价值 | **Partial** — 3 cases run; localization candidates are low-energy-frame artifacts (denominator effect), value case open | real_case_results.md |
| G23 benchmark | **Pass** | shape/dtype/runtime/bytes recorded |
| G24 canonical 回归 | **Pass** | full suite green (476) |

## Constraints honored (CODEX 绝对禁止)

1. No raw np.stack of S0/S1/S2 — interval-overlap alignment only.
2. No array-index time alignment — interval overlap on ms.
3. No zero-fill for unavailable — explicit masks.
4. No HOSVD on mixed-unit feature axes — multilinear only on homogeneous power tensor.
5. No repeated full-track STFT — one transform per source per view.
6. Research tensor never rewrites canonical measurement authority.

## Honest negatives

1. **G22 value claim open**: on this corpus, HOSVD time-residual candidates coincide with low-energy frames (mean power below corpus p10) — a denominator effect, not informative localization.
2. sfv valid fraction 0.386 means most cells are masked — the honest cost of heterogeneous scales.
3. HOSVD error 0.18–0.27 is an approximation metric, not an anomaly detector.

## Maturity

```text
R0 Theory        ✅ task docs + principle PDF
R1 Operator      ✅ tensor views + multilinear run (numpy/scipy)
R2 Synthetic     ✅ 20/20 gates, G1-G21/G23-G24 pass
R3 Case Proven   ⏸ open: multiway-value demonstration on real cases (September)
R4+              ⏸ canonical next-version consideration
```

## Outstanding (non-blocking)

1. September: corpus study comparing multiway vs 2D-table information gain (G22).
2. Frozen multilinear basis over a corpus for cross-case projection.
3. Feature-bus transform/cache reuse (R4+).
