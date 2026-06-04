# MHP-471: Tidal Core Bottleneck Brief

**Status**: completed
**Date**: 2026-06-04
**Chain**: ECHAIN-MOODIFY-TIDAL-CORE-008 / NEM-MOODIFY-TIDAL-CORE-PROBE-024
**Plan-6**: Probe Plan-6A: Boundary / P5 (Systemization)
**Depends on**: MHP-470 (Tidal Queue Intake Audit)

## 1. Purpose

Identify and rank the bottlenecks that limit tidal cycle throughput, reliability, and operator visibility. Each bottleneck is assessed for impact, root cause, and proposed resolution path within the E-Chain structure.

## 2. Bottleneck Ranking

### B1: No Task Outcome Tracking (P0 — Build Blocker)

| Field | Detail |
|-------|--------|
| Impact | `tasks_processed` always 0 — heartbeat, records, and reports are blind to actual work done |
| Root cause | `phase_run()` shells out to CLI but never parses stdout to extract task counts |
| Symptoms | Heartbeat shows cycle=2, tasks=0 despite 9 completed tasks in queue |
| Resolution | Parse CLI `run` output or query queue status after run; update `TideRecord` counters |
| MHP target | MHP-485 (Tidal State Machine) — embed counter update in run phase exit |

### B2: No Gate Phase Implementation (P0 — Quality Blocker)

| Field | Detail |
|-------|--------|
| Impact | All task outputs are accepted regardless of quality; no MRS scoring feedback loop |
| Root cause | Gate phase is in the vocabulary but not in `tidal_cycle.py` code |
| Symptoms | Degraded outputs would flow into reports and craft memory unnoticed |
| Resolution | Implement `phase_gate()` calling MRS scoring; add `gate_approve/reprocess/reject` counters |
| MHP target | MHP-489 (Tidal Safety Cutoff Engine) — embed quality gate logic |

### B3: Subprocess Architecture (P0 — Reliability Blocker)

| Field | Detail |
|-------|--------|
| Impact | Every phase shells out to `python3 -m moodify_runtime.cli` — slow, fragile, no shared state |
| Root cause | Phases are subprocess wrappers around CLI commands |
| Symptoms | ~200ms+ overhead per phase just for Python import; no in-process state sharing |
| Resolution | Convert phases to direct function calls where possible; keep subprocess only for `run` (which needs isolation) |
| MHP target | MHP-485 (Tidal State Machine) — refactor phase execution to call modules directly |

### B4: No Pause/Resume (P1 — Operations Blocker)

| Field | Detail |
|-------|--------|
| Impact | Operator cannot pause a running cycle; must SIGTERM the engine |
| Root cause | `TidalEngine._running` is binary; no intermediate state |
| Symptoms | Changing config requires full engine restart |
| Resolution | Add `PAUSED` engine state with SIGUSR1 handler; resume on SIGUSR2 or timer |
| MHP target | MHP-475 (Pause Resume Probe) and MHP-485 (State Machine) |

### B5: Night Worker / Tidal Cycle Schism (P1 — Architecture)

| Field | Detail |
|-------|--------|
| Impact | Two overlapping unattended systems: `tidal_cycle.py` and `workers/night_worker.py` |
| Root cause | Independent development; night worker predates E-Chain framework |
| Symptoms | Night worker has checkpoint/resume, parameter sweeps, scoring — tidal cycle has none |
| Resolution | Decision needed: absorb night worker into tidal cycle, or define clear coordination contract |
| MHP target | MHP-473 (Tidal Phase Probe) — evaluate integration options |

### B6: JSONL-File State Management (P1 — Data Integrity)

| Field | Detail |
|-------|--------|
| Impact | All state (registry, queue, events, records) in JSONL files with no indexing |
| Root cause | Simplicity-first design; JSONL was chosen for human readability |
| Symptoms | `existing_task_keys()` scans entire queue file; linear degradation as queue grows |
| Resolution | Add in-memory index for active tasks; periodic compaction of done/failed entries |
| MHP target | MHP-487 (Tidal Intake Queue Model) — implement indexed queue access |

### B7: No External Monitoring Surface (P2 — Observability)

| Field | Detail |
|-------|--------|
| Impact | Operator must SSH into the machine to check tidal status |
| Root cause | Heartbeat is a local JSON file; no HTTP endpoint or cloud ping |
| Symptoms | No alerting for engine crash or health degradation |
| Resolution | Add a lightweight HTTP status endpoint; periodic cloud health ping |
| MHP target | MHP-492 (Tidal Runtime API) — expose status endpoint |

### B8: Fixed Sleep Interval (P2 — Scheduling)

| Field | Detail |
|-------|--------|
| Impact | Sleep is `max(0, interval - elapsed)` — no time-of-day awareness |
| Root cause | `TidalEngine.__init__` takes a single `interval` parameter |
| Symptoms | Can't configure "run more often during day, less at night" or "pause during peak hours" |
| Resolution | Add mode-aware scheduling: different intervals for DAY/NIGHT/MANUAL modes |
| MHP target | MHP-493 (Tidal Mode Profiles) — implement mode switching |

### B9: No Cycle-Level Checkpoint (P2 — Resilience)

| Field | Detail |
|-------|--------|
| Impact | If engine crashes mid-cycle, next start begins fresh — no mid-cycle resume |
| Root cause | Cycle state is only in memory; written to records only at cycle end |
| Symptoms | Crash during run phase → all pending tasks must be re-planned |
| Resolution | Write cycle checkpoint at each phase boundary; resume from last checkpoint on restart |
| MHP target | MHP-499 (Pause Resume Validation) — validate checkpoint/resume cycle |

## 3. Bottleneck Dependency Map

```
B3 (Subprocess) ──► B1 (No Task Counters) ──► B2 (No Gate)
                                                     │
B5 (Night Worker Schism) ──► B6 (JSONL State) ──────┤
                                                     │
B4 (No Pause/Resume) ────► B9 (No Checkpoint) ──────┤
                                                     ▼
                                              Build NEM Ready
                                                     │
B7 (No Monitoring) ───► B8 (Fixed Sleep) ────────────┤
                                                     ▼
                                              System NEM Ready
```

## 4. Throughput Projection

| Scenario | Current | After Build NEM |
|----------|---------|-----------------|
| Cycle overhead (subprocess) | ~2s per phase | ~0.1s per phase (direct calls) |
| Tasks per cycle (current hardware) | 9 (3 samples × 3 presets) | 50-100 (with priority queue) |
| Tasks per 12h night | ~27 (3 cycles × 9) | ~300-600 (6 cycles × 50-100) |
| Operator awareness | SSH + manual inspection | HTTP API + morning brief |
| Crash recovery | Manual restart | Auto-restart with checkpoint |
| Quality gating | None | MRS scoring with approve/reprocess/reject |

## 5. Recommendation

**Sequence**: Fix B3 (subprocess) and B1 (counters) first — they unblock everything else. Then B2 (gate) and B4 (pause/resume) in parallel. Address B5 (night worker) as a design decision before Build NEM starts, since it affects the intake queue architecture.
