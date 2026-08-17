# MFY-CR-P06 — Candidate Results (Stage 3)

All three candidates pass every hard gate. Deltas vs SOURCE (exact, from the
real measurement chain):

| Metric | SOURCE | A | B | C |
|---|---|---|---|---|
| Integrated LUFS | -13.94 | -13.91 (+0.03) | -13.54 (+0.40) | -13.01 (+0.93) |
| LRA (LU) | 12.68 | 12.68 (+0.00) | 13.00 (+0.32) | 13.23 (+0.55) |
| Crest factor (dB) | 14.05 | 14.06 (+0.01) | 14.02 (-0.03) | 13.51 (-0.54) |
| Spectral centroid (Hz) | 1560 | 1598 (+38) | 1732 (+172) | 1813 (+253) |
| Clipping ratio | 0.0 | 0.0 | 0.0 | 0.0 |
| Stereo correlation | 0.707 | 0.708 | 0.712 | 0.717 |
| Duration (s) | 182.16 | 182.16 | 182.16 | 182.16 |
| Channels | 2 | 2 | 2 | 2 |

## Hard gates (all PASS)

```text
NO_NEW_CLIPPING        PASS (0 new clipped samples)
DURATION_PRESERVED     PASS (182.16 s preserved)
CHANNELS_PRESERVED     PASS (2ch)
FINITE_AUDIO           PASS
NO_INVALID_SAMPLES     PASS
LOUDNESS_WITHIN_BUDGET PASS (|delta| <= 0.93 LU < 3 LU)
```

## Honest interpretation

- The candidates are surgical brightness/presence restorations of EXISTING
  content (centroid +38..+253 Hz). They do NOT restore missing HF above 14 kHz
  — the objective never claims that.
- Loudness stays within ±1 LU of source (no loudness war).
- Dynamics essentially untouched (LRA +/- 0.55 LU, crest -0.54 dB).
