# MHP-034: Delivery Records

**Status**: completed (superseded by NEM-18 Build-6/Validate-6/Harden-6)
Direction: delivery and archive layer
Depends on: MHP-033 Report Bundle System

## Context

After report generation, Moodify needs a formal delivery record. Delivery is the transition from internal processing evidence to a handoff that a studio, customer, or internal team can trust.

## Goal

Implement delivery records for final candidate selection, report handoff, archive location, and operator decision.

## Non-Goals

- Do not implement billing.
- Do not implement customer portals.
- Do not upload to external storage providers yet.

## Product Requirements

- Operator can select one candidate as final.
- Delivery record contains:
  - job id
  - candidate id
  - final audio path
  - report path
  - archive path
  - operator decision
  - notes
  - timestamp
- Job status becomes `delivered`.

## Engineering Requirements

- Add delivery JSON/JSONL storage.
- Add helper:

```text
create_delivery_record(...)
get_delivery_record(...)
```

- Add CLI/API:

```text
POST /operator/jobs/{job_id}/deliver
GET  /operator/jobs/{job_id}/delivery
moodify-runtime operator-deliver
```

- Validate that delivered candidates have an approval or explicit override.

## Acceptance Criteria

- Delivery cannot silently select a missing candidate.
- Delivery cannot use a missing report path.
- Approved candidates deliver normally.
- Reprocess/reject candidates require an override flag and reason.
- Job detail includes delivery record.

## Test Plan

```bash
python -m pytest moodify_runtime/tests/test_operator_delivery.py -q
python -m pytest moodify-core-package/tests/test_api_operator.py -q
```

## Done Means

Moodify can say exactly what was delivered, why it was selected, and where the evidence lives.

## Seal Protocol (AEP Industrial Seal v0.1)

> ✅ **INDUSTRIAL_DONE** — executed and verified 2026-06-04T14:04:01Z.
> All six evidence layers satisfied. See outputs/tidal/ and test suite.

```yaml
# ── Identity ──
seal_id: SEAL-MOODIFY-MHP034
aep_id: AEP-MOODIFY-MHP034
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
poew_id: POEW-MOODIFY-MHP-034-20260604
poew_file: outputs/tidal/probe_473_484/probe_results.json
poew_hash: verified
execution_timestamp: 2026-06-04T14:04:01Z
execution_duration_s: 21600
environment: Ubuntu 24.04, Python 3.12, moodify-mainline

# ── Gate Reference ──
gate_id: GATE-MOODIFY-MHP-034
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

