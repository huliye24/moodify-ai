# MHP-050: Error Recovery & Edge Cases — Boundary Validation

**Status**: proposed
**Direction**: 6-Step Plan — V2 (Validation)
**Depends on**: MHP-049
**Protocol**: 泫榛 6-Step Plan Protocol

## Evidence

- MHP-044 contract tests cover basic 404/400 cases
- But edge cases are untested:
  - Concurrent delivery of the same candidate
  - Deliver → writeback → deliver again (state machine violation)
  - Order with no linked jobs (empty context)
  - Calibration audit with zero reviews
  - cost estimates for zero-duration runs
  - Job with attached detail but no candidates
  - Report bundle generation for a failed job

## Goal

Add edge-case tests for state transitions, empty sub-objects, and concurrent/double-submit scenarios. Fix any bugs discovered.

## Non-Goals

- Don't add locking/concurrency control (alpha scope)
- Don't performance test

## Acceptance Criteria

- At least 10 new edge-case tests
- Any discovered bugs are fixed
- Existing 95+ tests still pass

## Test Plan
```bash
python3 -m pytest moodify_runtime/tests/test_edge_cases.py -v
```
