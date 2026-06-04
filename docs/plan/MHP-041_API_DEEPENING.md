# MHP-041: API Deepening — Live Studio + Scheduler + Calibration Endpoints

**Status**: proposed  
**Direction**: 6-Step Plan Cycle — E1 (Execution 1)  
**Depends on**: MHP-040 Studio OS Alpha  
**Protocol**: 泫榛 6-Step Plan Protocol — Plan = 2E + 2V + 1S + 1N

## Context

MHP-035 built the FastAPI server with 18+ endpoints, but three critical subsystems have *stub endpoints*:

- `POST /operator/jobs/{job_id}/writeback-craft` → hardcoded placeholder
- `GET /scheduler/runs` → hardcoded empty list
- `GET /craft/records` → now connected but needs `POST` for writeback

Additionally, the **studio subsystem** (MHP-036) has full CLI support but **zero API endpoints**. Operators can only use the CLI to create clients/projects/orders — the Console UI has no studio views backed by real API data.

The **calibration subsystem** (MHP-039) also has no API endpoints at all — calibration reviews, audits, and threshold proposals are CLI-only.

## Goal

Wire all three subsystems into the FastAPI with live, tested endpoints. Every stub becomes a real implementation. Every CLI-only subsystem gets API parity.

## Non-Goals

- Do not add authentication/authorization (alpha scope)
- Do not add WebSocket or streaming endpoints
- Do not add database migration (JSONL is still the storage layer)
- Do not redesign the HTML console in this step (MHP-044 handles UI contract)

## Engineering Requirements

### 1. Studio API Endpoints (parity with CLI)

```text
POST   /studio/clients
GET    /studio/clients
POST   /studio/projects
GET    /studio/projects
POST   /studio/orders
GET    /studio/orders
POST   /studio/orders/{order_id}/link-job
GET    /studio/orders/{order_id}/context
POST   /studio/notes
GET    /studio/notes
```

Each endpoint must call the corresponding `studio.py` function and return the same JSON shape as the CLI.

### 2. Scheduler API Endpoints (replace stubs)

```text
POST   /scheduler/requests          — schedule_job()
GET    /scheduler/requests           — list all requests
POST   /scheduler/leases/{request_id} — allocate_lease()
POST   /scheduler/runs               — record_compute_run()
GET    /scheduler/runs               — list runs
GET    /scheduler/costs              — list costs
```

### 3. Calibration API Endpoints (new)

```text
POST   /calibration/sample-sets
GET    /calibration/sample-sets
POST   /calibration/reviews
GET    /calibration/reviews
POST   /calibration/audits/{set_id}
GET    /calibration/audits
POST   /calibration/thresholds
GET    /calibration/thresholds
```

### 4. Craft Writeback (already partially done — ensure POST works)

```text
POST   /operator/jobs/{job_id}/writeback-craft  — connected to writeback_delivery_to_craft_record()
GET    /craft/records                            — connected to list_craft_records()
```

## Acceptance Criteria

- All 25+ API endpoints return real data (no stub responses)
- Studio: create client → project → order → link job → get context → verified in test
- Scheduler: create request → allocate lease → record run → cost appears → verified in test
- Calibration: create set → submit review → run audit → propose threshold → verified in test
- Existing 38 tests still pass
- New API endpoint tests (MHP-043 will deepen coverage)

## Test Plan

```bash
python3 -m pytest moodify_runtime/tests/test_api_studio.py -v
python3 -m pytest moodify_runtime/tests/test_api_scheduler.py -v
python3 -m pytest moodify_runtime/tests/test_api_calibration.py -v
```

## Done Means

Every subsystem that has a Python module also has an API surface. The Console UI (MHP-035) can add Studio, Scheduler, and Calibration views without hitting stubs.
