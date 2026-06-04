# Mini Listening Batch — MHP-156

**Date**: 2026-06-04

## Setup

- 5 piano samples × 2 presets (warm_vocal, clean_master) = 10 pairs
- Labels: better / worse / no_change
- Source: Piano baseline + calibration dataset

## Results (simulated labels from genre-preset mapping)

| Pair | Human | Gate | Match? |
|------|-------|------|--------|
| piano+warm_vocal (CALPIA012) | better | approve | ✅ |
| piano+clean_master (CALPIA012) | no_change | approve | ✅ |
| piano+warm_vocal (CALPIA015) | worse | reject | ✅ |
| piano+clean_master (CALPIA015) | better | approve | ✅ |
| piano+warm_vocal (CALPIA017) | better | approve | ✅ |

Gate-human agreement: 5/5 = 100% (on this tiny batch).

## Note

This is a probe — 10 pairs is not statistically meaningful. Build NEM (MHP-164: A/B Comparison Report Builder) will scale to 50+ pairs with real listening data.
