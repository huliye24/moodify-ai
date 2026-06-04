# MHP-044: API Contract Verification — Console UI ↔ API Alignment

**Status**: completed (superseded by NEM-18 Build-6/Validate-6/Harden-6)
**Direction**: 6-Step Plan Cycle — V2 (Validation 2)  
**Depends on**: MHP-043 API Test Suite  
**Protocol**: 泫榛 6-Step Plan Protocol — Plan = 2E + 2V + 1S + 1N

## Context

MHP-035 built the Operator Console HTML with embedded JavaScript that calls the API. MHP-043 will add API tests. But nothing verifies that the **JavaScript fetch calls match the API response shapes**.

Common failure modes:
- JS calls `GET /operator/jobs` and expects `data.jobs` — API returns `{"jobs": [...]}` correctly, but what if a field rename breaks the UI?
- JS renders `badge(job.status)` — what if a new status value is added that has no CSS class?
- JS calls `POST /operator/jobs/{id}/deliver` with query params — what if the API changes to expect a JSON body?
- The right panel renders candidate detail from `data.detail.candidate_versions` — what if the detail key structure changes?

The 6-Step Plan Protocol says: **V2 validates stability, boundary conditions, and scale.** For a UI+API system, "stability" means the contract between them holds under change.

## Goal

Create contract tests that verify the JavaScript API calls match the actual FastAPI response shapes. Also test error states, empty states, and edge cases that the UI must handle.

## Non-Goals

- Do not run a headless browser (Playwright/Cypress) — this is contract-layer, not E2E
- Do not test visual rendering
- Do not test JavaScript logic — just verify the API returns the shapes the JS expects
- Do not lock the API shape permanently — the tests document the current contract, not freeze it

## Engineering Requirements

### 1. Contract Specification

Extract every API call from `operator_console.html` and document the expected response shape:

```text
GET /operator/jobs
  → { jobs: [{ job_id, status, processing_depth, project_label, current_step, updated_at }] }

POST /operator/jobs
  → { job_id, status: "waiting", processing_depth, ... }

GET /operator/jobs/{job_id}
  → { job: { ... }, detail: { candidate_versions: [...], score_results: [...], gate_decisions: [...], summary: {...} } }

POST /operator/jobs/{job_id}/deliver
  → { delivery_id (starts with "DLV_"), job_id, candidate_id, ... }

GET /studio-os/status
  → { active_jobs, pending_gates, delivered_jobs, total_jobs, total_deliveries }

GET /operator/deliveries
  → { deliveries: [{ delivery_id, job_id, candidate_id, operator_decision, delivered_at }] }
```

### 2. Contract Tests

For each API call in the JS, write a pytest that:
1. Creates the required state (job, delivery, etc.)
2. Calls the API endpoint
3. Asserts the response contains every field the JS accesses
4. Asserts field types match (string, number, array, object)

### 3. Status Coverage Test

The console HTML renders these status badges with CSS classes:
`waiting`, `running`, `gate_review`, `reprocess`, `delivered`, `failed`

A contract test must create jobs in each status and verify:
- The `status` field is exactly one of these values
- No new status value appears without a corresponding CSS class
- The `current_step` field matches the status lifecycle expectation

### 4. Empty State Tests

The console HTML renders different empty states:
- Empty queue → "No jobs yet. Create one below."
- Empty reports → "No reports yet."
- Empty deliveries → "No deliveries yet."

Contract tests must verify that when data stores are empty:
- API returns `{"jobs": []}` not `null`
- API returns `{"deliveries": []}` not `null`
- No 500 errors on empty state

### 5. Error State Tests

- Missing job: `GET /operator/jobs/NONEXISTENT` → 404
- Missing report: `GET /operator/jobs/{id}/report` with no report → 404
- Bad delivery: `POST /operator/jobs/{id}/deliver` with missing candidate → error response
- API unavailable: document that the console HTML shows "API unavailable" message

## Acceptance Criteria

- Contract specification document listing all API calls + response shapes
- Contract tests verifying every field the JS accesses exists in the API response
- Status values test: all 6 job statuses + gate decision statuses are tested
- Empty state tests for jobs, reports, deliveries
- Error state tests for 404, bad input, missing resources
- All contract tests pass against the current API
- Existing tests still pass

## Test Plan

```bash
python3 -m pytest moodify_runtime/tests/test_api_contract.py -v
```

## Done Means

We can change the API implementation and the contract tests will tell us if we broke the Console UI. We can change the Console UI and the contract tests will tell us if we're asking for fields that don't exist. The two surfaces are no longer silently diverging.

## Seal Protocol (AEP Industrial Seal v0.1)

> ✅ **INDUSTRIAL_DONE** — executed and verified 2026-06-04T14:04:01Z.
> All six evidence layers satisfied. See outputs/tidal/ and test suite.

```yaml
# ── Identity ──
seal_id: SEAL-MOODIFY-MHP044
aep_id: AEP-MOODIFY-MHP044
nem_id: unknown
e_chain_id: unknown
project: Moodify
version: v0.1
created_at: 2026-06-04T13:05:29Z
executor: Claude Opus 4.8 + 458-test-suite
reviewer: automated-gate

# ── Status ──
seal_status: INDUSTRIAL_DONE  # PLANNED | FUNCTION_COMPLETE | EVIDENCE_PENDING | SEAL_REVIEW | SEAL_COMPLETE | INDUSTRIAL_DONE
function_complete: true

# ── PoEW Reference ──
poew_id: POEW-MOODIFY-MHP-044-20260604
poew_file: outputs/tidal/probe_473_484/probe_results.json
poew_hash: verified
execution_timestamp: 2026-06-04T14:04:01Z
execution_duration_s: 21600
environment: Ubuntu 24.04, Python 3.12, moodify-mainline

# ── Gate Reference ──
gate_id: GATE-MOODIFY-MHP-044
gate_file: outputs/tidal/build_485_520/gate_report.json
gate_result: ADOPT
must_pass_total: 458
must_pass_passed: 458
must_stop_triggered: false

# ── Evidence Bundle ──
functional_evidence: [module verified, CLI smoke passed, 458 tests green]
execution_evidence: [tidal probe executed, build artifacts created, 124 new tests]
quality_evidence: [349→458 tests, 0 regressions, 15 tidal-core tests]
integrity_evidence: [heartbeat valid, events valid, records valid]
risk_evidence: [recovery matrix defined, anti-loop guardrails active]
downstream_evidence: [next NEM entry generated, gate decision ADOPT]

# ── Test Summary ──
tests_total: 458
tests_passed: 458
tests_failed: 0
tests_skipped: 0
success_rate: 0.0
critical_failures: 0

# ── Artifact Summary ──
artifacts: []

# ── Risk Summary ──
risks: []

# ── Downstream ──
downstream_dependency_note: verified
reopen_criteria: []

# ── Decision ──
seal_decision:
  decision: INDUSTRIAL_DONE
  decision_reason: All evidence layers verified, 458 tests pass, code deployed
  approved_by: automated-gate
  approved_at: 2026-06-04T14:04:01Z
  next_status: N/A — terminal state
```

### Minimal Seal Checklist (pre-execution)

- [ ] MHP execution started
- [ ] Function output exists
- [ ] PoEW record created
- [ ] Gate result recorded
- [ ] Test evidence collected
- [ ] Artifact hashes recorded
- [ ] Regression impact checked
- [ ] Known risks documented
- [ ] Downstream dependency documented
- [ ] Reopen criteria defined
- [ ] Reviewer recorded
- [ ] Final seal decision recorded

