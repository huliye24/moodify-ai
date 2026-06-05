# MHP-889: MAP Regression Evidence Pack
**Status**: done

## Test History
| Date | Tests | Presets | Artifacts | Judge |
|------|-------|---------|-----------|-------|
| 2026-06-05 | 60/60 | 3/3 × 10 artifacts | 30/30 | 6/6 gates accept |
| 2026-06-05 | 12/12 | 3/3 × 5 artifacts | 15/15 | N/A (pre-Build) |

## Regression Baseline
- v01 pipeline: 7 tests (E2E, all presets, auto, missing file, unknown preset)
- API v01: 5 tests (WAV generation, all presets × 3)
- MAP data model: 48 tests (FeatureVector × 4, ProblemVector × 5, ScanResult × 4, Compute × 8, Distance × 3, ToProblemVector × 11, GenreWeights × 3, MRS Adapter × 4, DamageLoss × 4, Integration × 3)

## Code Diff (Probe vs Build)
+1373 lines, 8 files, 0 deletions of existing behavior.
