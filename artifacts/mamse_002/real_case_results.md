# MAMSE-002 — Real Case Results (T10)

**Date:** 2026-08-11
**Sources:** 3 operator-owned AI pilot tracks (rights_ok=true), full-length, 48 kHz stereo, same files as MAMSE-001 T7 (linked source sha256 in each manifest).
**Scope:** TECHNICAL_OBSERVATION only. No artistic-quality statement is made for any case.

## Case selection

| Case | Role | Prior profile (linear scan) |
|---|---|---|
| case_9056391_harmonic | low-register prominent | LRA 4.53, centroid 504.5 Hz |
| case_9961e07_transient | harmonic/vocal sustained candidate | LRA 9.0, centroid 823.6 Hz |
| case_7b3f021_ai | AI-generated pilot track | LRA 6.75, centroid 979.3 Hz |

## Observations (all CQT status OK, 216 bins, 24 bpo)

| Case | Median dominant Hz | MIDI | Tuning deviation cents | Peakiness | Log entropy | Low-register adjacent events |
|---|---|---|---|---|---|---|
| 9056391 | 164.67 | 51.98 (G2) | **0.00** | 0.258 | 0.508 | 1 |
| 9961e07 | 130.63 | 47.98 (B1) | **-0.95** | 0.280 | 0.483 | 24 |
| 7b3f021 | 72.56 | 37.80 (F#1) | **-0.05** | 0.297 | 0.484 | 64 |

## Technical observations

1. **Near-zero tuning deviation in all three AI tracks** (0.00 / -0.95 / -0.05 cents). The log-frequency dominant sits on the equal-temperament grid within a cent in all cases. This is consistent with synthesized/sampled productions (pitch locked to a tuning grid); it is a *descriptive observation*, not a detection claim and not an artistic judgment. A human-performance dataset would be needed to interpret it further.

2. **Low-register adjacent tonal structure is abundant** in the transient (24 events) and AI (64 events) cases, e.g. centers [46.2, 51.9] Hz and [51.9, 58.3] Hz at 2.0 semitones. The 9056391 case shows one event ([65.4, 73.4] Hz). These are the structures the linear path reports as a single low-frequency mass (T6 Case A analogue at real scale).

3. **Tonal peakiness 0.26–0.30 and log entropy ~0.48** across cases — narrowband tonal concentration is similar in all three; no case stands out as noise-like.

## Per-case answer to the E-gate questions

| Case | What linear-Hz path already knows | What log path adds | Changes interpretation? | Cost |
|---|---|---|---|---|
| 9056391 | low centroid 504 Hz, LRA 4.53 | dominant 164.7 Hz (G2) locked to 0.0 cents; one low adjacent pair resolved | Refines "low-frequency content" into a specific pitch anchor + tuning lock | CQT ~18 s/full track |
| 9961e07 | transient-rich, centroid 823 | dominant 130.6 Hz (B1), 24 low-register adjacent tonal events | Adds structural detail the linear path cannot separate in the low band | same |
| 7b3f021 | bright AI track | dominant 72.6 Hz (F#1), 64 low events, near-zero tuning | The strongest case for log-frequency value: dense low-register tonal grid invisible to linear path | same |

## Verdict

Real cases provide incremental diagnostic evidence for the low-register/pitch-grid questions, with bounded cost (benchmark.json). No artistic claims; no claim that CQT "understands pitch".
