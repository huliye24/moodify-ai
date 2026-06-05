# MHP-867: MAP Core Tests

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-BUILD-046 / Build Plan-6A / S5
**Depends on**: MHP-863, MHP-864, MHP-865, MHP-866

## What Was Implemented

Created `moodify-core-package/tests/test_map_data_model.py` with 37 tests across 7 test classes:

| Class | Tests | Covers |
|-------|-------|--------|
| TestFeatureVector | 4 | defaults, to_list(), to_dict() precision, completeness |
| TestProblemVector | 5 | defaults, to_dict(), severity counting, empty state |
| TestScanResultAcousticFields | 4 | defaults, populated fields, None exclusion, zero exclusion |
| TestComputeFeatureVector | 8 | range checks, bass-heavy, thin, compressed, wide, mono, clamp |
| TestWeightedFeatureDistance | 3 | zero distance, positive distance, unknown genre fallback |
| TestToProblemVector | 11 | healthy, over_compressed, flat_dynamics, sub_overpower, presence_harsh, severity, confidence near/far, diagnosis_loss, mono exclusion, air_weak severity |
| TestGenreWeights | 3 | all 5 genres, 8 weights each, range check |

## Test Run Evidence

```text
49 passed in 4.41s (7 pipeline + 5 API + 37 MAP data model)
```
