# MAMSE-012 — Real Case Results (recording only)

**Date:** 2026-08-11
**Sources:** 3 operator-owned AI pilot tracks (same files as MAMSE-001..011, rights_ok=true).
**Scope:** Three graphs per track: band path graph (mean band-profile signal), temporal event graph (canonical events), positive-correlation graph (MAMSE-011 clean subset). Recording only; no canonical change.

## Descriptors

| Case | Band Dirichlet | Band hf ratio | Band dc ratio | Max LV node | Event nodes/edges | Corr edges (of 66) |
|---|---|---|---|---|---|---|
| 9056391 harmonic | 1.045 | 0.102 | 0.348 | 3 (mid) | 46 / 72 | 5 |
| 9961e07 transient | 1.027 | 0.101 | 0.471 | 4 (core_mid) | 95 / 194 | 7 |
| 7b3f021 AI | 1.301 | **0.199** | **0.557** | 4 (core_mid) | 51 / 47 | 6 |

## Technical observations

1. **The AI case's band profile is the least smooth in topology terms** (Dirichlet 1.30, high-graph-frequency ratio 0.199 vs 0.10 for the others, dc ratio 0.557). Its mean band profile varies more sharply across neighboring bands. This is a structural descriptor — consistent in direction with MAMSE-007's finding that the AI track is more multi-dimensional, but it is NOT an AI-detection claim (single track, descriptive only).

2. **Local variation peaks in the mid/core-mid region** (nodes 3–4) for all three tracks: the largest band-to-band profile discontinuity sits in the mid frequencies. Descriptive.

3. **Temporal event graphs are dense-ish** (46→72, 95→194, 51→47 edges) with exp(-gap/tau) proximity weights; original event semantics preserved, no invented labels.

4. **Positive-correlation graphs are sparse** (5–7 edges of 66): few clean-subset features co-vary above r ≥ 0.5 — consistent with MAMSE-011's effective rank ~5.5 (the relation space is not dense).

## Honest negatives

1. Band-graph signals are 8-dimensional median profiles — a coarse structural view; no perceptual claim.
2. graph frequency ≠ acoustic Hz (semantic boundary in every evidence file); high graph-frequency ratio is structural variation, not bad audio.
3. Three tracks, one probe per graph family — no corpus-level generalization.

## Verdict

The GSP layer runs correctly and deterministically on real tracks (spectra in ms), with explicit authority/provenance and topology-vs-Hz boundaries honored. Structural evidence is recorded; incremental-value questions (G31) remain open for the September corpus study.
