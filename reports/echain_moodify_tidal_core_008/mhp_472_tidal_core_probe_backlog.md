# MHP-472: Tidal Core Probe Backlog

**Status**: completed
**Date**: 2026-06-04
**Chain**: ECHAIN-MOODIFY-TIDAL-CORE-008 / NEM-MOODIFY-TIDAL-CORE-PROBE-024
**Plan-6**: Probe Plan-6A: Boundary / P6 (Next Entry)
**Depends on**: MHP-471 (Tidal Core Bottleneck Brief)

## 1. Purpose

Catalog the remaining probe experiments needed before Gate 1 (Probe → Build decision). This backlog defines the scope of Probe Plan-6B (Technical Probe, MHP-473 to MHP-478) and Probe Plan-6C (Feasibility Gate, MHP-479 to MHP-484).

## 2. Completed (Plan-6A: Boundary)

| MHP | Title | Status | Artifact |
|-----|-------|--------|----------|
| 467 | Tidal Current State Map | ✅ | `reports/echain_moodify_tidal_core_008/mhp_467_tidal_current_state_map.md` |
| 468 | Tidal Lifecycle Vocabulary | ✅ | `reports/echain_moodify_tidal_core_008/mhp_468_tidal_lifecycle_vocabulary.md` |
| 469 | Tidal Safety Risk Taxonomy | ✅ | `reports/echain_moodify_tidal_core_008/mhp_469_tidal_safety_risk_taxonomy.md` |
| 470 | Tidal Queue Intake Audit | ✅ | `reports/echain_moodify_tidal_core_008/mhp_470_tidal_queue_intake_audit.md` |
| 471 | Tidal Core Bottleneck Brief | ✅ | `docs/spec/tidal_core_bottleneck_brief.md` |
| 472 | Tidal Core Probe Backlog | ✅ | (this document) |

## 3. Pending (Plan-6B: Technical Probe)

### MHP-473: Tidal Phase Probe
- **Type**: Execution
- **Goal**: Run the engine in instrumented mode; measure per-phase latency, subprocess overhead, and phase failure rates
- **Method**: Add timing instrumentation to `tidal_cycle.py`; run 3 cycles with `--interval 60`; collect per-phase histograms
- **Key question**: Is subprocess overhead (>200ms/phase) the dominant latency, or is it audio processing?

### MHP-474: Sleep Mode Probe
- **Type**: Execution
- **Goal**: Validate that the sleep phase doesn't drift, leak resources, or miss wake signals
- **Method**: Run engine with `--interval 120` for 5 cycles; measure actual sleep durations vs planned; check memory/RSS after each sleep
- **Key question**: Does memory grow across sleep cycles (indicating a leak)?

### MHP-475: Pause Resume Probe
- **Type**: Validation
- **Goal**: Determine the minimum viable pause/resume mechanism
- **Method**: Implement SIGUSR1 pause handler; test pause during each phase; verify event stream integrity after resume
- **Key question**: Can we safely pause mid-cycle without corrupting queue state?

### MHP-476: Heartbeat Integrity Probe
- **Type**: Validation
- **Goal**: Verify heartbeat is written reliably under load, during sleep, and across process suspension
- **Method**: Run `tidal_status.sh` in a loop while engine runs; check for heartbeat gaps > 30s; simulate `SIGSTOP`/`SIGCONT`
- **Key question**: Does the heartbeat survive process suspension?

### MHP-477: Cycle Boundary Probe
- **Type**: Systemization
- **Goal**: Test edge cases at cycle boundaries: zero tasks, all tasks failed, phase timeout, concurrent shutdown
- **Method**: Create test scenarios: empty input dir, broken audio files, 1s timeout; observe engine behavior at each boundary
- **Key question**: Does the engine handle all boundary conditions gracefully?

### MHP-478: Tidal Core Probe Report
- **Type**: Next Entry
- **Goal**: Synthesize all probe findings into a single decision document for Gate 1
- **Method**: Aggregate MHP-473 through MHP-477 findings; score each against Gate 1 criteria; recommend ADOPT/HOLD/DROP
- **Key question**: Is the tidal core ready for Build NEM investment, or are more probes needed?

## 4. Pending (Plan-6C: Feasibility Gate)

### MHP-479: Tidal Core SLO Definition
- **Type**: Execution
- **Goal**: Define Service Level Objectives for the tidal core: cycle completion rate, task success rate, heartbeat freshness, crash recovery time
- **Output**: `docs/spec/tidal_core_slo.md`

### MHP-480: Mini Tidal Cycle Run
- **Type**: Execution
- **Goal**: Run a 2-hour unattended tidal cycle session with real audio processing; collect evidence for Gate 1
- **Output**: `reports/echain_moodify_tidal_core_008/mhp_480_mini_tidal_cycle_run.md`

### MHP-481: Cycle Recovery Matrix
- **Type**: Validation
- **Goal**: Test recovery from each failure mode identified in MHP-469; document recovery success rate
- **Output**: `reports/echain_moodify_tidal_core_008/mhp_481_cycle_recovery_matrix.md`

### MHP-482: Gate 1 Evidence Package
- **Type**: Validation
- **Goal**: Assemble all probe evidence into a structured Gate 1 package for the ADOPT/HOLD/DROP decision
- **Output**: `reports/echain_moodify_tidal_core_008/mhp_482_gate1_evidence_package.md`

### MHP-483: Tidal Core Probe Decision
- **Type**: Systemization
- **Goal**: Make the Gate 1 decision: ADOPT (proceed to Build NEM), HOLD (more probes needed), or DROP (not viable)
- **Output**: `reports/echain_moodify_tidal_core_008/mhp_483_tidal_core_probe_decision.md`

### MHP-484: Tidal Core Build Entry
- **Type**: Next Entry
- **Goal**: If ADOPT, create the Build NEM entry document with scoped MHPs and resource estimates
- **Output**: `docs/nem/NEM-MOODIFY-TIDAL-CORE-BUILD-025.md` (update from PLANNED to ACTIVE)

## 5. Probe Experiment Schedule

| Batch | MHPs | Estimated Effort | Dependencies |
|-------|------|-----------------|--------------|
| Plan-6B Technical Probe | 473-478 | 6 experiments, ~4h wall clock | None (can run in parallel) |
| Plan-6C Feasibility Gate | 479-484 | 1 SLO + 1 run + 1 matrix + 3 synthesis | Plan-6B complete |

## 6. Gate 1 Decision Criteria

| Criterion | ADOPT Threshold | Evidence Source |
|-----------|----------------|-----------------|
| Cycle stability | ≥95% cycles complete without error | MHP-473, MHP-480 |
| Sleep integrity | No memory leak across 5+ cycles | MHP-474 |
| Pause safety | No queue corruption after pause/resume | MHP-475 |
| Heartbeat reliability | No gaps > 30s during normal operation | MHP-476 |
| Boundary handling | Graceful behavior on all edge cases | MHP-477 |
| Recovery rate | ≥80% of failure modes recoverable | MHP-481 |
| SLO achievability | Defined SLOs are feasible on current hardware | MHP-479 |

## 7. Probe NEM Completion Checklist

- [x] Plan-6A Boundary (MHP-467 to MHP-472) — **COMPLETE**
- [ ] Plan-6B Technical Probe (MHP-473 to MHP-478)
- [ ] Plan-6C Feasibility Gate (MHP-479 to MHP-484)
- [ ] Gate 1 Decision: ADOPT / HOLD / DROP
