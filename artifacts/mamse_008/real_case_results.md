# MAMSE-008 — Real Case Results (S1 band-ratio input, recording only)

**Date:** 2026-08-11
**Sources:** 3 operator-owned AI pilot tracks (same files as MAMSE-001..007, rights_ok=true).
**Scope:** Input = canonical S1 band-energy ratios (8 nonnegative simplex columns; mid/side + short_term_lufs excluded per baseline audit). rank=3 NMF. Components are anonymous factors; activation peak times map to the source clock and are human-checkable. No threshold, no source labeling.

## Descriptors (rank 3, beta=2, 300 iter)

| Case | Rel error | Iter | C00 peak | C01 peak | C02 peak | Runtime |
|---|---|---|---|---|---|---|
| 9056391 harmonic | 0.300 | 300 | 115.6 s | 50.1 s | 44.5 s | 75 ms |
| 9961e07 transient | 0.423 | 240 | 177.3 s | 175.4 s | 2.0 s | 102 ms |
| 7b3f021 AI | 0.419 | 300 | 110.5 s | 197.5 s | 19.9 s | 100 ms |

Activation sparsity (Hoyer): 0.22–0.37 across components; total activation ordered C00 > C01 > C02 by the deterministic permutation rule.

## Technical observations (recording only)

1. **Relative error 0.30–0.42** on the 8-band simplex input: the rank-3 factorization leaves substantial unexplained structure. Expected — 8 compositional bands are inherently higher-rank than 3 factors; consistent with the benchmark (rank-2 0.45 / rank-3 0.30). No quality reading.

2. **Activation peaks are spread through each track's timeline** (e.g. 9056391: C02 at 44.5 s, C01 at 50.1 s, C00 at 115.6 s; 9961e07: C02 at 2.0 s, C00/C01 at ~176 s; 7b3f021: C02 at 19.9 s, C00 at 110.5 s, C01 at 197.5 s). These time positions are **human-checkable evidence** (G18): a reviewer can listen at those timestamps to verify whether the activation corresponds to real structure changes. No automated claim is made.

3. **All components are anonymous** — no semantic_label, no "vocal/drums/bass" inference, no AI-artifact claim.

4. **Runtime ~0.1 s, payload 34–50 KB per case** — negligible resource cost.

## Honest negatives

1. The 8-band simplex input is a coarse, compositionally constrained feature set; the factors describe *band-profile mixtures*, not fine spectral components. Fine-grained NMF (e.g. on a power spectrogram) is a separate analysis path for future experiments.
2. No frozen-basis cross-case projection was run (CORPUS_FROZEN reopen validated synthetically only); real-case out-of-subspace detection needs a corpus basis (September).
3. Residual ratios are unthresholded; no anomaly judgment is derived.
4. Peak-time checkability does not imply the peaks are perceptually salient.

## Verdict

The operator runs cleanly on real tracks via a semantically-audited nonnegative input, with deterministic identity, anonymous components, negligible cost, and time-checkable evidence. Standing at **R2**; R3 requires frozen-basis corpus work in the September data experiment.
