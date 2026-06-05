# MHP-863: Implement MAP Data Model

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-BUILD-046 / Build Plan-6A: Data Model / E1
**Depends on**: MHP-862 (Close Probe NEM), MHP-852 (Feature Vector Brief), MHP-853 (Diagnosis Taxonomy)
**Protocol**: AWJ Stack + E-Chain 54

## What Was Implemented

Added three MAP v0.2 dataclasses to `v01_types.py`:

### FeatureVector
8-D feature vector with `to_list()`, `to_dict()`:
`[bass_balance, warmth, clarity, presence_energy, density, stereo_width, transient_energy, reality_index]`

### ProblemEntry
Single problem diagnosis: `problem_id`, `category`, `severity`, `confidence`, `weight`, `description`

### ProblemVector
Collection of ProblemEntry with `diagnosis_loss`, `high_severity_count`, `medium_severity_count`

### GENRE_WEIGHTS
5-genre weight matrix constant.

## Files Modified

- `moodify-core-package/src/moodify/v01_types.py`: +83 lines

## Acceptance Criteria

- [x] FeatureVector dataclass with 8 named dimensions.
- [x] ProblemEntry dataclass with 6 fields.
- [x] ProblemVector dataclass with diagnosis_loss.
- [x] GENRE_WEIGHTS for 5 genres.
- [x] All dataclasses have to_dict().
- [x] Existing tests continue to pass (backwards compatible — no imports changed).
