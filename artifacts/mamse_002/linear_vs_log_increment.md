# MAMSE-002 — Linear vs Log Increment Comparison (T6)

**Date:** 2026-08-11
**Method:** synthetic fixtures run through the canonical linear-Hz path (`moodify.auditory.metrics.compute_metrics`, STFT n_fft=8192) and the MAMSE-002 log-frequency path (24 bpo CQT). Numeric evidence: `linear_vs_log_comparison_synth.json`.

## Case A — low-register semitone pair (55.0 + 58.27 Hz, 1.0 semitone)

| Path | What it sees |
|---|---|
| Linear-Hz | spectral centroid 56.6 Hz; a single blended low-frequency mass, no separation |
| Log-frequency | **two distinct peaks at 55.0 and 58.27 Hz** (top-2 mean peaks), dominant 55.0 Hz |

**Incremental evidence:** YES — resolves a 1-semitone low-register pair that a 93.75 Hz linear bin cannot separate. This is the strongest increment case.

**Cost delta:** CQT ~2.3 s wall for 4 s audio locally (see benchmark for node numbers).

## Case B — harmonic sustained (220 + 440 + 660 Hz)

| Path | What it sees |
|---|---|
| Linear-Hz | centroid 290.6 Hz (energy-weighted middle of the harmonic stack) |
| Log-frequency | peaks at 220.0 and 440.0 (octave structure explicit), dominant 220.0 Hz, dominant_midi 220.01 |

**Incremental evidence:** YES (moderate) — octave-fold structure visible and the fundamental is localized to within a cent; useful for harmonic/pitch-ratio research cases.

**Redundant evidence:** loudness/level metrics identical in both paths (as expected — CQT adds no loudness value).

## Case C — note-locked narrowband anomaly (440 Hz + 443.6 Hz @ 0.2 gain)

| Path | What it sees |
|---|---|
| Linear-Hz | centroid 440.0 Hz; no separation |
| Log-frequency | mean spectrum: single peak 440.0 Hz; per-frame dominant swings into the 434–443 Hz window (quadratic subbin wobble) |

**Incremental evidence:** NONE at the mean-spectrum level for this fixture. Frame-level dominant wobble is a weak clue only. Honest conclusion: for this anomaly class the log path does NOT beat the linear path on mean evidence; a stronger/persistent anomaly or per-frame analysis would be needed. **Not a basis for claiming general superiority.**

## Verdict per case

| Case | Increment | Redundancy | Cost |
|---|---|---|---|
| A low semitone pair | **strong** | level metrics | CQT >> STFT |
| B harmonic sustained | moderate | level/centroid | CQT >> STFT |
| C note-locked narrowband | none (this fixture) | — | — |

Conditional-invocation implication: MAMSE-002 earns its cost only when low-register close structure or harmonic/pitch-ratio questions are present — exactly the T7 policy triggers.
