# MHP-076: Build-6 Next Entry — Generate Validate-6 (MHP-077→082)

**Status**: completed
**Direction**: NEM-MOODIFY-MRS-002 / Build-6 / N1 (Next Entry)
**Depends on**: MHP-075 (calibration guide written)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

Build-6 has built the MRS calibration infrastructure. The next phase is Validate-6: build a real calibration dataset, run the pipeline, and measure gate accuracy against human labels.

## Build-6 Results

| MHP | Type | Task | Result |
|-----|------|------|--------|
| 071 | E1 | Genre-Specific Threshold Config | ✅ `configs/mrs_thresholds.yaml` — 5 genres, per-genre overrides |
| 072 | E2 | Graduated Over-Dark Detector | ✅ `moodify_runtime/over_dark.py` — 3-level (none/mild/severe) |
| 073 | V1 | Pseudo-MRS Weight Calibration | ✅ `scripts/calibrate_pseudo_mrs.py` — grid search engine |
| 074 | V2 | Gate Threshold Unit Tests | ✅ 16 tests — genre dispatch, over-dark levels, boundaries, combined |
| 075 | S1 | MRS Calibration Guide | ✅ `docs/MRS_CALIBRATION_GUIDE.md` — 6 sections |
| 076 | N1 | Build-6 Next Entry | ✅ Validate-6 entry confirmed |

### Key Artifacts

| Artifact | Path | Purpose |
|----------|------|---------|
| Threshold config | `configs/mrs_thresholds.yaml` | Per-genre gate thresholds |
| Over-dark detector | `moodify_runtime/over_dark.py` | Graduated 3-level detection |
| Calibration script | `scripts/calibrate_pseudo_mrs.py` | Weight grid search |
| Gate tests | `moodify_runtime/tests/test_mrs_gate.py` | 16 tests covering all paths |
| Calibration guide | `docs/MRS_CALIBRATION_GUIDE.md` | Operator documentation |

### Test Status

- 135 tests total (119 Studio OS + 16 MRS gate)
- All green, 0.79s
- Genre dispatch: electronic/piano/vocal/rock/ambient thresholds verified
- Over-dark: none→pass, mild→reprocess, severe→reject verified
- Backward compat: binary flag still works

### Calibration Results (synthetic data)

- Best weights: peak=0.10, rms=0.20, crest=0.50, dc=0.20
- Default weights: peak=0.25, rms=0.25, crest=0.35, dc=0.15
- Note: Grid search engine works. Real calibration needs real labeled pairs in Validate-6.

## Next: Validate-6 (MHP-077→082)

Validate-6 plan files already exist. Next step is MHP-077: build calibration dataset with 50+ real labeled samples.

## Acceptance Criteria

- [x] Build-6 completion verified (6/6 tasks done)
- [x] 6 Validate-6 plan files confirmed (MHP-077→082 exist)
- [x] PROJECT_ROADMAP.md updated
