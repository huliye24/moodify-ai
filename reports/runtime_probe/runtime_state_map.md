# Runtime State Map — MHP-089

**Date**: 2026-06-04  
**E-Chain**: ECHAIN-MOODIFY-RUNTIME-001  
**NEM**: NEM-MOODIFY-RUNTIME-PROBE-003  
**Protocol**: E-Chain 54, Phase: Probe Plan-6A Problem Boundary

---

## 1. Module Inventory

Current runtime surface: **17 modules, 2,630+ lines of core runtime code**.

| Module | Lines | Role | Health |
|--------|-------|------|--------|
| `runner.py` | 320 | Core execution loop: lock, queue, retry, disk check | ✅ Functional, sequential only |
| `operator_console.py` | 1,195 | Job lifecycle, gate, storage, compaction | ✅ Production-ready |
| `cli.py` | 496 | 40+ subcommands | ✅ Feature-complete |
| `config.py` | 117 | RuntimeConfig dataclass | ✅ Clean, extensible |
| `utils.py` | 344 | I/O, hashing, subprocess, locks, templates | ✅ Stable |
| `queue.py` | 86 | Task queue management | ✅ Functional |
| `registry.py` | 72 | Audio input registration | ✅ Functional |
| `metrics.py` | 303+ | WAV analysis, pseudo_mrs, MRS Open | ✅ Calibrated |
| `over_dark.py` | 230+ | FFT graduated over-dark | ✅ Fixed v0.2 |
| `mrs_engine.py` | 150+ | Unified MRS scoring entry | ✅ New |
| `mrs_calibration.py` | 206 | Calibration lab | ✅ Functional |
| `operator_api.py` | 500+ | FastAPI, 40 routes | ✅ Production |
| `studio.py` | ~200 | Client/project/order layer | ✅ Functional |
| `scheduler.py` | ~120 | Cloud GPU scheduler models | ⚠️ Models only, no real backend |
| `craft_memory.py` | ~100 | Craft library writeback | ✅ Functional |
| `planner.py` | ~80 | Experiment planning | ⚠️ Research-only |
| `failure.py` | ~50 | Basic failure analysis | ⚠️ Minimal |

---

## 2. Execution Flow Map

```
CLI/API entry
    ↓
plan_operator_runtime()     # Register inputs → create queue tasks
    ↓
run_operator_job()           # Dispatch to run_daily()
    ↓
run_daily()                  # Core loop
    ├── Lock file acquire
    ├── Disk space check
    ├── load_queue()          # Read JSONL queue
    ├── select_pending_tasks()# Filter pending/retry tasks
    ├── for each task:
    │   ├── render command template
    │   ├── subprocess.run()  # BLOCKING — no timeout enforcement at OS level
    │   ├── collect stdout/stderr
    │   ├── retry on failure (max_retries_per_task)
    │   └── write manifest.csv row
    ├── write summary.json
    └── lock release
```

### Control flow characteristics

| Aspect | Current | Target |
|--------|---------|--------|
| Execution model | Sequential, single-process | Parallel-ready, multi-worker |
| Failure recovery | Retry within same run, no cross-run resume | Resumable queue with checkpoint |
| Observability | Text log + manifest.csv only | Structured event stream + heartbeat |
| Process supervision | None — subprocess.run() blocks | Timeout watchdog + crash restart |
| State persistence | Queue JSONL + manifest CSV | Event-sourced state + resumable snapshots |
| Resource awareness | Disk check only | CPU, memory, GPU monitoring |
| Long-running | Manual loops (run_daily called once) | Continuous runtime daemon mode |

---

## 3. Command Surface Inventory

40+ CLI subcommands across 10 command groups:

| Group | Commands | Coverage |
|-------|----------|----------|
| `register` | scan input_dirs, write registry | ✅ |
| `plan` | generate run_queue.jsonl from registry | ✅ |
| `run` | execute pending/retry queue | ⚠️ Sequential only |
| `report` | generate daily Markdown report | ✅ |
| `craft` | generate craft memory seeds | ✅ |
| `failures` | analyze failure types | ⚠️ Basic stats only |
| `next` | suggest next experiments | ⚠️ Planner-driven |
| `operator-*` | create/list/attach/deliver jobs | ✅ |
| `operator-run` | run operator job | ✅ |
| `operator-report` | build operator report bundle | ✅ |

---

## 4. Identified Gaps

### P0 — Structural (would block production adoption)

| # | Gap | Impact | Evidence |
|---|-----|--------|----------|
| 1 | **No process supervision** | Crashed subprocess = dead run. No watchdog, no restart. | runner.py:139 — blocking subprocess.run() |
| 2 | **No resumable state** | If process dies mid-run, all progress is lost. Queue state is append-only — can't mark partial completion. | queue.py: JSONL with status flags, no checkpoint |
| 3 | **No structured events** | All runtime telemetry is in text logs. Can't query failure rates, latency percentiles, or task distribution without parsing logs. | runner.py: LineLogger writes unstructured text |
| 4 | **No SLO framework** | Zero runtime SLOs defined. No uptime target, no processing-time SLA, no error budget. | Nothing in configs/ or docs/ |

### P1 — Operational (would degrade production quality)

| # | Gap | Impact | Evidence |
|---|-----|--------|----------|
| 5 | **Sequential only** | 90 tasks × 30s = 45min single-threaded. No parallelism. | runner.py: for loop over tasks |
| 6 | **No heartbeat** | Can't distinguish "running slowly" from "dead." Cloud scheduler has no liveness signal. | No heartbeat endpoint or file |
| 7 | **No failure injection** | Can't test recovery paths without manually killing processes. | No test_failure_injection.py |
| 8 | **config.json only** | No runtime profiles (dev/staging/prod). Same config for all environments. | config.py: single RuntimeConfig |

### P2 — Strategic (future capability)

| # | Gap | Impact |
|---|-----|--------|
| 9 | **No cloud worker backend** | scheduler.py has models but no actual cloud orchestration |
| 10 | **No progress streaming** | Console can't show real-time task progress |
| 11 | **No runtime manifest version** | No versioned manifest of runtime capabilities |

---

## 5. Dependency Graph

```
config.py (zero deps)
    ↓
utils.py → registry.py → queue.py
    ↓
runner.py (run_daily)
    ↓
operator_console.py (jobs, gates, reports)
    ↓
operator_api.py (FastAPI) + cli.py (CLI)
    ↓
studio.py / scheduler.py / mrs_calibration.py / craft_memory.py
    ↓
mrs_engine.py / over_dark.py / metrics.py (scoring layer)
```

No circular imports. `config.py` is the true foundation — all paths flow from RuntimeConfig.

---

## 6. Phase Transition Target

```
S_current: script-runnable runtime
  ──→ S_target: production-grade unattended runtime

Required capabilities to reach S_target:
  S1. Observable   — heartbeat + structured events
  S2. Resumable    — checkpoint + restart
  S3. Recoverable  — supervisor + retry policy
  S4. Operable     — runtime dashboard + runbook
  S5. Reusable     — event schema spec + handoff pack
```

---

## 7. Current Test Coverage

| Category | Tests | Coverage |
|----------|-------|----------|
| Unit + API + Contract | 119 | Operator Console, API, Gate |
| MRS Gate | 16 | Threshold dispatch, over-dark, boundaries |
| Real Audio | 3 | E2E DSP pipeline |
| Full Stack Smoke | 7 | uvicorn + HTTP + CLI |
| Runtime-specific tests | 10 | Operator job runner only |
| **Runtime supervisor** | **0** | **Nothing exists yet** |
| **Failure recovery** | **0** | **Nothing exists yet** |
| **Parallel/multi-worker** | **0** | **Nothing exists yet** |

**Total**: 145 tests, 0 runtime-specific infrastructure tests.

---

> This map is a probe artifact. It reduces unknowns before construction. The gaps listed here form the Probe Experiment Backlog (MHP-094).
