# Craft SLO Definition — MHP-155

**Date**: 2026-06-04

## Craft SLO Targets

| SLO | Target | Measurement |
|-----|--------|-------------|
| Preset safety gate pass rate | 100% | All presets pass safety gate before adoption |
| Craft record accuracy | ≥85% gate-human agreement | Gate audit (MRS calibration workflow) |
| Preset reproducibility | ≥95% identical output for same input | MD5 of output WAV |
| Over-dark false positive | <10% | Per-preset FP rate |
| Over-bright false positive | <10% | Per-preset FP rate |
| Failure case coverage | ≥1 failure case per preset × genre | Failure case library query |

## Error Budget

| Defect | Max FP Rate | Action if Exceeded |
|--------|-----------|---------------------|
| over_dark | 10% | Recalibrate band tolerances |
| over_bright | 10% | Adjust high-freq threshold |
| transient_damage | 5% | Reduce compression ratio |
| vocal_thinning | 5% | Increase vocal presence gain |
