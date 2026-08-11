# MAMSE-010 — Real Case Results (recording only)

**Date:** 2026-08-11
**Sources:** 3 operator-owned AI pilot tracks (same files as MAMSE-001..009, rights_ok=true).
**Scope:** Two tensor views per case — TIME×SCALE×FEATURE (overlap-aligned canonical planes) and TIME×FREQ×CHANNEL (linear power) — plus a research HOSVD. Recording only; no canonical change.

## Descriptors

| Case | tensor_id | sfv shape | sfv valid | csv shape | HOSVD err | Top residual candidates |
|---|---|---|---|---|---|---|
| 9056391 harmonic | tensor-50bd6… | 1286×3×12 | 0.389 | 1506×99×2 | 0.210 | 42.0 s (r=1.00), 94.3 s, 116.3 s |
| 9961e07 transient | tensor-185ca… | 1844×3×12 | 0.385 | 2160×99×2 | 0.180 | 58.7 s, 162.0 s, 162.7 s |
| 7b3f021 AI | tensor-c6ba9… | 1980×3×12 | 0.386 | 2320×99×2 | 0.273 | 9.0 s, 10.9 s, 46.4 s |

## Technical observations

1. **The scale-feature view honestly carries 61% masked cells** (valid fraction 0.386): S0/S1/S2 expose different feature sets, and absent features stay NaN + mask=False (G7) — the tensor does not fabricate cross-scale values.

2. **HOSVD reconstruction error 0.18–0.27** at ranks (8,8,2) on the power tensor: a moderately informative low-multilinear-rank approximation of the 99-bin × 2-channel power surface. Descriptive; no quality reading (G14).

3. **Top time-residual candidates coincide with low-energy frames.** Verified for 9056391: the r≈1.0 frames at 42.0/94.3/116.3 s have mean power 1.1e-5 / 7.2e-6 / 3.0e-6 — below the corpus p10 (1.66e-5). The saturated relative residual is a denominator effect (near-silent frames), **not** a structural anomaly localization. Honest negative for the "cross-scale/channel localization" value claim on this corpus (G22): the localization axis did not produce informative candidates here.

4. **Deterministic identity holds**: tensor_id stable per schema/source; HOSVD model_id stable.

## Honest negatives

1. Localization candidates are low-energy-frame artifacts on this corpus — no informative cross-scale/channel localization demonstrated (G22 value case open, September).
2. HOSVD error 0.18–0.27 is an approximation metric, not an anomaly detector.
3. No canonical representation change; no product entry point.

## Verdict

The tensor layer runs correctly and honestly: named axes, explicit masks, interval-based alignment, guarded materialization, deterministic identity. The incremental-value question (multiway > multiple 2D tables) is NOT demonstrated on this corpus — recorded as an open question for the September data experiment.
