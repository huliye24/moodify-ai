# MHP-852: Feature Vector Weighting Brief — Completion Report

**Generated**: 2026-06-05
**Status**: done
**E-Chain**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6B

## Key Finding

`AudioMetrics` is a flat 13-field object. MAP needs an 8-D feature vector `f = [b, w, c, p, d, s, t, r]` with per-genre weights.

## Feature Vector Formula

All 8 dimensions derivable from existing AudioMetrics fields via `tanh` or linear clamp to [0, 1]:

| Dim | Name | From | Formula |
|-----|------|------|---------|
| b | Bass Balance | rms_bass | `tanh((rms_bass + 15) / 10)` |
| w | Warmth | rms_low_mid | `tanh((rms_low_mid + 10) / 10)` |
| c | Clarity | rms_mid | `tanh((rms_mid + 10) / 10)` |
| p | Presence | rms_presence | `tanh((rms_presence + 15) / 12)` |
| d | Density | crest_factor | `1.0 - min(1.0, crest/12)` |
| s | Stereo Width | correlation_lr | `1.0 - abs(correlation_lr)` |
| t | Transient Energy | peak_db, rms_total | `tanh((peak - rms - 6) / 8)` |
| r | Reality Index | dynamic_range_db | `1.0 - abs(dr - 12) / 18` |

## Genre Weights

5 genres defined (vocal, piano, electronic, orchestral, default). Each has 8 weights. Weighted Euclidean distance for comparison.

## Implementation

Build NEM MHP-865 (Implement Feature Vector Contract). Worker creates `compute_feature_vector(metrics) -> FeatureVector` + YAML config for genre weights. Architect approves `FeatureVector` dataclass in v01_types.py (MHP-863).
