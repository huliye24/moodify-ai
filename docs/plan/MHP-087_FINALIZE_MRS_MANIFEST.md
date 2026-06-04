# MHP-087: Finalize MRS Manifest — Thresholds Doc, D_ref Audit, Version Bump

**Status**: completed
**Direction**: NEM-MOODIFY-MRS-002 / Harden-6 / S1 (Systemization)
**Depends on**: MHP-086 (integration audit complete)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

NEM-18's Harden phase requires that every node leave behind durable engineering assets. For MRS-002, these are:

1. **Final threshold values** — the calibrated, validated, per-genre thresholds
2. **D_ref audit** — when was D_ref last calibrated? What is its current value? Should it change?
3. **MRS variant decision** — which variant is production default? (calibrated pseudo-MRS or MRS Open?)
4. **Version bump** — MRS scoring moves from experimental to adopted

## Goal

1. **`configs/mrs_thresholds.yaml`**: Update with final calibrated values (not Build-6 estimates)
2. **D_ref audit**: Document current D_ref value, last calibration date, recalibration procedure
3. **MRS variant decision**: Document which variant is production default and why
4. **`docs/MRS_CALIBRATION_GUIDE.md`**: Update with final values and lessons learned
5. **README.md**: Update MRS section with v0.2.0 status
6. **CHANGELOG.md**: Add MRS-002 entries
7. **Version bump**: MRS scoring v0.2.0 (adopted)
8. **X-CLP score**: Re-estimate with MRS hardening included

### X-CLP Re-estimation
```text
R_speed: 75 → 78 (MRS calibration cycle completed fast)
S_structure: 70 → 75 (mrs_engine.py = single entry point, cleaner)
M_maintainability: 78 → 82 (150+ tests, calibration guide, gate audit trail)
E_evolvability: 72 → 78 (configurable thresholds, genre dispatch, graduated over_dark)

L_code = (0.78 × 0.75 × 0.82 × 0.78) × 100 ≈ 37.4 → Gate: Script (20-39)
Target next cycle: L_code ≥ 60 (NEM-ready)
```

## Acceptance Criteria
- `configs/mrs_thresholds.yaml` finalized with validated values
- D_ref audit written
- MRS variant decision documented with evidence
- README MRS section updated
- CHANGELOG updated through MHP-086
- All tests still pass (docs + config only)
