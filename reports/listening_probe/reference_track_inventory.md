# Reference Track Inventory — MHP-200

## Golden Reference Tracks

These are well-produced reference tracks used to calibrate reviewers before each session.

| # | Genre | Reference Type | Source |
|---|-------|---------------|--------|
| 1 | electronic | Clean master reference | NEM-002 calibration: CALELE001 (Control Theory) |
| 2 | piano | Natural acoustic reference | NEM-002 baseline: piano.wav |
| 3 | vocal | Vocal clarity reference | NEM-002 baseline: vocal_folk.wav |
| 4 | rock | Full-band reference | NEM-002 calibration: CALROC007 (Black Therapy) |
| 5 | ambient | Space/depth reference | NEM-002 calibration: CALAMB028 |

## Anchor Pairs

Known-better and known-worse pairs for reviewer training.

| Pair Type | Source | Expected |
|-----------|--------|----------|
| Clearly better | warm_vocal on piano (+5 Δ MRS) | "Better" |
| Clearly worse | warm_vocal on over-dark piano (-36 Δ MRS) | "Worse" |
| No difference | bypass_control (same in/out) | "No difference" |
| Subtle improvement | clean_master on well-mastered electronic | Reviewer-dependent |
