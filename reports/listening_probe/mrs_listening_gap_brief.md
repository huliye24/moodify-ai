# MRS Listening Gap Brief — MHP-201

## Gaps Between MRS Scores and Human Perception

| Gap | Evidence | Severity |
|-----|----------|----------|
| **Pseudo-MRS doesn't correlate with preference** | r=0.19 in NEM-002, all deltas negative | P0 |
| **MRS Open only mildly correlates** | Agreement 60.6%, no genre tuning | P1 |
| **No per-genre calibration** | Piano (56%) ≠ Electronic (71%) ≠ Rock (40%) | P1 |
| **Gate thresholds untuned to perception** | 0.0 delta threshold passes everything | P0 (fixed in MHP-071, but not validated with humans) |
| **over_dark severity ≠ annoyance** | "severe" FFT detection may not match "sounds bad to human" | P1 |
| **No "subtle improvement" detection** | Small but real improvements (Δ +2) not captured | P2 |

## Priority Actions

1. Build blind review protocol with reference tracks
2. Collect 100+ real human pairwise labels
3. Recalibrate gate thresholds per genre using human agreement data
4. Tune over_dark severity levels to match human annoyance ratings
