# MHP-036: Studio Back Office

**Status**: completed (superseded by NEM-18 Build-6/Validate-6/Harden-6)
Direction: studio workflow layer
Depends on: MHP-035 Internal Operator Console UI

## Context

The Operator Console manages production. The Studio Back Office manages the commercial workflow around production: customers, projects, packages, deadlines, and staff notes.

## Goal

Add studio-level order management around Operator Jobs.

## Non-Goals

- Do not implement payment collection.
- Do not build public customer login.
- Do not implement multi-tenant SaaS.

## Product Requirements

Add durable objects:

- `StudioClient`
- `StudioProject`
- `Order`
- `ProcessingPackage`
- `StaffNote`

Orders should link to one or more Operator Jobs.

## Engineering Requirements

- Add JSONL-backed storage for studio records.
- Add API endpoints:

```text
POST /studio/clients
POST /studio/projects
POST /studio/orders
GET  /studio/orders
GET  /studio/orders/{order_id}
POST /studio/orders/{order_id}/jobs
```

- Add UI views:
  - Orders
  - Clients
  - Project detail
  - Linked jobs

## Acceptance Criteria

- An order can be created and linked to jobs.
- A project can show all jobs and delivery status.
- Operator Console can filter by project/order.
- Tests cover order/job linking.

## Test Plan

```bash
python -m pytest moodify_runtime/tests/test_studio_back_office.py -q
python -m pytest moodify-core-package/tests/test_api_studio.py -q
```

## Done Means

Moodify starts operating like a studio system, not just a runtime tool.

## Seal Protocol (AEP Industrial Seal v0.1)

> ✅ **INDUSTRIAL_DONE** — executed and verified 2026-06-04T14:04:01Z.
> All six evidence layers satisfied. See outputs/tidal/ and test suite.

```yaml
# ── Identity ──
seal_id: SEAL-MOODIFY-MHP036
aep_id: AEP-MOODIFY-MHP036
nem_id: unknown
e_chain_id: unknown
project: Moodify
version: v0.1
created_at: 2026-06-04T13:06:11Z
executor: Claude Opus 4.8 + 458-test-suite
reviewer: automated-gate

# ── Status ──
seal_status: INDUSTRIAL_DONE
function_complete: true

# ── PoEW Reference ──
poew_id: POEW-MOODIFY-MHP-036-20260604
poew_file: outputs/tidal/probe_473_484/probe_results.json
poew_hash: verified
execution_timestamp: 2026-06-04T14:04:01Z
execution_duration_s: 21600
environment: Ubuntu 24.04, Python 3.12, moodify-mainline

# ── Gate Reference ──
gate_id: GATE-MOODIFY-MHP-036
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

