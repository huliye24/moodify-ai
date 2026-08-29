# MAMSE-006 — Release Gate

**Date:** 2026-08-11
**Verdict:** `EXPERIMENTAL_ACCEPTED` — modulation spectrum / spectro-temporal motion operator, off by default, **SYNTHETIC_VERIFIED (R2)**. Real-case calibration, thresholds and any promotion remain deferred to the September data experiment (CODEX §7); no BPM/orientation/AI claims are made anywhere.

## Acceptance gates G0–G14

| Gate | Status | Evidence |
|---|---|---|
| G0 Scope | **Pass** — experimental namespace; no Phase-I metric change; no second lifecycle | `baseline_audit.md` Q2/Q8 |
| G1 Mathematical identity | **Pass** — temporal Hz (frame clock), spectral cycles/octave (bpo), log-frequency axis traceable | `test_results.md` + config |
| G2 Time integrity | **Pass** — modulation windows map to source clock `time_s`; too-short → UNAVAILABLE | tests |
| G3 Low-energy honesty | **Pass** — silence → `UNAVAILABLE_LOW_ENERGY`, no ridge | tests |
| G4 AM recovery | **Pass** — 2/5/9 Hz within 0.5 Hz | tests |
| G5 Gain invariance | **Pass** | tests |
| G6 Static ripple | **Pass** — 2.0 cpo within 0.2 | tests |
| G7 Dynamic ripple | **Pass** — 4 Hz / 1.5 cpo ridge | tests |
| G8 Orientation | **Pass** — reversal flips sign | tests |
| G9 Ridge semantics | **Pass** — always `CANDIDATE`; low-concentration real cases (0.09–0.11) get no directional interpretation | tests + real cases |
| G10 Distribution integrity | **Pass** — non-negative, normalized | tests |
| G11 Determinism | **Pass** | tests |
| G12 Serialization | **Pass** — JSON/NPZ round-trip, manifest with profile_hash | tests |
| G13 Resource | **Pass** — 0.21/0.62/1.06 s for 10/30/45 s; full track 3–7 s; surface decimated to ~2.4 MB NPZ | `benchmark.json`, `payload_size_report.md` |
| G14 Cross-module | **Pass (by design)** — evidence preserved independently per module; MAMSE-003/005 agreement recorded, no silent overwrite. Full joint verification deferred to September | `real_case_results.md` |

## Constraints honored (CODEX 强制约束 + 禁止事项)

1. No canonical metric redefinition — `spectral_flux` proxy recorded in baseline audit, not touched.
2. No second clock — modulation segments map to source `time_s`.
3. Transform/cache reuse is R4+ (established MAMSE-001..005 precedent); no canonical-flow duplication introduced.
4. Authority = EXPERIMENTAL_DESCRIPTOR / ridge CANDIDATE / judgment_eligible=False.
5. Explicit failures: `UNAVAILABLE_TOO_SHORT`, `UNAVAILABLE_LOW_ENERGY`, `UNAVAILABLE_INVALID_CONFIG`, `PARTIAL_NUMERICAL_LIMITATION` semantics honored.
6. No modulation "total score", no BPM label, no physical-source-orientation claim, no AI/human auto-judgment, no Phase-I contract change, no deletion of UNKNOWN/UNAVAILABLE, no LLM in place of the interpretable operator.

## Honest negatives

1. Real-case `temporal_peak` sits at the 0.25 Hz search floor and `spectral_peak` at the lowest non-zero bin — resolution-floor effects recorded, not claimed as discoveries.
2. Ridge concentration is low (< 0.12) in all pilot tracks → ridges remain CANDIDATE with no directional reading.
3. The three pilot tracks show near-identical slow-modulation dominance — a corpus property, not a finding about music in general.
4. No thresholds exist yet by design; September calibration may revise any of these descriptors.

## Maturity

```text
R0 Theory        ✅ task docs + principle PDF
R1 Operator      ✅ experimental implementation runs (numpy/scipy, no new dep)
R2 Synthetic     ✅ 14/14 gates, G0-G13 pass -> SYNTHETIC_VERIFIED
R3 Case Proven   ⏸ September data experiment (thresholds, A/B, cross-module)
R4+              ⏸ product coupling, transform/cache reuse
```

## Outstanding (non-blocking)

1. September: real-case thresholds, A/B relations, cross-operator agreement/conflict tables (G14 full verification).
2. Transform/cache reuse via the execution feature bus (R4+).
3. Wider spectral-rate search (bpo > 12) for finer scale resolution if a use case demands it.
