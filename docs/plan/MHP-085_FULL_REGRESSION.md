# MHP-085: Full Regression — All Studio OS Tests + New MRS Tests

**Status**: completed
**Direction**: NEM-MOODIFY-MRS-002 / Harden-6 / V1 (Validation)
**Depends on**: MHP-084 (MRS engine refactored)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

After MHP-083 (fixes) and MHP-084 (refactor), we need to prove nothing broke — across the entire Studio OS test suite AND the new MRS-specific tests.

This is a broader regression than MHP-067 (which covered only Studio OS). Now we have:
- 129 Studio OS tests (from NEM-001)
- New MRS gate tests (from MHP-074)
- Calibration pipeline tests
- MRS engine tests

## Goal

Run the complete test suite:

1. All Studio OS tests (119 unit + 3 real audio + 7 smoke)
2. MRS gate threshold tests (≥12 tests from MHP-074)
3. MRS engine score_audio() tests
4. Over-dark detector tests (3-level classification)
5. Genre threshold dispatch tests
6. Backward compatibility: pseudo_mrs() and compare_before_after() still work

## Acceptance Criteria
- **0 test failures** across all categories
- **Test count ≥ 150** (129 Studio OS + 21+ new MRS)
- Slow tests pass (real audio with new MRS scoring)
- Full stack smoke passes (API still serves MRS data correctly)
- Regression report: `reports/nem_mrs_002/regression_report.md`
