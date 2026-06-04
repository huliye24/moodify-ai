# MHP-468: Tidal Lifecycle Vocabulary

**Status**: completed
**Date**: 2026-06-04
**Chain**: ECHAIN-MOODIFY-TIDAL-CORE-008 / NEM-MOODIFY-TIDAL-CORE-PROBE-024
**Plan-6**: Probe Plan-6A: Boundary / P2 (Execution)
**Depends on**: MHP-467 (Tidal Current State Map)

## 1. Purpose

This document defines the canonical vocabulary for the Tidal Core system. Every downstream artifact — state machine spec, event schema, heartbeat contract, CLI commands, operator runbook — uses these terms with the exact meanings defined here.

## 2. Cycle Lifecycle States

A tidal cycle is the fundamental unit of work. It progresses through a fixed sequence of phases.

### 2.1 Phase Enumeration

| State | Canonical Name | Description | Entry Condition | Exit Condition |
|-------|---------------|-------------|-----------------|----------------|
| 0 | `INIT` | Engine started, pre-flight checks running | Engine process launch | Health check passed |
| 1 | `REGISTER` | Scanning input directories, registering new audio | Health OK | Registration complete (success or fail) |
| 2 | `PLAN` | Generating task queue from registry × presets | Registration phase ended | Queue planning complete |
| 3 | `RUN` | Executing pending tasks under supervisor | Queue non-empty or dry-run | All tasks done, or limit reached |
| 4 | `GATE` | Running quality gates on run outputs | Run phase ended | Gates evaluated (approve/reprocess/reject) |
| 5 | `REPORT` | Generating daily report from run evidence | Gate phase ended | Report written to disk |
| 6 | `CRAFT` | Writing craft memory seeds from run results | Report phase ended | Craft records written |
| 7 | `SLEEP` | Idle period between cycles | Craft phase ended | Interval elapsed or wake signal |
| 8 | `SHUTDOWN` | Graceful termination | SIGTERM/SIGINT received, or max cycles reached | Process exit |
| 9 | `ERROR` | Unhandled exception during cycle | Exception in any phase | Error recorded, next cycle starts or engine stops |

### 2.2 State Transition Diagram

```
                    ┌──────────────────────────────────────────┐
                    │              (any phase)                  │
                    │                  │                        │
                    │            unhandled error                │
                    │                  ▼                        │
                    │              ERROR ───► (log + recover)   │
                    │                  │                        │
                    │           (if recoverable)                │
                    │                  ▼                        │
                    │              SLEEP or next cycle          │
                    └──────────────────────────────────────────┘

INIT ──► REGISTER ──► PLAN ──► RUN ──► GATE ──► REPORT ──► CRAFT ──► SLEEP
  │                                                                       │
  │        ◄───────────────────────────────────────────────────────────────┤
  │                              (next cycle)                              │
  │                                                                       │
  └──► SHUTDOWN (SIGTERM / SIGINT / max_cycles)                           │
```

### 2.3 Phase Entry/Exit Rules

| Rule | Description |
|------|-------------|
| R1 | Every phase transition emits a `PHASE_ENTER` and `PHASE_EXIT` event |
| R2 | `REGISTER` must precede `PLAN` (planning needs current registry) |
| R3 | `PLAN` must precede `RUN` (running needs a queue) |
| R4 | `GATE` is optional — if no tasks ran, skip to `REPORT` |
| R5 | `SLEEP` must check health before transitioning to `REGISTER` |
| R6 | `SHUTDOWN` can interrupt `SLEEP` but must not interrupt `RUN` |
| R7 | `ERROR` always transitions to `SLEEP` (preserve rhythm) or `SHUTDOWN` (if fatal) |

## 3. Engine States

Above the cycle level, the engine itself has states.

| State | Canonical Name | Description |
|-------|---------------|-------------|
| `ENGINE_STARTING` | Engine initializing, PID written, signals registered |
| `ENGINE_RUNNING` | Cycle loop active, health checks passing |
| `ENGINE_PAUSED` | Health check failed or explicit pause — sleeping, will retry |
| `ENGINE_STOPPING` | Shutdown signal received, waiting for current phase to complete |
| `ENGINE_STOPPED` | Process exiting, PID file removed |
| `ENGINE_CRASHED` | Unrecoverable error, engine cannot continue |

### 3.1 Engine State Transitions

```
ENGINE_STARTING ──► ENGINE_RUNNING
ENGINE_RUNNING ──► ENGINE_PAUSED (health fail)
ENGINE_RUNNING ──► ENGINE_STOPPING (signal)
ENGINE_PAUSED ──► ENGINE_RUNNING (health restored)
ENGINE_PAUSED ──► ENGINE_STOPPING (signal during pause)
ENGINE_STOPPING ──► ENGINE_STOPPED
ENGINE_RUNNING ──► ENGINE_CRASHED (unrecoverable)
```

## 4. Event Vocabulary

Every significant occurrence in the tidal system is emitted as a structured event with a canonical `event_type`.

### 4.1 Engine-Level Events

| Event Type | Severity | Description | Required Fields |
|-----------|----------|-------------|-----------------|
| `ENGINE_START` | INFO | Engine process began | `interval_s`, `max_cycles`, `pid` |
| `ENGINE_STOP` | INFO | Engine process ending | `cycles_completed`, `total_tasks`, `elapsed_s` |
| `ENGINE_PAUSE` | WARN | Engine paused (health/operator) | `reason`, `pause_duration_s` |
| `ENGINE_RESUME` | INFO | Engine resumed after pause | `pause_duration_s` |
| `ENGINE_CRASH` | ERROR | Engine encountered fatal error | `exception_type`, `exception_message` |

### 4.2 Cycle-Level Events

| Event Type | Severity | Description | Required Fields |
|-----------|----------|-------------|-----------------|
| `CYCLE_START` | INFO | New cycle beginning | `cycle_number`, `cycle_id` |
| `CYCLE_END` | INFO | Cycle completed normally | `cycle_number`, `tasks_processed`, `tasks_succeeded`, `tasks_failed`, `elapsed_s` |
| `CYCLE_ERROR` | ERROR | Cycle terminated abnormally | `cycle_number`, `exception_type`, `exception_message` |

### 4.3 Phase-Level Events

| Event Type | Severity | Description | Required Fields |
|-----------|----------|-------------|-----------------|
| `PHASE_ENTER` | DEBUG | Entering a phase | `phase`, `cycle_number` |
| `PHASE_EXIT` | DEBUG | Exiting a phase | `phase`, `cycle_number`, `ok`, `elapsed_ms` |
| `PHASE_ERROR` | WARN | Phase completed with errors | `phase`, `cycle_number`, `error_message` |

### 4.4 Operational Events

| Event Type | Severity | Description | Required Fields |
|-----------|----------|-------------|-----------------|
| `HEALTH_CHECK` | DEBUG | Health check result | `disk_free_gb`, `mem_free_gb`, `passed` |
| `HEALTH_FAIL` | WARN | Health check failed | `disk_free_gb`, `mem_free_gb`, `reason` |
| `TASK_START` | DEBUG | Individual task began | `task_id`, `sample_id`, `preset` |
| `TASK_END` | DEBUG | Individual task finished | `task_id`, `ok`, `elapsed_s` |
| `TASK_FAIL` | WARN | Individual task failed | `task_id`, `error`, `attempt` |
| `SHUTDOWN` | INFO | Shutdown signal received | `signal` |
| `SLEEP` | DEBUG | Entering sleep phase | `duration_s`, `wake_at` |
| `WAKE` | DEBUG | Exiting sleep phase | `slept_s` |

## 5. Task States

Tasks flow through the queue with their own lifecycle, observed by the tidal engine.

| State | Canonical Name | Description |
|-------|---------------|-------------|
| `TASK_PENDING` | Created, waiting to run |
| `TASK_RUNNING` | Currently executing under supervisor |
| `TASK_DONE` | Completed successfully |
| `TASK_FAILED` | Failed all retry attempts |
| `TASK_TIMED_OUT` | Exceeded timeout without completing |
| `TASK_SKIPPED` | Skipped by gate or operator decision |

### 5.1 Task State Transitions

```
TASK_PENDING ──► TASK_RUNNING ──► TASK_DONE
                            ├──► TASK_FAILED
                            └──► TASK_TIMED_OUT
TASK_PENDING ──► TASK_SKIPPED
```

## 6. Gate Decision Vocabulary

After `RUN`, each task output passes through quality gates. The gate vocabulary is shared with the MRS and Craft systems.

| Decision | Meaning | Action |
|----------|---------|--------|
| `APPROVE` | Output meets quality bar | Record as success, include in report |
| `REPROCESS` | Output needs rework | Re-queue with different parameters |
| `REJECT` | Output is unusable | Record as failure, log reason |
| `HOLD` | Human review needed | Pause, flag for operator |

## 7. Operational Modes

The tidal engine can run in different modes, selectable at startup or switchable at runtime.

| Mode | Description | Typical Interval | Use Case |
|------|-------------|-----------------|----------|
| `DAY` | Light processing, frequent cycles | 3600s (1h) | Daytime background work |
| `NIGHT` | Heavy processing, long cycles | 7200s (2h) | Overnight batch work |
| `MANUAL` | Single cycle, no sleep | N/A | Operator-triggered run |
| `WATCH` | No processing, monitor only | 300s (5min) | Observation/debug |
| `BOOTSTRAP` | First-run initialization | N/A | System setup |

## 8. Integration Vocabulary

Terms used across system boundaries.

| Term | Definition | Owner Module |
|------|-----------|-------------|
| `tide` | One complete cycle (REGISTER → SLEEP) | Tidal Core |
| `ebb` | The active work portion of a tide (REGISTER → CRAFT) | Tidal Core |
| `flow` | The sleep/idle portion of a tide | Tidal Core |
| `flood` | A period of sustained high activity across multiple tides | Tidal Operations |
| `neap` | A period of low activity (maintenance, observation) | Tidal Operations |
| `moon` | A 24-hour collection of tides, the natural reporting boundary | Tidal Operations |
| `strand` | A task that failed repeatedly and was set aside | Tidal Intelligence |
| `wake` | The morning review moment when the operator inspects overnight results | Tidal Operations |

## 9. Naming Conventions

### 9.1 Identifiers

| Entity | Pattern | Example |
|--------|---------|---------|
| Cycle ID | `TIDE_{YYYY-MM-DD}_{HH-MM-SS}` | `TIDE_2026-06-04_22-15-00` |
| Moon ID | `MOON_{YYYY-MM-DD}` | `MOON_2026-06-04` |
| Strand ID | `STRAND_{sample_id}_{preset}` | `STRAND_SMP_16B0_warm_vocal` |

### 9.2 File Paths

| Artifact | Path Pattern |
|----------|-------------|
| Events | `outputs/tidal/tidal_events.jsonl` |
| Heartbeat | `outputs/tidal/tidal_heartbeat.json` |
| Records | `outputs/tidal/tidal_records.jsonl` |
| PID | `outputs/tidal/tidal.pid` |
| Cycle report | `reports/tidal/moon_{date}/cycle_{num}_report.md` |

## 10. Validation Rules

These rules are checked by the state machine and event validator.

| Rule | Check |
|------|-------|
| V1 | `CYCLE_START` must be preceded by `CYCLE_END` or `ENGINE_START` |
| V2 | `PHASE_ENTER.phase` must match the expected next phase in sequence |
| V3 | `PHASE_EXIT.phase` must match the current `PHASE_ENTER.phase` |
| V4 | No `CYCLE_START` during `ENGINE_PAUSED` |
| V5 | Heartbeat `cycle` must be monotonic (never decrease) |
| V6 | `SLEEP` duration must not exceed `interval * 1.5` |
| V7 | Every `CYCLE_START` must have a corresponding `CYCLE_END` or `CYCLE_ERROR` |
