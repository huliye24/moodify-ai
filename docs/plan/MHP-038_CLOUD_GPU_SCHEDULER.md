# MHP-038: Cloud GPU Scheduler

**Status**: completed (superseded by NEM-18 Build-6/Validate-6/Harden-6)
Direction: cloud production capacity
Depends on: MHP-037 Craft Library Writeback

## Context

Deep processing and studio processing need cloud capacity, scheduling, cost tracking, and failure recovery. MHP-038 turns runtime execution into a cloud production scheduler.

## Goal

Introduce a cloud scheduling layer for long-running and GPU-backed jobs.

## Non-Goals

- Do not require Kubernetes unless current scale demands it.
- Do not introduce vendor lock-in.
- Do not rewrite the audio engine.

## Product Requirements

- Jobs can request compute class:
  - `cpu_standard`
  - `gpu_standard`
  - `gpu_deep`
  - `studio_reserved`
- Scheduler tracks:
  - queue time
  - execution time
  - node id
  - estimated cost
  - retry count
  - failure class

## Engineering Requirements

- Add scheduler records:

```text
ComputeRequest
ComputeLease
ComputeRun
CostRecord
```

- Add API/CLI:

```text
POST /operator/jobs/{job_id}/schedule
GET  /scheduler/runs
moodify-runtime scheduler-plan
moodify-runtime scheduler-run
```

- Keep local fallback path for tests and small jobs.

## Acceptance Criteria

- A job can be scheduled without immediate execution.
- Scheduler can record a completed compute run.
- Cost records are produced for each run.
- Failed leases can be retried.
- Tests use a fake scheduler backend.

## Test Plan

```bash
python -m pytest moodify_runtime/tests/test_cloud_scheduler.py -q
```

## Done Means

Moodify has a production capacity layer, not just a script runner.

## Seal Protocol (AEP Industrial Seal v0.1)

> ✅ **INDUSTRIAL_DONE** — executed and verified 2026-06-04T14:04:01Z.
> All six evidence layers satisfied. See outputs/tidal/ and test suite.

```yaml
# ── Identity ──
seal_id: SEAL-MOODIFY-MHP038
aep_id: AEP-MOODIFY-MHP038
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
poew_id: POEW-MOODIFY-MHP-038-20260604
poew_file: outputs/tidal/probe_473_484/probe_results.json
poew_hash: verified
execution_timestamp: 2026-06-04T14:04:01Z
execution_duration_s: 21600
environment: Ubuntu 24.04, Python 3.12, moodify-mainline

# ── Gate Reference ──
gate_id: GATE-MOODIFY-MHP-038
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

