# MHP-079: MRS Comparison — Calibrated vs Pseudo-MRS vs MRS Open

**Status**: completed
**Direction**: NEM-MOODIFY-MRS-002 / Validate-6 / V1 (Validation)
**Depends on**: MHP-078 (pipeline run complete)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

We now have three MRS measurements on the same 50+ audio pairs:
1. **pseudo_mrs** — the original placeholder formula (fixed weights)
2. **calibrated pseudo-MRS** — grid-search-optimized weights from MHP-073
3. **MRS Open v0.3.1** — the external benchmark engine

We need to compare them quantitatively to answer:
- Does the calibrated pseudo-MRS correlate better with human labels than the original?
- How does each correlate with MRS Open v0.3.1?
- Which metric best predicts human "better/worse" decisions?

## Goal

Generate a comparison report:

1. Compute Spearman rank correlation between each MRS variant and human labels
2. Compute pairwise correlations between the three MRS variants
3. Compute agreement rate: % of pairs where MRS delta sign matches human "better"/"worse"
4. Per-genre breakdown of all metrics
5. Recommendation: which MRS variant should be the production default

### Metrics to compute
```python
metrics = {
    "spearman_r_vs_human": {variant: float},
    "agreement_rate": {variant: float},  # MRS sign matches human
    "pairwise_correlation": {(v1, v2): float},
    "per_genre": {
        genre: {
            variant: {"r": float, "agreement": float}
        }
    },
    "best_variant": str,
    "best_r": float,
}
```

## Acceptance Criteria
- Comparison report: `reports/nem_mrs_002/mrs_comparison.md`
- All 3 variants compared against human labels
- Per-genre breakdown
- Clear recommendation for production default
- Statistical significance noted where sample size is small
