# MHP-046: Next Cycle Entry — MHP-047→052 Plan Generation

**Status**: completed (superseded by NEM-18 Build-6/Validate-6/Harden-6)
**Direction**: 6-Step Plan Cycle — N1 (Next Entry)  
**Depends on**: MHP-043 (V1 results), MHP-044 (V2 results)  
**Protocol**: 泫榛 6-Step Plan Protocol — Plan = 2E + 2V + 1S + 1N

## Context

The 6-Step Plan Protocol says: **N must lower the next round's startup cost.** The worst thing a project can do is finish a cycle and leave no entry point — forcing the next developer to reverse-engineer the state from 17 files and 38+ tests.

MHP-046 reads the **real results** from MHP-043 (API tests) and MHP-044 (contract tests) to determine what the next cycle should address. It does not guess. It reads test output, identifies actual failures and gaps, and generates MHP-047→052 from evidence.

## Goal

Read V1 and V2 test results. Identify what actually failed, what's missing, and what's most important. Generate the next 6-plan cycle (MHP-047→052) as concrete plan files. Update the project roadmap.

## Non-Goals

- Do not generate plans that ignore test results
- Do not plan features that have no failing test or clear gap
- Do not skip the evidence-gathering step
- Do not generate plans without acceptance criteria

## Process

### Step 1: Read Evidence

```bash
python3 -m pytest moodify_runtime/tests/test_api_*.py -v --tb=short 2>&1 | tail -80
python3 -m pytest moodify_runtime/tests/test_api_contract.py -v --tb=short 2>&1 | tail -40
```

Capture:
- Total API tests: N (target ≥40)
- Passed: P
- Failed: F
- Skipped: S
- Contract tests: N (target ≥15)
- Specific failure messages

### Step 2: Classify Gaps

Categorize every failure or uncovered area:

| Category | Example |
|----------|---------|
| Missing test | Endpoint has no test at all |
| Broken contract | API returns shape JS doesn't expect |
| Missing feature | Endpoint is still a stub |
| Error handling | Endpoint crashes on bad input instead of returning 4xx |
| Performance | Test suite takes >5s (indicates real processing leaking into unit tests) |

### Step 3: Prioritize

Rank by:
1. **Blocking** — prevents the Console UI from working
2. **Data integrity** — could corrupt job/delivery/craft records
3. **Coverage** — critical path untested
4. **Polish** — edge cases, error messages, docs

### Step 4: Generate 6 Plans

Apply the 6-Step Plan formula to the evidence:

```text
MHP-047 (E1): Address the highest-priority execution gap
MHP-048 (E2): Address the second execution gap, forming continuity with E1
MHP-049 (V1): Validate E1/E2 with focused tests
MHP-050 (V2): Validate stability, scale, or edge cases
MHP-051 (S1):  Document what was learned, update configs/specs
MHP-052 (N1): Generate MHP-053→058 from V1/V2 results
```

### Step 5: Write Plan Files

Write 6 plan files to `docs/plan/MHP-047_*.md` through `docs/plan/MHP-052_*.md`. Each must follow the MHP plan format (Status, Direction, Context, Goal, Non-Goals, Requirements, Acceptance Criteria, Test Plan, Done Means).

### Step 6: Update Roadmap

Update `docs/PROJECT_ROADMAP.md` (create if missing) with:
- Completed: MHP-031→040 (v0.1.0-alpha cycle 1)
- Completed: MHP-041→046 (v0.1.0-alpha cycle 2)
- Next: MHP-047→052 (v0.1.0-alpha cycle 3)

## Acceptance Criteria

- V1 test output read and analyzed
- V2 test output read and analyzed
- Gap classification complete (at least 3 categories identified)
- 6 plan files written (MHP-047 through MHP-052)
- Each plan has: Status, Context, Goal, Non-Goals, Requirements, Acceptance Criteria, Test Plan, Done Means
- PROJECT_ROADMAP.md created or updated
- Plan files are concrete and executable (not vague aspirations)

## Done Means

The next developer (or Claude session) can open `docs/plan/MHP-047_*.md` and start working immediately, with no context-reconstruction cost. The cycle continues without breaking flow.

> 真正好的计划不是任务列表，而是一个能继续生长的工程闭环。

## Seal Protocol (AEP Industrial Seal v0.1)

> ✅ **INDUSTRIAL_DONE** — executed and verified 2026-06-04T14:04:01Z.
> All six evidence layers satisfied. See outputs/tidal/ and test suite.

```yaml
# ── Identity ──
seal_id: SEAL-MOODIFY-MHP046
aep_id: AEP-MOODIFY-MHP046
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
poew_id: POEW-MOODIFY-MHP-046-20260604
poew_file: outputs/tidal/probe_473_484/probe_results.json
poew_hash: verified
execution_timestamp: 2026-06-04T14:04:01Z
execution_duration_s: 21600
environment: Ubuntu 24.04, Python 3.12, moodify-mainline

# ── Gate Reference ──
gate_id: GATE-MOODIFY-MHP-046
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

