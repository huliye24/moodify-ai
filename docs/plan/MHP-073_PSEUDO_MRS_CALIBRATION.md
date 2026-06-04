# MHP-073: Pseudo-MRS Weight Calibration — Grid Search on Calibration Data

**Status**: proposed
**Direction**: NEM-MOODIFY-MRS-002 / Build-6 / V1 (Validation)
**Depends on**: MHP-072 (over_dark graduated)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

The current `pseudo_mrs()` in `metrics.py:216` uses fixed weights:

```python
return 100.0 * (0.25 * peak_score + 0.25 * rms_score + 0.35 * crest_score + 0.15 * dc_score)
```

These weights (0.25, 0.25, 0.35, 0.15) were chosen by intuition. We need to calibrate them against actual human preference data. The right approach isn't guessing better weights — it's running a grid search against labeled data and picking weights that maximize correlation with human judgments.

## Goal

1. Load the calibration reviews from `calibration/reviews.jsonl` (human_decision: better/worse/no_change)
2. For each reviewed candidate, compute pseudo-MRS with different weight combinations
3. Grid search over weight space: each weight ∈ {0.10, 0.15, ..., 0.50}, sum = 1.0
4. Score each weight combination by: Spearman correlation with human ranking + gate decision agreement rate
5. Output the best weight set with correlation score

### Grid search parameters
```python
weights_space = {
    "peak":   [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40],
    "rms":    [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40],
    "crest":  [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50],
    "dc":     [0.05, 0.10, 0.15, 0.20],
}
# Constraint: peak + rms + crest + dc = 1.0
```

## Acceptance Criteria
- `scripts/calibrate_pseudo_mrs.py` runs grid search
- Best weights documented with correlation score
- Updated `pseudo_mrs()` uses calibrated weights (or configurable weights)
- Calibration report shows weight → correlation mapping
- Existing 129 tests still pass (pseudo_mrs values may shift slightly)
