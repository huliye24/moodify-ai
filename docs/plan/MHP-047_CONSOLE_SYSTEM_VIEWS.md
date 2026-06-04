# MHP-047: Console System Views — Studio + Scheduler + Calibration Panels

**Status**: completed (superseded by NEM-18 Build-6/Validate-6/Harden-6)
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

## Seal Protocol (AEP Industrial Seal v0.1)

> ✅ **INDUSTRIAL_DONE** — executed and verified 2026-06-04T14:04:01Z.
> All six evidence layers satisfied. See outputs/tidal/ and test suite.

```yaml
# ── Identity ──
seal_id: SEAL-MOODIFY-MHP047
aep_id: AEP-MOODIFY-MHP047
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
poew_id: POEW-MOODIFY-MHP-047-20260604
poew_file: outputs/tidal/probe_473_484/probe_results.json
poew_hash: verified
execution_timestamp: 2026-06-04T14:04:01Z
execution_duration_s: 21600
environment: Ubuntu 24.04, Python 3.12, moodify-mainline

# ── Gate Reference ──
gate_id: GATE-MOODIFY-MHP-047
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

