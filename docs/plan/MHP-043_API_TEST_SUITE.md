# MHP-043: Operator API Test Suite — FastAPI TestClient Coverage

**Status**: proposed  
**Direction**: 6-Step Plan Cycle — V1 (Validation 1)  
**Depends on**: MHP-041 API Deepening  
**Protocol**: 泫榛 6-Step Plan Protocol — Plan = 2E + 2V + 1S + 1N

## Context

The Operator API has 25+ endpoints across 5 subsystems (jobs, studio, scheduler, calibration, craft). **Zero of them have API-level tests.** All existing tests exercise the Python functions directly through `RuntimeConfig` — they never go through HTTP.

This means:

- No test verifies that FastAPI route parameters are correctly parsed
- No test verifies HTTP error codes (404, 422, 500)
- No test verifies CORS, content-type headers, or response shapes
- The API could have a broken route and we wouldn't know until the Console UI fails
- `POST` endpoints with query parameters (FastAPI default for non-body args) might behave unexpectedly

The 6-Step Plan Protocol says: **V must enter real execution.** For an API server, "real execution" means HTTP requests through the TestClient.

## Goal

Create a comprehensive API test suite using `fastapi.testclient.TestClient` that hits every endpoint with valid and invalid inputs, and verifies correct HTTP semantics.

## Non-Goals

- Do not test the HTML rendering (that's MHP-044)
- Do not load-test or performance-test
- Do not test with a real uvicorn server process (TestClient is sufficient for contract testing)
- Do not mock the storage layer — use tmp_path like existing tests

## Engineering Requirements

### 1. Test Structure

One test file per subsystem:

```text
moodify_runtime/tests/test_api_jobs.py         — /operator/jobs/*
moodify_runtime/tests/test_api_studio.py       — /studio/*
moodify_runtime/tests/test_api_scheduler.py    — /scheduler/*
moodify_runtime/tests/test_api_calibration.py  — /calibration/*
moodify_runtime/tests/test_api_system.py       — /health, /studio-os/status
```

### 2. Coverage Matrix

Every endpoint must have at minimum:

| Test Case | Description |
|-----------|-------------|
| Happy path | Valid inputs, expect 200 + correct JSON shape |
| Not found | Missing resource, expect 404 |
| Bad input | Invalid parameters, expect 422 or 400 |
| Empty state | No data yet, expect valid empty response (not error) |

### 3. TestClient Setup Pattern

```python
from fastapi.testclient import TestClient
from moodify_runtime.operator_api import app

def test_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

Each test file must use `tmp_path` for data isolation, injecting a custom config via environment or config path.

### 4. Specific Endpoint Coverage

#### Jobs (14 endpoints)
- `GET /health` → `{"status": "ok"}`
- `GET /studio-os/status` → keys: active_jobs, pending_gates, delivered_jobs, total_jobs, total_deliveries
- `POST /operator/jobs` → creates job, returns job dict
- `GET /operator/jobs` → lists jobs, supports ?status= filter
- `GET /operator/jobs/{job_id}` → returns job + detail
- `GET /operator/jobs/{job_id}` with nonexistent → 404
- `POST /operator/jobs/{job_id}/plan-runtime` → returns plan
- `POST /operator/jobs/{job_id}/run` → dry_run by default
- `POST /operator/jobs/{job_id}/attach-run` → attaches evidence
- `POST /operator/jobs/{job_id}/report` → builds report bundle
- `GET /operator/jobs/{job_id}/report` → returns report path
- `POST /operator/jobs/{job_id}/deliver` → creates delivery
- `GET /operator/jobs/{job_id}/delivery` → returns delivery
- `POST /operator/jobs/{job_id}/writeback-craft` → creates craft record

#### Studio (10 endpoints)
- CRUD for clients, projects, orders
- link-job, context, notes

#### Scheduler (6 endpoints)
- requests, leases, runs, costs

#### Calibration (8 endpoints)
- sample-sets, reviews, audits, thresholds

#### Craft (2 endpoints)
- POST writeback, GET records

#### Static (2 endpoints)
- GET / → HTML
- GET /operator → HTML

## Acceptance Criteria

- 40+ API tests across 5 test files
- Every endpoint has at least 1 happy-path test
- At least 10 endpoints have error-case tests (404/422)
- All tests use TestClient (real HTTP request/response cycle)
- Test suite completes in under 1 second (no real audio processing in API tests)
- Existing 38 tests still pass

## Test Plan

```bash
python3 -m pytest moodify_runtime/tests/test_api_*.py -v
```

## Done Means

The API is no longer "code that probably works." It is "code that has been called through HTTP and verified." The distinction is what separates a script from a service.
