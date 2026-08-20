# MAMSE-006 — Real Case Results (recording only, no threshold tuning)

**Date:** 2026-08-11
**Sources:** 3 operator-owned AI pilot tracks (same files as MAMSE-001..005, rights_ok=true, sha256-linked).
**Scope:** Per CODEX §7, real-case thresholds are deferred to the September data experiment. This document records descriptors and evidence only — no threshold, no rule, no upgrade.

## Descriptors (full tracks, 99 log-frequency bins, 12 bpo, 4 s modulation window)

| Case | RMS dBFS | t_peak Hz | t_centroid Hz | slow/mid/fast ratio | t_entropy | s_peak cpo | orientation | ridge conc |
|---|---|---|---|---|---|---|---|---|
| 9056391 harmonic | -17.2 | 0.25 | 3.50 | 0.753 / 0.195 / 0.052 | 0.645 | 0.121 | 0.055 | 0.085 |
| 9961e07 transient | -16.8 | 0.25 | 3.30 | 0.769 / 0.179 / 0.053 | 0.578 | 0.121 | 0.002 | 0.114 |
| 7b3f021 AI | -17.5 | 0.25 | 3.31 | 0.777 / 0.164 / 0.059 | 0.546 | 0.121 | -0.003 | 0.106 |

All ridges: `status: CANDIDATE`, 0.25 Hz / 0.121 cpo, velocity 2.06 oct/s. Segments 64–98; runtime 3.2–7.0 s full track.

## Technical observations (recording only)

1. **Slow modulation dominates all three tracks** (slow ratio 0.75–0.78, temporal peak at the 0.25 Hz lower bound, centroid 3.3–3.5 Hz). Consistent with MAMSE-003's finding that these productions share overall modulation character — the two operators agree in direction (G14 cross-module: no conflict, no overwrite).

2. **Spectral modulation sits at the lowest non-zero bin (0.121 cpo)** in all cases: the spectral marginal decays monotonically, i.e. no strong band-to-band ripple pattern. Descriptive; consistent with smooth spectral envelopes (MAMSE-005 envelope roughness ≈ 0.004).

3. **Orientation is ≈ 0** (-0.003 to 0.055): no systematic spectro-temporal direction bias. Per G9, with ridge concentration 0.09–0.11 (low), no strong directional interpretation is made.

4. **Ridge concentration is low (< 0.12)** in all cases: no single dominant modulation structure. The ridges stay CANDIDATE.

## Honest negatives

1. `temporal_peak = 0.25 Hz` is the search lower bound, not a discovered peak — the true slow-modulation peak is below the v0.1 resolution floor. Recorded as-is.
2. `spectral_peak = 0.121 cpo` is the lowest non-zero bin; it means "monotonic spectral marginal", not a discovered ripple.
3. No threshold, no BPM claim, no AI-vs-human statement, no artistic judgment — per the operator's limitations and CODEX §7 deferral.
4. These three tracks are a pilot corpus, not a basis for any generalization.

## Verdict

The operator runs cleanly on full tracks (3–7 s wall), with explicit CANDIDATE/UNAVAILABLE semantics and cross-operator consistency with MAMSE-003/005. Standing at **SYNTHETIC_VERIFIED (R2)**; real-case calibration is explicitly deferred to the September data experiment.
