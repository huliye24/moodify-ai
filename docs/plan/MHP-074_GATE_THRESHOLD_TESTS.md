# MHP-074: Gate Threshold Unit Tests — Verify New Thresholds Gate Correctly

**Status**: completed
**Direction**: NEM-MOODIFY-MRS-002 / Build-6 / V2 (Validation)
**Depends on**: MHP-073 (pseudo-MRS calibrated)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

Build-6 has introduced three changes to the gate system:
1. Genre-specific thresholds (MHP-071)
2. Graduated over_dark detection (MHP-072)
3. Calibrated pseudo-MRS weights (MHP-073)

These changes modify `decide_candidate_gate()` behavior. We need comprehensive tests that verify each threshold path, including edge cases and genre interactions.

## Goal

Write tests covering:

### 1. Genre threshold dispatch
- `decide_candidate_gate(genre="electronic")` uses electronic thresholds
- `decide_candidate_gate(genre="piano")` uses piano thresholds
- `decide_candidate_gate(genre=None)` uses defaults

### 2. over_dark graduated gating
- `level="none"` + good MRS → approve
- `level="mild"` + marginal MRS → reprocess (not reject)
- `level="severe"` + any MRS → reject

### 3. Threshold boundary tests
- `mrs_delta = threshold - 0.01` → reprocess
- `mrs_delta = threshold + 0.01` → pass
- `transient = threshold - 0.01` → pass
- `transient = threshold + 0.01` → reject

### 4. Combined gate scenarios
- Good MRS + mild over_dark → reprocess (not reject)
- Bad MRS + no over_dark → reprocess
- Severe over_dark + good MRS → reject (over_dark dominates)

## Acceptance Criteria
- `moodify_runtime/tests/test_mrs_gate.py` with ≥12 tests
- All threshold dispatch paths tested
- All over_dark level → decision paths tested
- Edge case: all thresholds at boundaries
- Existing 129 tests still pass
