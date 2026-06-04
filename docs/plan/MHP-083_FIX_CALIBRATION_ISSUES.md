# MHP-083: Fix Calibration Issues — Patch Failures from Validate-6

**Status**: completed
**Direction**: NEM-MOODIFY-MRS-002 / Harden-6 / E1 (Execution)
**Depends on**: MHP-082 (Gate Decision)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

Validate-6 (MHP-080) identified gate accuracy gaps. MHP-082 made the gate decision. Harden-6 begins by fixing the highest-priority issues found during validation.

Expected issue classes (to be confirmed by actual Validate-6 results):
1. **Threshold boundary errors** — some genre thresholds too strict/loose
2. **Over-dark false triggers** — mild darkness flagged as severe in specific frequency bands
3. **MRS weight instability** — calibrated weights overfit to small per-genre samples
4. **D_ref staleness** — MRS Open D_ref hasn't been recalibrated

## Goal

Fix every issue classified as P0 or P1 from the gate accuracy analysis:
- Adjust genre thresholds based on sensitivity analysis
- Tune over-dark band-specific thresholds
- Add regularization to MRS weight calibration (prevent overfitting)
- Recalibrate D_ref if MRS Open accuracy is below expectation

### Fix priority
| Priority | Action |
|----------|--------|
| P0 | Adjust thresholds where gate accuracy < 70% |
| P1 | Fix over-dark false triggers (>20% FP rate in any genre) |
| P2 | Recalibrate D_ref if MRS Open correlation < 0.5 |
| P3 | Document remaining limitations |

## Acceptance Criteria
- All P0 issues fixed and verified
- All P1 issues fixed or documented with deferral reason
- Every fix has a regression test
- Fix log written to `reports/nem_mrs_002/fix_log.md`
- Existing 129+ Studio OS tests still pass
- Gate accuracy re-measured after fixes (target ≥85%)
