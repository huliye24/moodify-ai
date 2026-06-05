# MHP-865: Implement Feature Vector Contract

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-BUILD-046 / Build Plan-6A / V3
**Depends on**: MHP-863 (Data Model), MHP-852 (Feature Vector Brief)

## What Was Implemented

`compute_feature_vector(metrics: AudioMetrics) -> FeatureVector` in `v01_analyzer.py`.

8-D vector derived from existing AudioMetrics fields:
- `bass_balance` = tanh((rms_bass + 15) / 10)
- `warmth` = tanh((rms_low_mid + 10) / 10)
- `clarity` = tanh((rms_mid + 10) / 10)
- `presence_energy` = tanh((rms_presence + 15) / 12)
- `density` = 1.0 - min(1.0, crest_factor / 12)
- `stereo_width` = 1.0 - abs(correlation_lr)
- `transient_energy` = tanh((peak_db - rms_total - 6) / 8)
- `reality_index` = 1.0 - abs(dr - 12) / 18

### Also implemented

`weighted_feature_distance(fv1, fv2, genre) -> float` with genre-weighted Euclidean distance.

### Verification

```text
vocal_folk.wav before: bass=0.73, warmth=0.58, clarity=0.23...
vocal_folk.wav after (clean_master): bass=0.73, warmth=0.58, clarity=0.21...
Weighted distance: 0.049 (minimal change, correct for clean_master)
```

### Files Modified

- `moodify-core-package/src/moodify/v01_analyzer.py`: +70 lines

### Tests

12/12 existing tests pass.
