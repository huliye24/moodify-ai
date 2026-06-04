# MHP-048: Dedicated List Functions — Scheduler & Calibration Data Access

**Status**: proposed
**Direction**: 6-Step Plan — E2 (Execution)
**Depends on**: MHP-047
**Protocol**: 泫榛 6-Step Plan Protocol

## Evidence

- `operator_api.py` lines for `/scheduler/requests` and `/calibration/sample-sets` use inline `read_jsonl()` calls
- Scheduler has `list_scheduler_runs()` and `list_scheduler_costs()` but no `list_requests()` or `list_leases()`
- Calibration has `list_calibration_reviews()` but no `list_sample_sets()`, `list_audits()`, or `list_thresholds()`
- Inline `read_jsonl` in API handlers breaks the pattern established by every other subsystem

## Goal

Add dedicated list functions to scheduler.py and mrs_calibration.py. Replace all inline `read_jsonl` calls in operator_api.py with proper function calls.

## Non-Goals

- Don't change storage format
- Don't add filtering beyond what exists

## Requirements

### scheduler.py
```python
def list_scheduler_requests(cfg) -> List[Dict]
def list_scheduler_leases(cfg) -> List[Dict]
```

### mrs_calibration.py
```python
def list_calibration_sample_sets(cfg) -> List[Dict]
def list_calibration_audits(cfg) -> List[Dict]
def list_calibration_thresholds(cfg) -> List[Dict]
```

### operator_api.py
Replace all `from .utils import read_jsonl` inline calls with the new dedicated functions.

## Acceptance Criteria
- All list functions have docstrings
- API handlers call dedicated functions, not inline read_jsonl
- Existing 95 tests still pass
- Pattern consistency: every subsystem follows the same list-X pattern

## Test Plan
```bash
python3 -m pytest moodify_runtime/tests/ -q
```
