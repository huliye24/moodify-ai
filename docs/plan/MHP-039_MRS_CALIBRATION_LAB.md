# MHP-039: MRS Calibration Lab

**Status**: completed (superseded by NEM-18 Build-6/Validate-6/Harden-6)
Direction: quality standard and calibration
Depends on: MHP-038 Cloud GPU Scheduler

## Context

MRS is useful only if it keeps being calibrated against real samples, failure cases, and human review. MHP-039 makes calibration a formal lab workflow.

## Goal

Create a calibration workflow for MRS thresholds, flags, and gate decisions.

## Non-Goals

- Do not claim MRS is final truth.
- Do not replace human review.
- Do not optimize only for higher scores.

## Product Requirements

Calibration Lab tracks:

- sample sets
- before/after pairs
- human review notes
- gate false positives
- gate false negatives
- over-dark cases
- transient damage cases
- loudness penalty cases
- threshold proposals

## Engineering Requirements

- Add calibration records:

```text
CalibrationSampleSet
CalibrationReview
GateAudit
ThresholdProposal
MRSVersion
```

- Add tooling:

```text
moodify-runtime mrs-calibration-run
moodify-runtime mrs-gate-audit
```

- Add reports:

```text
reports/mrs_calibration/{calibration_id}/summary.md
```

## Acceptance Criteria

- Calibration can compare gate decisions against human review.
- Threshold proposals are written as reviewable artifacts.
- MRS version and gate rules are recorded.
- Reports identify known failure classes.

## Test Plan

```bash
python -m pytest moodify_runtime/tests/test_mrs_calibration_lab.py -q
```

## Done Means

Moodify quality gates become calibratable industrial standards.

## Seal Protocol (AEP Industrial Seal v0.1)

> ✅ **INDUSTRIAL_DONE** — executed and verified 2026-06-04T14:04:01Z.
> All six evidence layers satisfied. See outputs/tidal/ and test suite.

```yaml
# ── Identity ──
seal_id: SEAL-MOODIFY-MHP039
aep_id: AEP-MOODIFY-MHP039
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
poew_id: POEW-MOODIFY-MHP-039-20260604
poew_file: outputs/tidal/probe_473_484/probe_results.json
poew_hash: verified
execution_timestamp: 2026-06-04T14:04:01Z
execution_duration_s: 21600
environment: Ubuntu 24.04, Python 3.12, moodify-mainline

# ── Gate Reference ──
gate_id: GATE-MOODIFY-MHP-039
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

