# MAMSE-004 — Release Gate

**Date:** 2026-08-11
**Verdict:** `EXPERIMENTAL_ACCEPTED` — phase geometry & group delay operator, off by default, **R2 Verified**. Per the task package release rule, R3/R4 requires a real production case that exercises the intended phase/time-anomaly scenario; the three pilot cases in this package do not change any canonical conclusion (honest negative), so no R3 claim is made.

## Acceptance gates A–E

| Gate | Status | Evidence |
|---|---|---|
| A. 数学正确性 (A1–A5) | **Pass.** rad/s axis → seconds; unwrap before derivative; pure delay 1.75 ms within 2 µs; linear-phase curvature < 1e-12; 2π wrap invariance | `test_results.md` G1–G3 |
| B. 可靠性 (B1–B4) | **Pass.** low-magnitude bins masked incl. zero-energy frames; valid_bin_ratio explicit; silence/short/mono → UNAVAILABLE with reason; None in JSON, never 0 | G4, G7, silence/short tests |
| C. Stereo cross-check (C1–C4) | **Pass.** convention fixed `R*conj(L)`; 0.5 ms and 2.5 ms delays recovered (sign + magnitude); GCC-PHAT within 1 sample; disagreement reported, never resolved | G5, G5b, G6, real cases |
| D. Engineering (D1–D6) | **Pass.** canonical `stereo.py` untouched (baseline audit Q4); experimental namespace; JSON+NPZ roundtrip; deterministic; runtime ~linear (0.5/2.0/3.0 s for 10/30/45 s); no NN dependency | `test_results.md`, `benchmark.json` |
| E. Evidence (E1–E5) | **Pass.** `phase_geometry_evidence.json` + `mamse004_phase_geometry.npz` + `mamse004_manifest.json` per case; manifest carries operator/config/source/runtime identity + config_hash; benchmark records duration/CPU/output size; 13/13 tests PASS | `real_cases/`, `benchmark.json` |

## Resource evidence

Local benchmark (48 kHz stereo, n_fft 8192 / hop 2048, band 80–18000 Hz):

| Slice | wall s | CPU s | GD median ms | valid_ratio |
|---|---|---|---|---|
| 10 s | 0.52 | 0.52 | -2.94 | 0.302 |
| 30 s | 2.02 | 2.03 | -1.41 | 0.224 |
| 45 s | 2.98 | 2.97 | -1.09 | 0.241 |

Full-track runs: 8.5–17.3 s wall. **Materially lighter than MAMSE-003** (43–76 s) — no per-band filter bank; the heavy cost is the 2D arrays (full-track intermediates ~310–470 MB, persisted sketch ~7 MB/case, see `payload_size_report.md`). On the 2C2G node, 45 s slices are safe under the resource guard; full-track runs remain offline/high-ACU until chunked analysis exists (R4+ optimization).

## Constraints honored (CODEX 强制约束)

1. Nonzero group delay never a FAIL — `judgment_eligible=false`, limitations explicit.
2. `phase_risk_ratio` semantics untouched (baseline audit Q4).
3. Low-magnitude bins masked → UNAVAILABLE, never 0 (silence test).
4. All parameters versioned: config_hash in every manifest; conventions (FFT/hop/window/range/floor/unwrap/cross-sign) part of the versioned config.
5. Experimental namespace `moodify_experimental/mamse004/`; no canonical authority promotion.
6. JSON summary + NPZ 2D sketch (decimated, self-describing); provenance in manifest.
7. Deterministic (G8) — logical identity excludes only runtime bookkeeping.
8. No heavy NN dependency; numpy/scipy only.

## Honest negatives

1. **Corpus-level no-increment**: for the three pilot tracks, MAMSE-004 changes no canonical conclusion (no interchannel delay, low phase risk confirmed). The operator's value case is the intended scenario (suspected phase/time anomaly, frequency-dependent phase artifacts) which none of the three tracks exhibits. R3 stays open by design.
2. GCC-PHAT = 0.0 ms in all real cases (peak at 0 within ±5 ms) — shows alignment, not validation.
3. GD MAD ~56 ms on real music — median descriptors only; anomaly thresholds need fixture-based study.
4. Negative GD median (9056391, -0.69 ms) is descriptive, not diagnostic.

## Maturity

```text
R0 Theory        ✅ task docs + principle PDF
R1 Operator      ✅ experimental implementation runs (numpy/scipy, no new dep)
R2 Verified      ✅ 13/13 synthetic gates, A–E gates pass, ruff clean, deterministic
R3+              ⏸ open: requires a production case exercising the phase/time-anomaly scenario
```

## Outstanding (non-blocking)

1. Fixture-based study of GD-dispersion thresholds before any anomaly interpretation.
2. Chunked analysis for on-node full tracks (R4+).
3. GCC-PHAT with a wider search window (beyond ±5 ms) for use cases with larger interchannel delays.
4. R_phase profiles coupling with MAMSE-001 resolution axes (architecture §4) — future.
