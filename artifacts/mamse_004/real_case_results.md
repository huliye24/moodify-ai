# MAMSE-004 — Real Case Results

**Date:** 2026-08-11
**Sources:** 3 operator-owned AI pilot tracks (same files as MAMSE-001/002/003, rights_ok=true, sha256-linked in manifests).
**Scope:** TECHNICAL_OBSERVATION only. No artistic judgment. Nonzero group delay is never treated as a defect.

## Canonical (linear/stereo) profile vs MAMSE-004

| Case | corr | side_to_mid dB | neg_corr | phase_risk_ratio | GD median ms | GD MAD ms | GD p95abs ms | valid_ratio |
|---|---|---|---|---|---|---|---|---|
| 9056391 harmonic | 0.695 | -7.45 | 0.0050 | 0.0176 | **-0.690** | 57.2 | 80.0 | 0.291 |
| 9961e07 transient | 0.848 | -10.86 | 0.0086 | 0.0211 | 0.036 | 55.8 | 79.8 | 0.450 |
| 7b3f021 AI | 0.766 | -8.77 | 0.0006 | 0.0024 | 0.045 | 56.2 | 79.8 | 0.435 |

Stereo cross-channel (all three cases): interchannel delay median ≈ 0 (-0.004 / 0.001 / 0.004 ms), GCC-PHAT = 0.0 ms, cross-method disagreement ≤ 0.004 ms.

## Technical observations

1. **No measurable interchannel time misalignment in any case.** Both IPD-slope and GCC-PHAT agree at ≈ 0 ms (disagreement < 5 µs). The canonical path already reported low phase_risk (0.002–0.021) — the two paths agree; MAMSE-004 adds that the *delay* structure is aligned, not just that energy ratios are sane.

2. **The harmonic case shows a systematic negative group-delay offset (-0.69 ms)** while the transient and AI cases sit near 0. A negative GD median means the phase tends to advance with frequency — consistent with a specific filter/EQ/delay chain in that production. Descriptive only: this is not a defect claim, and one case cannot justify a rule.

3. **Group-delay dispersion is large in all cases (MAD 55–57 ms, p95abs ≈ 80 ms).** For harmonic-rich music, STFT phase derivatives vary strongly across frequency (wrapping + unwrap residuals). v0.1 therefore reports descriptors only; any "anomaly" threshold needs a fixture-based study before use.

4. **valid_bin_ratio differs by case (0.291 / 0.450 / 0.435)** — the harmonic case has the sparsest spectrum, consistent with MAMSE-003's sparsity ranking (0.343 highest for 9056391). Cross-operator consistency is noted as supporting evidence, not proof.

5. **Phase curvature median ≈ 1e-7 s² in all cases** — no strong nonlinear phase distortion is observed at the median. Again descriptive.

## Per-case answer (E-gate style questions)

| Case | What canonical path already knows | What MAMSE-004 adds | Changes interpretation? | Cost |
|---|---|---|---|---|
| 9056391 | corr 0.695, low phase_risk 0.018, low centroid | GD median -0.69 ms (systematic phase-advance signature); channels aligned | No — but adds a *frequency-derivative* phase dimension the frame-level risk ratio cannot express | 8.5 s / full track |
| 9961e07 | corr 0.848, highest phase_risk 0.021 | channels aligned (0.001 ms), GD ≈ 0, highest valid ratio 0.45 | No — confirms no phase issue; quantifies phase-information availability | 17.3 s |
| 7b3f021 | lowest phase_risk 0.002 | channels aligned, GD ≈ 0 | No — consistent with canonical; adds no-delay evidence | 15.7 s |

**If MAMSE-004 is not run:** the system knows "no obvious phase risk" (energy ratios) but has no answer to "is there a time-of-arrival difference between channels" or "does phase structure advance/retard systematically with frequency". For the current three cases the increment does NOT change any conclusion — an honest negative at corpus level. Its value case is for future low-register phase/time questions (e.g., a track with a suspected interchannel delay or a frequency-dependent phase artifact), which none of these three productions exhibits.

## Honest negatives

1. GCC-PHAT = 0.0 ms in all cases: within the ±5 ms search window the peak sits at 0. This shows no significant interchannel delay, not an instrument validation.
2. GD MAD ~56 ms: the raw dispersion is dominated by harmonic-rich phase structure; median-based descriptors are the only honest summary at v0.1.
3. Negative GD median is descriptive, not diagnostic.
4. Three productions are not a corpus; no rule or threshold is derived from them.

## Verdict

Real cases run cleanly with bounded cost and explicit UNAVAILABLE semantics. For these specific tracks the operator adds no conclusion-changing evidence — the incremental-value case remains open for the intended scenarios (phase/time anomaly questions). Per the task package release rule, v0.1 stands at **R2 Verified**; R3 requires a production case that exercises the intended scenario.
