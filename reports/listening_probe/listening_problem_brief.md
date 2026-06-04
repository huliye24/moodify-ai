# Listening Problem Brief — MHP-197

**Date**: 2026-06-04 | **E-Chain**: ECHAIN-MOODIFY-MRS-LISTENING-003

## Problem Statement

NEM-MOODIFY-MRS-002 proved the MRS scoring infrastructure works end-to-end. But Validate-6 exposed a fundamental gap: **gate accuracy = 9.1%** against human labels. The MRS formula and over_dark detector were fixed, but we never validated the *gate criteria* against real human listening judgments.

The core problem: **MRS scores don't reliably predict what humans perceive as "better" audio.**

## Why This Matters

Every gate decision in the Studio OS pipeline depends on MRS. If MRS doesn't align with human perception, the entire quality assurance system is operating on a flawed metric.

## Current State (from NEM-002 evidence)

| Metric | Value | Target |
|--------|-------|--------|
| Gate accuracy vs human labels | 9.1% | ≥85% |
| MRS Open agreement | 60.6% | ≥70% |
| Pseudo-MRS Spearman r | 0.19 | ≥0.7 |
| Human-labeled samples | 33 (synthesized) | ≥100 (real listeners) |

## Phase Transition Target

```
calibrated scoring engine → human-aligned production quality evaluation system
```

This requires:
1. Blind listening protocols — remove expectation bias
2. Pairwise preference (A/B) — more reliable than absolute scoring
3. Genre-specific calibration — electronic ≠ piano ≠ vocal
4. Reviewer agreement measurement — measure label quality
5. MRS-human correlation tracking — continuous feedback loop
