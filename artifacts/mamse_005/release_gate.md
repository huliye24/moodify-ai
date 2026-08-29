# MAMSE-005 — Release Gate

**Date:** 2026-08-11
**Verdict:** `EXPERIMENTAL_ACCEPTED` — cepstral structure / source-filter operator, off by default, **R2 Verified**. Per the package scope (R0-R2), no canonical promotion and no R3 claim; segment-level (voice/vocal) periodicity diagnostics are the R3 candidate path.

## Acceptance gates G0–G9

| Gate | Status | Evidence |
|---|---|---|
| G0 边界 | **Pass** — experimental namespace `moodify_experimental/mamse005/`; canonical metrics/schemas untouched (baseline audit Q5) | `baseline_audit.md` |
| G1 数学正确性 | **Pass** — real cepstrum via even log-magnitude IFFT; explicit magnitude floor; quefrency axis = 1/sr; lifter identity reconstruction (< 1e-10) | `test_results.md` |
| G2 周期 fixture | **Pass** — 200 Hz < 3%; ladder 100/250/400 < 4%; gain-invariant candidate | tests |
| G3 包络分离 | **Pass** — envelope 280× smoother than raw on real mixes; fine residual keeps texture; exact log-domain reconstruction | tests + real cases |
| G4 Resonance candidate | **Pass** — controlled iirpeak resonators found within tolerance; schema/limitations always say `candidate` | tests + evidence |
| G5 失败诚实 | **Pass** — silence/short → UNAVAILABLE with reason; noise never forced onto stable F0 (ratio < 0.8 gate) | tests |
| G6 确定性 | **Pass** — logical JSON and source SHA256 identical across reruns | tests |
| G7 资源 | **Pass** — bounded linear growth (0.65/2.7/5.7 s for 10/30/45 s; 21–52 s full track); NPZ stores decimated sketch, dense per-frame arrays never persisted | `benchmark.json`, `payload_size_report.md` |
| G8 Evidence | **Pass** — JSON summary + NPZ raw sketch + manifest (version/config/source hash/config_hash) | `real_cases/*/` |
| G9 Moodify 集成 | **Pass** — no product score exposed; deep-scan/diagnostic invocation only; CQT/MSE conflict-detection hook documented, not built | `real_case_results.md` |

## Constraints honored (CODEX 强制约束)

1. No canonical metric definition/unit/threshold/schema modified.
2. `f0_candidate` labeled ESTIMATOR, never ground-truth pitch (limitations + schema).
3. `resonance_candidates` = envelope peaks, never auto-named formant.
4. Low-energy/silence/short inputs → UNAVAILABLE with reason (no fabricated numbers).
5. All config versioned; config_hash in every manifest.
6. 2D arrays → NPZ sketch; JSON keeps summary/provenance/config/limitations only.
7. Operator off by default; research/deep-scan paths only.
8. Tests first; all synthetic fixtures reproducible (seeded RNG, no hidden state).

## Honest negatives

1. **Track-level F0 candidate is unreliable on full mixes by design**: 1.0–14.5% periodic frames; the median over few frames is not a song pitch label.
2. Fine-to-envelope energy ratio ~0.03 in all three tracks — fine structure is a small component; no claim that this generalizes.
3. Resonance candidates on dense productions were not interpreted (no formant/vocal inference).
4. The periodicity gap between 9056391 (1%) and the other two (~14%) is a single-corpus observation.
5. GCC-style cross-check with CQT pitch (G9 conflict detection) is a future hook, not implemented here.

## Maturity

```text
R0 Theory        ✅ task docs + principle PDF
R1 Operator      ✅ experimental implementation runs (numpy/scipy, no new dep)
R2 Verified      ✅ 13/13 synthetic gates, G0-G9 pass, ruff clean, deterministic
R3+              ⏸ open: segment-level (voice/vocal) periodicity fixtures; CQT/MSE conflict detection
```

## Outstanding (non-blocking)

1. Segment-level (vocal/voiced-region) periodicity analysis with labeled fixtures — the R3 path.
2. CQT/MSE pitch conflict-detection integration (G9 hook).
3. Resonance-candidate interpretation on single-source material (instrumental stems) before any formant-adjacent claim.
4. Optional quefrency-axis decimation of the NPZ sketch if payload must shrink further (currently ~11 MB/case, acceptable).
