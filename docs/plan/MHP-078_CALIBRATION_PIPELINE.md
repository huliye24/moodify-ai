# MHP-078: Run Calibration Pipeline — Before/After MRS + Gate Decisions + Human Labels

**Status**: completed
**Direction**: NEM-MOODIFY-MRS-002 / Validate-6 / E2 (Execution)
**Depends on**: MHP-077 (dataset ready)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

We have a calibration dataset (50+ samples, 30+ labeled). Now we need to run the full pipeline:
1. Process every sample through its genre-appropriate preset
2. Compute before/after MRS scores
3. Run the new graduated over_dark detector
4. Apply genre-specific gate thresholds
5. Record gate decisions
6. Compare gate decisions against human labels

## Goal

Run `scripts/run_calibration_pipeline.py` that:
1. Reads `data/calibration/mrs_002/registry.jsonl`
2. For each sample, runs `moodify.cli process` with the genre-appropriate preset
3. Computes MRS Open v0.3.1 + calibrated pseudo-MRS on before/after
4. Runs graduated over_dark detection
5. Applies genre-specific gate thresholds
6. Stores all results in `outputs/nem_mrs_002/calibration_run/`

### Pipeline output
```text
outputs/nem_mrs_002/calibration_run/
├── manifest.csv           # per-sample results
├── gate_decisions.jsonl   # automated gate decisions
├── metrics.jsonl          # before/after MRS scores
├── over_dark.jsonl        # graduated over_dark assessments
├── summary.json           # aggregate statistics
└── run.log
```

## Acceptance Criteria
- Pipeline script runs end-to-end without manual intervention
- All 50+ samples processed (or documented failures)
- Gate decisions recorded for every sample
- Graduated over_dark assessments recorded
- Run log preserved for audit
- Existing tests still pass (pipeline is additive)
