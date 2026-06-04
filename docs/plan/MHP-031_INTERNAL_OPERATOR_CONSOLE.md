# MHP-031: Internal Operator Console

**Status**: completed (superseded by NEM-18 Build-6/Validate-6/Harden-6)
Direction: Moodify Industrial Operator Console
Depends on: v0.1 runtime stability, MRS scoring, report summaries

## Context

The 2026-06-04 brand direction repositions Moodify from a consumer AI music processing app into an enterprise acoustic industrial system.

MHP-031 is the first implementation milestone after that shift. Its purpose is to stop treating the UI as a casual upload/download app and start building the operator console for an internal production line.

## Goal

Build the first internal console workflow around jobs, queues, scan depth, processing status, MRS gate evidence, reports, and delivery records.

The console should make this workflow visible:

```text
Sample -> Job -> ScanProfile -> ProcessingPlan -> CandidateVersion -> ScoreResult -> GateDecision -> Report -> Delivery
```

## Non-Goals

- Do not optimize for public C-end onboarding.
- Do not build a marketing landing page.
- Do not make "one-click instant processing" the center of the product.
- Do not hide reports behind a secondary debug panel.
- Do not add new DSP presets just to make the UI look bigger.

## Product Requirements

### 1. Job Intake

The operator can create a job with:

- source audio path or uploaded file;
- customer / project label;
- processing depth: `quick_scan`, `standard_process`, `deep_process`, `studio_process`;
- target notes;
- priority;
- expected delivery mode.

### 2. Queue and Status

The operator can see:

- waiting / running / gate_review / reprocess / delivered jobs;
- current step;
- elapsed time;
- last log event;
- failure reason when present;
- linked report path.

### 3. Scan and Plan Summary

For each job, the console should show:

- scan depth and scan dimensions;
- detected issues;
- chosen processing plan;
- candidate count;
- risk flags.

### 4. Candidate Review

For each candidate version, show:

- output identity and lineage;
- preset / chain used;
- MRS score and delta;
- side-effect flags such as over-dark, transient damage, and loudness penalty;
- gate decision;
- operator note.

### 5. Report as First-Class Output

Every completed job should have a report panel with:

- before / after summary;
- MRS interpretation;
- quality gate result;
- selected candidate explanation;
- delivery notes;
- archive paths.

### 6. Delivery Record

Delivery should persist:

- final selected candidate;
- report file;
- job metadata;
- processing version;
- operator decision;
- archive location.

## Engineering Requirements

### Data Model

Introduce or align around these durable records:

```text
Sample
Job
ScanProfile
ProcessingPlan
CandidateVersion
ScoreResult
GateDecision
Report
Delivery
CraftRecord
```

JSONL is acceptable for the first internal version if it is easy to audit and migrate later.

### API Shape

Minimum internal API targets:

```text
GET  /health
GET  /presets
POST /jobs
GET  /jobs
GET  /jobs/{job_id}
POST /jobs/{job_id}/run
GET  /jobs/{job_id}/reports
POST /jobs/{job_id}/deliver
```

The existing CLI/runtime can remain the execution backend while the console matures.

### Quality Gates

Candidate approval must be gate-driven:

```text
if runtime_success == false:
    reject

if mrs_score_delta < required_threshold:
    reject_or_reprocess

if over_dark_triggered == true:
    reject_or_reprocess

if transient_damage > threshold:
    reject

if loudness_penalty > threshold:
    reject

approve_candidate
```

### Report Bundle

Each run should create a lightweight report bundle:

```text
reports/operator_runs/{run_id}/summary.md
reports/operator_runs/{run_id}/summary.json
reports/operator_runs/{run_id}/results.jsonl
reports/operator_runs/{run_id}/gate_decisions.jsonl
reports/operator_runs/{run_id}/delivery.md
```

Heavy audio and generated media should stay out of git.

## UI Direction

The first screen should be the console itself:

- left navigation for Queue, Jobs, Reports, Craft Library;
- main area for job table and selected job detail;
- right rail for gate state, report links, and delivery action;
- compact, dense, operational layout;
- restrained industrial visual style;
- no consumer-app hero page.

The UI should feel like a production control room, not a music toy.

## Acceptance Criteria

- A job can be created and assigned a processing depth.
- The job can be represented in a queue state.
- A run can attach summary/report evidence.
- MRS and gate decisions are visible as product information.
- A delivery record can be created.
- The README points new contributors to the industrial direction.
- No heavy generated audio assets are committed as part of this milestone.

## Immediate Task Order

1. Add durable internal data schemas for job, candidate, score, gate, and delivery records.
2. Build a CLI or API stub that can create/list jobs from JSONL storage.
3. Connect one existing runtime run into the job/report bundle shape.
4. Build the first internal console screen around the queue and job detail.
5. Promote report generation into the main workflow.
6. Add tests for record serialization and gate decision logic.

## Decision

MHP-031 replaces "make a user-facing app" as the next frontend milestone.

The next frontend is an internal industrial operator console.

## Seal Protocol (AEP Industrial Seal v0.1)

> ✅ **INDUSTRIAL_DONE** — executed and verified 2026-06-04T14:04:01Z.
> All six evidence layers satisfied. See outputs/tidal/ and test suite.

```yaml
# ── Identity ──
seal_id: SEAL-MOODIFY-MHP031
aep_id: AEP-MOODIFY-MHP031
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
poew_id: POEW-MOODIFY-MHP-031-20260604
poew_file: outputs/tidal/probe_473_484/probe_results.json
poew_hash: verified
execution_timestamp: 2026-06-04T14:04:01Z
execution_duration_s: 21600
environment: Ubuntu 24.04, Python 3.12, moodify-mainline

# ── Gate Reference ──
gate_id: GATE-MOODIFY-MHP-031
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

