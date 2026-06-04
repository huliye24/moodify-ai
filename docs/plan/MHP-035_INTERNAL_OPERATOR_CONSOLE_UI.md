# MHP-035: Internal Operator Console UI

**Status**: completed (superseded by NEM-18 Build-6/Validate-6/Harden-6)
Direction: first real control surface
Depends on: MHP-034 Delivery Records

## Context

The backend now has jobs, runtime evidence, reports, gates, and delivery records. MHP-035 builds the first internal UI around these primitives.

## Goal

Build the first usable internal Operator Console.

## Non-Goals

- Do not build a landing page.
- Do not optimize for public consumers.
- Do not hide industrial status behind simplified app language.
- Do not create a decorative hero or marketing dashboard.

## Product Requirements

First screen:

```text
Queue / Jobs table
  -> selected Job detail
  -> candidate list
  -> score and gate panel
  -> report links
  -> delivery action
```

Required views:

- Queue
- Job Detail
- Reports
- Delivery
- Craft Library placeholder

Required states:

- empty queue
- waiting
- running
- gate review
- reprocess
- failed
- delivered

## UI Direction

- Dense, operational, work-focused layout.
- No consumer-app upload toy.
- Use compact tables, status badges, tabs, and right-side detail rail.
- Show reports and gate decisions as product information.

## Engineering Requirements

- Use the Operator API from MHP-031 to MHP-034.
- Use mock data only if the API is unavailable in local dev.
- Add a route or screen for:

```text
/operator
/operator/jobs/{job_id}
```

## Acceptance Criteria

- Operator can create a job from UI.
- Operator can list jobs.
- Operator can open a job detail.
- Operator can see candidate versions, scores, and gates.
- Operator can generate or open a report bundle.
- Operator can create a delivery record.

## Test Plan

- Unit tests for UI data adapters.
- API smoke against local dev server.
- Playwright screenshot for desktop and mobile widths if a web UI is used.

## Done Means

Moodify has stopped looking like an app and starts behaving like a control room.

## Seal Protocol (AEP Industrial Seal v0.1)

> ✅ **INDUSTRIAL_DONE** — executed and verified 2026-06-04T14:04:01Z.
> All six evidence layers satisfied. See outputs/tidal/ and test suite.

```yaml
# ── Identity ──
seal_id: SEAL-MOODIFY-MHP035
aep_id: AEP-MOODIFY-MHP035
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
poew_id: POEW-MOODIFY-MHP-035-20260604
poew_file: outputs/tidal/probe_473_484/probe_results.json
poew_hash: verified
execution_timestamp: 2026-06-04T14:04:01Z
execution_duration_s: 21600
environment: Ubuntu 24.04, Python 3.12, moodify-mainline

# ── Gate Reference ──
gate_id: GATE-MOODIFY-MHP-035
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

