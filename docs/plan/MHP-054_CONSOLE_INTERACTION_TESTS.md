# MHP-054: Console UI Interaction Tests — Browser-like Flow Verification

**Status**: proposed
**Direction**: 6-Step Plan — E2 (Execution)
**Depends on**: MHP-053
**Protocol**: 泫榛 6-Step Plan Protocol

## Evidence

- Console HTML has 8 views (Queue, Jobs, Reports, Delivery, Craft, Studio, Scheduler, Calibration)
- API contracts are verified (MHP-044)
- But no test verifies that the HTML renders correctly with real data
- No test simulates a user clicking through the workflow: create job → plan → run → review → deliver
- The JS functions call `api()` which may fail if the server isn't running

## Goal

Create interaction tests that simulate browser flow using FastAPI TestClient:
1. Load the Console HTML → verify it contains all 8 view render functions
2. POST a job via API → verify the Queue view shows it
3. Attach run → verify the Job Detail view shows candidates
4. Deliver → verify the Delivery view shows the record
5. Create studio entities → verify Studio view renders them
6. Schedule a request → verify Scheduler view renders it
7. Submit a review → verify Calibration view renders it

## Acceptance Criteria

- 8 interaction tests (one per view)
- Each test: create data via API, request the Console HTML, verify the view renders
- No real browser required (TestClient)
- Existing 107+ tests still pass

## Test Plan
```bash
python3 -m pytest moodify_runtime/tests/test_console_interaction.py -v
```
