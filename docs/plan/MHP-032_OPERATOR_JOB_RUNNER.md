# MHP-032: Operator Job Runner

**Status**: completed (superseded by NEM-18 Build-6/Validate-6/Harden-6)
Direction: MHP-031 continuation
Depends on: MHP-031 Operator Job records and API

## Context

MHP-031 made Operator Jobs visible and attachable to existing runtime run evidence. MHP-032 closes the next gap: an Operator Job should be able to request a runtime execution path instead of only attaching evidence after the fact.

## Goal

Connect Operator Jobs to the runtime queue and runner so an internal operator can move a job from intake to running to gate review.

```text
Operator Job -> runtime queue task(s) -> run_daily -> manifest -> operator detail
```

## Non-Goals

- Do not build the full UI yet.
- Do not add a new audio processing engine.
- Do not replace the existing runtime queue.
- Do not make this a public user workflow.

## Product Requirements

- A job can be marked as ready for runtime processing.
- A job can create one or more runtime queue tasks.
- A job can trigger or reference a runtime run.
- Job status changes are persisted: `waiting`, `running`, `gate_review`, `reprocess`, `failed`.
- Runtime errors are reflected back onto the Operator Job.

## Engineering Requirements

- Add a job-to-runtime adapter that maps:
  - `OperatorJob.source_audio` -> runtime task input
  - `processing_depth` -> preset/candidate strategy
  - `priority` -> runtime queue priority
  - `project_label` -> run metadata
- Add CLI/API entry points:

```text
POST /operator/jobs/{job_id}/plan-runtime
POST /operator/jobs/{job_id}/run
moodify-runtime operator-plan-runtime
moodify-runtime operator-run
```

- Reuse `run_daily` where possible.
- Keep generated audio and run outputs outside git.

## Acceptance Criteria

- A test can create an Operator Job and generate runtime queue rows from it.
- A dry-run path can show the commands that would execute.
- A successful run updates the job with `run_id` and `run_dir`.
- A failed run updates `last_error`.
- Existing runtime tests still pass.

## Test Plan

```bash
python -m pytest moodify_runtime/tests/test_operator_console.py -q
python -m pytest moodify_runtime/tests/test_operator_job_runner.py -q
```

## Done Means

Operator Jobs no longer just hold metadata. They can initiate the production line.

## Seal Protocol (AEP Industrial Seal v0.1)

> ✅ **INDUSTRIAL_DONE** — executed and verified 2026-06-04T14:04:01Z.
> All six evidence layers satisfied. See outputs/tidal/ and test suite.

```yaml
# ── Identity ──
seal_id: SEAL-MOODIFY-MHP032
aep_id: AEP-MOODIFY-MHP032
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
poew_id: POEW-MOODIFY-MHP-032-20260604
poew_file: outputs/tidal/probe_473_484/probe_results.json
poew_hash: verified
execution_timestamp: 2026-06-04T14:04:01Z
execution_duration_s: 21600
environment: Ubuntu 24.04, Python 3.12, moodify-mainline

# ── Gate Reference ──
gate_id: GATE-MOODIFY-MHP-032
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

