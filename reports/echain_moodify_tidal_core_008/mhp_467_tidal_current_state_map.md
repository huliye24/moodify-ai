# MHP-467: Tidal Current State Map

**Status**: completed
**Date**: 2026-06-04
**Chain**: ECHAIN-MOODIFY-TIDAL-CORE-008 / NEM-MOODIFY-TIDAL-CORE-PROBE-024
**Plan-6**: Probe Plan-6A: Boundary / P1 (Execution)

## 1. Executive Summary

The tidal cycle is a **working background loop** (`moodify_runtime/tidal_cycle.py`) that runs the Moodify processing pipeline unattended: register → plan → run → report → craft → sleep → repeat. It has completed 2 real cycles (2026-06-04), shell scripts for start/stop/status exist, and structured events + heartbeat are emitted. However, it lacks a formal state machine, pause/resume semantics, intelligent scheduling, and integration with the parallel night worker system. This report maps the current state, identifies gaps, and sets the baseline for the Tidal Core E-Chain.

## 2. Architecture Map

### 2.1 Component Inventory

| Component | Path | Role | Maturity |
|-----------|------|------|----------|
| TidalEngine | `moodify_runtime/tidal_cycle.py` | Main loop engine | alpha — runs, not hardened |
| TideRecord | `moodify_runtime/tidal_cycle.py` | Cycle-level dataclass | basic — fields defined, no validation |
| tidal_start.sh | `scripts/tidal_start.sh` | Background launcher | operational |
| tidal_stop.sh | `scripts/tidal_stop.sh` | Graceful shutdown (SIGTERM→SIGKILL) | operational |
| tidal_status.sh | `scripts/tidal_status.sh` | Heartbeat + event reader | operational |
| NightWorker | `workers/night_worker.py` | Separate overnight batch engine | beta — has checkpoint/resume |
| night_jobs.yaml | `configs/night_jobs.yaml` | Night worker config | operational |
| Supervisor | `moodify_runtime/supervisor.py` | Subprocess crash+retry wrapper | probe-level |
| Queue | `moodify_runtime/queue.py` | Task planning from registry | operational |
| Registry | `moodify_runtime/registry.py` | Audio sample registration | operational |

### 2.2 Data Flow

```
tidal_input/*.wav
    │
    ▼
[register] ──► tidal_registry.jsonl
    │
    ▼
[plan] ──► tidal_queue.jsonl (sample × preset combinations)
    │
    ▼
[run] ──► supervisor.py ──► cli.py run ──► outputs/{run_id}/
    │
    ▼
[report] ──► reports/daily_report_tidal.md
    │
    ▼
[craft] ──► data/tidal_craft/craft_memory_seed_tidal.md
    │
    ▼
[sleep] ──► tidal_heartbeat.json (every 10s during sleep)
    │
    └──► tidal_events.jsonl (all phases)
    └──► tidal_records.jsonl (per-cycle summary)
    └──► tidal.pid (process ID)
```

### 2.3 Phase Table

| Phase | Method | CLI Command | Timeout | Retry | Blocks on Failure? |
|-------|--------|-------------|---------|-------|--------------------|
| register | `phase_register()` | `cli register --source tidal_cycle` | 600s | No | No |
| plan | `phase_plan()` | `cli plan [--presets ...]` | 600s | No | No |
| run | `phase_run()` | `cli run [--limit N]` via supervisor | 3600s | 1 retry | No (records error) |
| report | `phase_report()` | `cli report` | 600s | No | No |
| craft | `phase_craft()` | `cli craft` | 600s | No | No |
| sleep | (internal timer) | N/A | N/A | N/A | N/A |

## 3. Current State Assessment

### 3.1 What Works

1. **Loop mechanics**: The engine starts, runs cycles, sleeps, and repeats. Shutdown via SIGTERM/SIGINT works.
2. **Structured events**: All phase transitions emit JSONL events with timestamps, cycle numbers, and metadata.
3. **Heartbeat**: Written every cycle end + every 10s during sleep. Contains PID, cycle count, disk/memory.
4. **Health checks**: Pre-cycle disk (3GB threshold) and memory (0.5GB threshold) checks with 5min pause on failure.
5. **Operational scripts**: Start (with nohup), stop (graceful then force), status (heartbeat + last 5 events).
6. **Crash resilience**: Top-level try/except in `_run_one_cycle()` ensures a single cycle crash doesn't kill the engine.
7. **Signal handling**: SIGTERM and SIGINT trigger graceful shutdown at sleep boundaries.

### 3.2 What's Missing / Gaps

#### G1: No Formal State Machine
The engine uses a string `phase` field (`"init" → "register" → "plan" → "run" → "report" → "craft" → "sleep"`) but there is no state machine with defined transitions, guards, or invariants. The `TideRecord.phase` is set imperatively — no validation that phases execute in order.

#### G2: No Pause/Resume
The only lifecycle operations are start and stop. There is no way to pause a running cycle, inspect its state, and resume. The `_running` flag is binary.

#### G3: Task Counters Are Stale
`TideRecord.tasks_processed`, `tasks_succeeded`, `tasks_failed` are fields on the dataclass but are never populated from actual run results. The `phase_run()` method does not parse the CLI output to extract task counts; `self._total_tasks` etc. are initialized to 0 and never updated.

#### G4: No Mid-Cycle Operator Surface
There is no CLI/API command to query the current cycle's phase, progress, or errors while the engine runs. The status script reads the heartbeat file, which only updates at cycle boundaries and every 10s during sleep.

#### G5: Night Worker Not Integrated
`tidal_cycle.py` and `workers/night_worker.py` are two separate unattended runtime systems with overlapping concerns (batch processing, reporting). The night worker has richer features (checkpoint/resume, parameter sweeps, scoring) but is not called by the tidal cycle. The tidal cycle delegates to `cli.py run`, which is a different execution path.

#### G6: No Cycle Configuration Profiles
The engine accepts `--interval`, `--max-cycles`, `--task-limit`, `--presets` as CLI args but has no concept of named configuration profiles (e.g., "daytime" vs "overnight" with different intervals/task limits).

#### G7: Phase Failures Don't Gate Subsequent Phases
If `register` or `plan` fails, the engine still proceeds to `run`. If `run` fails, `report` and `craft` still execute. There is no per-phase gate logic.

#### G8: No External Monitoring Integration
The heartbeat is a local JSON file. There is no HTTP endpoint, cloud ping, or structured log shipping. External monitoring requires SSH access to the machine.

#### G9: No Lease/Coordination Model
The PID file prevents duplicate local instances, but there is no distributed lease mechanism for multi-machine or cloud-worker coordination.

#### G10: Sleep Is a Dumb Timer
The sleep phase is `max(0, interval - elapsed)` — it doesn't account for time-of-day, external schedules, or adaptive pacing.

### 3.3 Safety Risks

| Risk | Severity | Description |
|------|----------|-------------|
| R1: Silent task counter drift | Medium | `tasks_processed` always 0 — operators can't tell if work was done from heartbeat alone |
| R2: Unbounded error accumulation | Low | `record.errors` list grows without limit; no max-error cap per cycle |
| R3: No circuit breaker | Medium | Repeated phase failures don't trigger engine pause (only disk/mem health does) |
| R4: Health check is coarse | Low | Only checks disk < 3GB and mem < 0.5GB; doesn't check CPU, I/O, or process count |
| R5: Single-cycle crash recovery is best-effort | Medium | The try/except catches unhandled exceptions but the engine may continue with corrupted state |

## 4. Boundary Analysis

### 4.1 What the Tidal Cycle Owns
- The loop orchestration (phase ordering, sleep timing)
- The event stream and heartbeat
- Process lifecycle (PID, signals)
- Health gating (disk/memory checks)

### 4.2 What the Tidal Cycle Delegates
- **Task execution** → `supervisor.py` → `cli.py run`
- **Audio registration** → `cli.py register`
- **Queue planning** → `queue.py` → `registry.py`
- **Report generation** → `cli.py report` → `report.py`
- **Craft memory** → `cli.py craft` → `craft_memory.py`
- **Audio processing** → `moodify-core-package/src/moodify/`

### 4.3 What the Tidal Cycle Should Own But Doesn't Yet
- **Pause/resume** — currently only stop
- **Task outcome tracking** — currently delegated to CLI stdout, not parsed
- **Cycle-aware scheduling** — currently a fixed interval timer
- **Operator query interface** — currently only file-based heartbeat

### 4.4 What Should Stay Outside
- **Parameter sweeps and scoring** — belongs to the night worker or craft library
- **MRS calibration** — separate system
- **Cloud scheduling** — separate E-Chain (CLOUD-WORKER-004)
- **Audio analysis metrics** — delegated to moodify-core-package

## 5. Integration Points

| System | Integration Type | Current State | Gap |
|--------|-----------------|---------------|-----|
| Runtime Supervisor | Import + call | `phase_run()` uses `run_supervised()` | OK |
| CLI | Subprocess | All phases shell out to `python3 -m moodify_runtime.cli` | Fragile — stdout parsing needed for task counts |
| Queue/Registry | Via CLI | CLI commands read/write JSONL | Indirect — engine has no direct queue visibility |
| Night Worker | None | Separate system, separate scripts | Should coordinate or merge |
| Operator Console | None | No tidal views in `operator_console.html` | Gap |
| Cloud Scheduler | None | `scheduler.py` exists but not wired | Gap (separate E-Chain) |

## 6. Evidence Inventory

| Evidence | Path | Description |
|----------|------|-------------|
| Engine source | `moodify_runtime/tidal_cycle.py` (419 lines) | Full implementation |
| Start script | `scripts/tidal_start.sh` | Background launcher |
| Stop script | `scripts/tidal_stop.sh` | Graceful shutdown |
| Status script | `scripts/tidal_status.sh` | Heartbeat reader |
| Events log | `outputs/tidal/tidal_events.jsonl` | 2 real cycles of events |
| Heartbeat | `outputs/tidal/tidal_heartbeat.json` | Last heartbeat state |
| Records | `outputs/tidal/tidal_records.jsonl` | Per-cycle summaries |
| Registry | `data/tidal_registry.jsonl` | 3 registered samples |
| Queue | `data/tidal_queue.jsonl` | 9 completed tasks (3 samples × 3 presets) |
| Night worker | `workers/night_worker.py` (809 lines) | Parallel overnight system |
| Night config | `configs/night_jobs.yaml` | Night worker configuration |
| NEM definition | `docs/nem/NEM-MOODIFY-TIDAL-CORE-PROBE-024.md` | Probe NEM plan |

## 7. Readiness Assessment

**Decision**: The tidal cycle is ready for Probe NEM hardening. The engine runs and produces events. The gaps are well-understood and addressable within the Probe → Build → System structure.

**Key unknowns to resolve in remaining Probe MHPs (468–484)**:
1. Should the tidal cycle absorb the night worker, or coordinate with it?
2. What pause/resume semantics are needed for operator workflows?
3. What SLOs are achievable for a 6–12 hour unattended run?
4. How does heartbeat integrity hold under process suspension?

## 8. Next Step

Proceed to **MHP-468: Tidal Lifecycle Vocabulary** — define the canonical state names, transitions, and event types that the Tidal Core state machine will use.
