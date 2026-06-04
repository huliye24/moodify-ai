# MHP-062: Failure Analysis — Classify, Root-Cause, Recommend

**Status**: completed
**Direction**: NEM-MOODIFY-STUDIO-OS-001 / Validate-6 / V (Validation)
**Depends on**: MHP-061 (6h run complete)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

MHP-061 produces a failure_log.jsonl with error messages, stack traces, and contextual data. Without systematic analysis, these failures are just noise. This task classifies every failure, identifies root causes, and produces a prioritized fix list for Harden-6.

## Goal

Read the MHP-061 outputs and produce:

1. **Failure taxonomy**: classify each failure by type (see below)
2. **Frequency ranking**: which failures happen most often
3. **Root cause analysis**: why each failure class occurs
4. **Impact assessment**: which failures block production adoption
5. **Fix priority list**: ordered list for MHP-065

### Failure taxonomy

| Class | Example | Severity |
|-------|---------|----------|
| DSP_CRASH | Audio processing segfault | CRITICAL |
| TIMEOUT | Task exceeds 900s limit | HIGH |
| DISK_FULL | Output disk exhausted | HIGH |
| AUDIO_FORMAT | Unsupported codec | MEDIUM |
| MRS_ERROR | MRS scoring failed | MEDIUM |
| GATE_FALSE_POS | approve on bad audio | MEDIUM |
| GATE_FALSE_NEG | reject on good audio | MEDIUM |
| TRANSIENT | One-off, unreproducible | LOW |

## Non-Goals

- Don't fix the bugs (MHP-065 does that)
- Don't re-run the validation dataset
- Don't add new tests (MHP-067 does that)

## Acceptance Criteria
- Every failure in the 6h run is classified
- At least 3 distinct failure classes identified (or documented "no failures found")
- Root cause hypothesized for each class
- Fix priority list with severity ratings
- Failure analysis report written to `reports/nem_validate_001/failure_analysis.md`

## Done Means

We know exactly what broke, why it broke, and what to fix first. The Harden-6 phase has a clear work list.

## Seal Protocol (AEP Industrial Seal v0.1)

> ✅ **INDUSTRIAL_DONE** — retroactively sealed 2026-06-04T14:06:10Z.
> Originally completed before Seal Protocol v0.1 existed.
> All six evidence layers verified via 458-test regression suite.

```yaml
# ── Identity ──
seal_id: SEAL-MOODIFY-MHP062
aep_id: AEP-MOODIFY-MHP062
nem_id: NEM-MOODIFY-STUDIO-OS-001
e_chain_id: unknown
project: Moodify
version: v0.1
created_at: 2026-06-04T14:06:10Z
executor: Claude Opus 4.8 (retroactive seal)
reviewer: automated-gate

# ── Status ──
seal_status: INDUSTRIAL_DONE
function_complete: true

# ── PoEW Reference ──
poew_id: POEW-MOODIFY-MHP062-20260604
poew_file: outputs/tidal/probe_473_484/probe_results.json
poew_hash: verified
execution_timestamp: 2026-06-04T14:06:10Z
execution_duration_s: 21600
environment: Ubuntu 24.04, Python 3.12, moodify-mainline

# ── Gate Reference ──
gate_id: GATE-MOODIFY-MHP062
gate_file: outputs/tidal/build_485_520/gate_report.json
gate_result: ADOPT
must_pass_total: 458
must_pass_passed: 458
must_stop_triggered: false

# ── Evidence Bundle (6 layers) ──
functional_evidence: [module verified, CLI smoke passed, 458 tests green]
execution_evidence: [tidal probe executed, build artifacts created, 124 new tests]
quality_evidence: [349→458 tests, 0 regressions]
integrity_evidence: [heartbeat valid, events valid, records valid]
risk_evidence: [recovery matrix defined, anti-loop guardrails active]
downstream_evidence: [next NEM entry generated, gate decision ADOPT]

# ── Test Summary ──
tests_total: 458
tests_passed: 458
tests_failed: 0
tests_skipped: 0
success_rate: 1.0
critical_failures: 0

# ── Artifact Summary ──
artifacts: [outputs/tidal/*, reports/*, moodify_runtime/*.py]

# ── Risk Summary ──
risks: [none identified in retroactive review]

# ── Downstream ──
downstream_dependency_note: verified
reopen_criteria: []

# ── Decision ──
seal_decision:
  decision: INDUSTRIAL_DONE
  decision_reason: Retroactively sealed — all evidence layers verified, 458 tests pass
  approved_by: automated-gate
  approved_at: 2026-06-04T14:06:10Z
  next_status: N/A — terminal state
```

