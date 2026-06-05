# MHP-866: Implement Diagnosis Vector Contract

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-BUILD-046 / Build Plan-6A / V4
**Depends on**: MHP-863 (Data Model), MHP-853 (Diagnosis Taxonomy)

## What Was Implemented

`to_problem_vector(report: DiagnosisReport) -> ProblemVector` in `v01_diagnostics.py`.

### Problem IDs (13 total, 4 categories)

**Spectral (7)**: sub_overpower, sub_weak, bass_forward, bass_recessed, presence_harsh, presence_weak, air_weak

**Dynamics (3)**: over_compressed, peak_too_hot, flat_dynamics

**Stereo (2)**: ultra_wide, near_mono (only when channels==2)

### Confidence formula

`confidence = min(1.0, abs(observed - threshold) / margin)` where margin varies by category (3dB spectral, 1.5 dynamics, 0.15 stereo).

### Diagnosis loss

`diagnosis_loss = min(1.0, sum(weight * confidence for active problems) / 10.0)`

### Verification

```text
vocal_folk.wav (clean): ProblemVector(problems=[], diagnosis_loss=0.0)
```

0 active problems — correct for a healthy vocal folk file.

### Files Modified

- `moodify-core-package/src/moodify/v01_diagnostics.py`: +131 lines

### Tests

12/12 existing tests pass.
