# MHP-075: MRS Calibration Guide — Operator Documentation

**Status**: proposed
**Direction**: NEM-MOODIFY-MRS-002 / Build-6 / S1 (Systemization)
**Depends on**: MHP-074 (gate tests pass)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

Build-6 has produced three new MRS capabilities: genre thresholds, graduated over_dark, and calibrated pseudo-MRS. Without documentation, future operators and AI agents won't know how to tune these for new genres, add calibration samples, or interpret gate audit results.

## Goal

Write `docs/MRS_CALIBRATION_GUIDE.md` covering:

1. **What MRS measures** — the four sub-scores (peak, rms, crest, dc) and how they relate to perceived quality
2. **Genre thresholds** — how to read `configs/mrs_thresholds.yaml`, how to add a new genre, what each threshold means
3. **Over-dark detection** — the 3-level system, how to interpret per-band scores, when to trust/reject the detector
4. **Calibration workflow** — how to submit human reviews, run gate audits, propose threshold changes
5. **Interpreting audit reports** — false positive vs false negative, accuracy targets, when to recalibrate
6. **D_ref maintenance** — what D_ref is, when to recalibrate it, how to run `calibrate_dref`

## Acceptance Criteria
- `docs/MRS_CALIBRATION_GUIDE.md` with all 6 sections
- Code examples for each workflow
- Clear enough that an operator who didn't build the system can run a calibration cycle
- Existing tests still pass (docs only)
