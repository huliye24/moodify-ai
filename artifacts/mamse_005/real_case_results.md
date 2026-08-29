# MAMSE-005 — Real Case Results

**Date:** 2026-08-11
**Sources:** 3 operator-owned AI pilot tracks (same files as MAMSE-001..004, rights_ok=true, sha256-linked in manifests).
**Scope:** TECHNICAL_OBSERVATION only. `f0_candidate` is a cepstral candidate, not ground-truth pitch; `resonance_candidates` are envelope peaks, not formants.

## Descriptors (full tracks, n_fft 4096 / hop 1024, lifter 2.5 ms)

| Case | Periodicity avail ratio | Median F0 candidate Hz | Median periodicity score | Envelope roughness | Raw log-spectrum roughness | Fine/env energy ratio |
|---|---|---|---|---|---|---|
| 9056391 harmonic | **0.010** | 333.3 | 0.751 | 0.0042 | 1.210 | 0.031 |
| 9961e07 transient | 0.145 | 390.2 | 0.774 | 0.0048 | 1.212 | 0.032 |
| 7b3f021 AI | 0.136 | 347.8 | 0.778 | 0.0046 | 1.219 | 0.030 |

## Technical observations

1. **Homomorphic separation works on real mixes: envelope roughness ≈ 0.004 vs raw ≈ 1.21 (~280× smoother).** The low-quefrency lifter (2.5 ms cutoff) removes the harmonic fine structure from the envelope as designed; the fine residual carries the remaining texture.

2. **Fine-to-envelope energy ratio is low (~0.03) in all three cases.** The log-spectrum energy of these productions concentrates in the smooth envelope; the periodic fine structure is a small component. Descriptive — not a quality statement.

3. **Cepstral periodicity is sparse in full mixes: 1.0–14.5% of frames.** Most frames fail the RMS gate or the cepstral-peak prominence gate. Honest consequence: the *track-level* median F0 candidate (333–390 Hz) is computed over few frames and must NOT be read as the song's pitch. Cepstral periodicity is a frame-level diagnostic, not a track-level label.

4. **The harmonic case stands out: 1.0% periodic frames vs 13.6–14.5% for the other two.** 9056391's energy is dominated by a low CQT-pitch anchor (MAMSE-002: 164.7 Hz G2, 0.0 cents) but its cepstral periodicity is sparse. This is a *complementary* dimension — energy dominance vs periodicity evidence — not a defect claim and not a cross-operator contradiction (different scales: track-level grid pitch vs frame-level cepstral peaks).

## Complementarity with STFT / CQT (CODEX step 8)

| Question | STFT/MR-STFT | CQT (MAMSE-002) | Cepstrum (MAMSE-005) |
|---|---|---|---|
| Where is energy? | band energies, centroid | log-frequency dominant + tuning lock | — |
| What is the internal spectrum structure? | — | — | envelope (source/filter shape) vs fine structure, periodicity ratio, resonance candidates |
| Track-level pitch? | — | dominant_midi (grid, energy-based) | NOT claimed — candidate over sparse frames only |

Concrete complement: for 9056391, CQT reports a locked G2 pitch anchor while cepstrum reports 1% periodic frames. A system using only one path would see "pitched track" (CQT) or "no cepstral pitch" (cepsrum); together they describe *energy-pitched but structurally sparse* — a statement neither alone can make. This remains descriptive; no rule is derived.

## Honest negatives

1. Track-level F0 candidate is unreliable by design for these full mixes (sparse availability) — recorded, not hidden.
2. Resonance candidates on full mixes are envelope peaks; on these dense productions they were not interpreted further (no formant claim, no vocal inference).
3. No artistic/naturalness score is produced anywhere in the operator.
4. The 9056391 vs others periodicity gap (1% vs 14%) is one corpus observation, not a production-type classifier.

## Verdict

The operator runs cleanly on real tracks with bounded cost (21–52 s full track; benchmark 0.65/2.7/5.7 s for 10/30/45 s), produces honest UNAVAILABLE semantics, and adds a spectrum-internal-structure dimension complementary to STFT/CQT. Per the package scope, v0.1 stands at **R2 Verified**; frame-level periodicity diagnostics on targeted segments (voice/vocal regions) are the R3 candidate path, requiring segment-level fixtures.
