# MHP-047: Console System Views — Studio + Scheduler + Calibration Panels

**Status**: proposed
**Direction**: 6-Step Plan — E1 (Execution)
**Depends on**: MHP-045, MHP-046
**Protocol**: 泫榛 6-Step Plan Protocol

## Evidence

- MHP-043 confirmed: Studio API returns correct data shapes
- MHP-043 confirmed: Scheduler API returns correct data shapes
- MHP-043 confirmed: Calibration API returns correct data shapes
- MHP-044 confirmed: API contracts are stable
- The Console HTML has views for Queue, Jobs, Reports, Delivery, and a Craft placeholder
- But Studio, Scheduler, and Calibration views are missing — the data is there, the UI is not

## Goal

Add Studio, Scheduler, and Calibration views to the Operator Console HTML. Each view must use the API endpoints verified in MHP-043 and render data from real JSONL stores.

## Non-Goals

- Don't redesign the CSS framework
- Don't add real-time polling (refresh button is sufficient)
- Don't add auth or session management

## Requirements

### Studio View
- List clients / projects / orders
- Create new client/project/order from UI
- Link jobs to orders
- View order context (client + project + linked jobs)

### Scheduler View
- List compute requests / leases / runs / costs
- Create schedule request from UI

### Calibration View
- List sample sets / reviews / audits / thresholds
- Submit review from UI

## Acceptance Criteria
- 3 new sidebar nav items render their views
- Each view loads data from its API endpoint
- Create forms work for each subsystem
- Contract tests (MHP-044) still pass
- Existing 95 tests still pass

## Test Plan
```bash
python3 -m pytest moodify_runtime/tests/test_api_contract.py -v
```
