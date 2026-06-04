# MHP-033: Report Bundle System

**Status**: completed (superseded by NEM-18 Build-6/Validate-6/Harden-6)
Direction: report-first industrial workflow
Depends on: MHP-032 Operator Job Runner

## Context

MHP-031 and MHP-032 connect jobs to runtime evidence. MHP-033 makes reports a first-class product output rather than a side file created after processing.

## Goal

Create a standard Operator Report Bundle for each job.

```text
summary.md
summary.json
candidate_versions.jsonl
score_results.jsonl
gate_decisions.jsonl
delivery.md
manifest.csv
```

## Non-Goals

- Do not design customer-facing visual PDFs yet.
- Do not add chart rendering unless existing evidence already exists.
- Do not store heavy audio files in the report bundle.

## Product Requirements

- Every completed or failed job has a report bundle path.
- The bundle explains:
  - input identity
  - processing depth
  - candidate versions
  - MRS / pseudo MRS interpretation
  - gate decisions
  - selected next action
- Operators can read the report without opening raw logs.

## Engineering Requirements

- Add `build_operator_report_bundle(job_id)` using existing detail data.
- Add durable paths under:

```text
reports/operator_runs/{job_id}/
```

- Add CLI/API:

```text
POST /operator/jobs/{job_id}/report
GET  /operator/jobs/{job_id}/report
moodify-runtime operator-report
```

- Keep full raw logs referenced, not duplicated, unless a compact tail is needed.

## Acceptance Criteria

- Report bundle is generated from a real attached run.
- JSON/JSONL files validate.
- Markdown summary includes gate counts and candidate ranking.
- The job record stores `report_path`.
- Tests cover missing detail, failed candidates, and all-pass candidates.

## Test Plan

```bash
python -m pytest moodify_runtime/tests/test_operator_report_bundle.py -q
python -m pytest moodify-core-package/tests/test_api_operator.py -q
```

## Done Means

A Moodify result is no longer just an audio output. It is an explainable industrial report bundle.

## Seal Protocol (AEP Industrial Seal v0.1)

> ✅ **INDUSTRIAL_DONE** — executed and verified 2026-06-04T14:04:01Z.
> All six evidence layers satisfied. See outputs/tidal/ and test suite.

```yaml
# ── Identity ──
seal_id: SEAL-MOODIFY-MHP033
aep_id: AEP-MOODIFY-MHP033
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
poew_id: POEW-MOODIFY-MHP-033-20260604
poew_file: outputs/tidal/probe_473_484/probe_results.json
poew_hash: verified
execution_timestamp: 2026-06-04T14:04:01Z
execution_duration_s: 21600
environment: Ubuntu 24.04, Python 3.12, moodify-mainline

# ── Gate Reference ──
gate_id: GATE-MOODIFY-MHP-033
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

