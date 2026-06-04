# MHP-470: Tidal Queue Intake Audit

**Status**: completed
**Date**: 2026-06-04
**Chain**: ECHAIN-MOODIFY-TIDAL-CORE-008 / NEM-MOODIFY-TIDAL-CORE-PROBE-024
**Plan-6**: Probe Plan-6A: Boundary / P4 (Validation)
**Depends on**: MHP-469 (Tidal Safety Risk Taxonomy)

## 1. Purpose

Audit how tasks enter the tidal queue, assess capacity limits, fairness properties, starvation risks, and queue hygiene. This informs the Build NEM's intake queue model (MHP-487).

## 2. Current Intake Pipeline

```
tidal_input/*.wav
    │
    ▼
[phase_register()] ──► cli.py register ──► registry.py append_registry()
    │                                        │
    │                                        ▼
    │                                   tidal_registry.jsonl
    │                                        │
    ▼                                        │
[phase_plan()] ──► cli.py plan ──► queue.py plan_queue()
                     │                     │
                     │                     ▼
                     │              registry × presets → tidal_queue.jsonl
                     │
                     ▼
[phase_run()] ──► supervisor.py ──► cli.py run ──► processes pending tasks
```

## 3. Queue Data Model

Each task in `tidal_queue.jsonl`:

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string | Unique ID: `TASK_{sample_id}_{preset}` |
| `sample_id` | string | Registry sample ID |
| `input_path` | string | Absolute path to audio file |
| `preset` | string | Processing preset name |
| `status` | enum | `pending`, `running`, `done`, `failed` |
| `priority` | int | Task priority (default 5, range 1-10) |
| `reason` | string | Why this task was created (`daily_run`) |
| `created_at` | ISO8601 | Creation timestamp |
| `started_at` | ISO8601 or null | When execution began |
| `finished_at` | ISO8601 or null | When execution ended |
| `run_id` | string or null | Batch run identifier |
| `output_dir` | string or null | Path to processing output |
| `attempts` | int | Number of execution attempts |
| `last_error` | string or null | Last error message |

## 4. Intake Properties

### 4.1 Throughput Characteristics

| Property | Current Value | Assessment |
|----------|--------------|------------|
| Intake method | Full cross-product (registry × presets) | **Bottleneck**: grows as O(samples × presets) |
| Dedup strategy | `(sample_id, preset)` key check | Correct but O(n) per task |
| Current registry size | 3 samples | Trivial now; will grow |
| Current preset count | 3 (warm_vocal, clean_master, wide_space) | Small |
| Max queue size (current) | 9 tasks (3 × 3) | Trivial |
| Max queue size (projected) | 100 samples × 10 presets = 1000 | Acceptable for JSONL |

### 4.2 Intake Fairness

| Property | Assessment |
|----------|-----------|
| Registration order | First-come-first-served (FIFO by file discovery) |
| Task creation order | Nested loops: samples outer, presets inner |
| Preset fairness | Equal — all presets applied to all samples |
| Priority distribution | All tasks get same priority (5) — no differentiation |
| Starvation risk | **Low**: all eligible tasks are created at plan time |
| Batching | No — all tasks created in one `plan_queue()` call |

### 4.3 Queue Hygiene

| Check | Status | Issue |
|-------|--------|-------|
| Duplicate prevention | ✅ Working | `existing_task_keys()` dedup |
| Stale task cleanup | ❌ Missing | Done tasks stay in queue forever |
| Failed task re-queue | ❌ Missing | Failed tasks stay as `failed` — never retried by engine |
| Queue compaction | ❌ Missing | JSONL grows unbounded |
| Queue-output consistency | ❌ Missing | No check that `done` tasks have actual outputs |
| Atomic writes | ✅ Yes | `atomic_write_jsonl()` for rewrites |
| Concurrent access | ❌ Missing | No file locking; two planners would conflict |

## 5. Intake Gap Analysis

### G1: No Queue Capacity Limit
`plan_queue()` has `max_new_tasks` parameter but it defaults to 0 (unlimited). A large registry with many presets could generate thousands of tasks with no backpressure.

### G2: No Task Differentiation
All tasks get `priority=5` and `reason="daily_run"`. There's no way to prioritize certain samples or presets, or to create tasks with different reasons (e.g., `gate_reprocess`, `operator_request`).

### G3: No Queue Garbage Collection
Done/failed tasks accumulate in the JSONL file. On subsequent cycles, `existing_task_keys()` scans the entire file to find already-planned tasks — O(n) per task, growing without bound.

### G4: No Intake Source Attribution
Tasks are not tagged with which cycle or moon created them. This makes it hard to answer "which cycle's work produced this output?"

### G5: Registry Has No Health Validation
`plan_queue()` trusts the registry. If a registered sample's file has been deleted, the task will fail at runtime with no pre-flight check.

### G6: Plan Phase Doesn't Report Queue Stats
`phase_plan()` in tidal_cycle.py returns `{"ok": True/False}` but doesn't extract `added` count from `plan_queue()`'s return value. The engine can't tell how many new tasks were created.

## 6. Build NEM Intake Requirements

From this audit, the Build NEM intake queue model (MHP-487) must:

1. **Capacity guard**: Hard limit on queue size (e.g., 500 tasks); refuse new tasks when exceeded
2. **Task lifecycle**: Support status transitions: `pending → running → done | failed | skipped`
3. **Queue garbage collection**: Archive completed tasks after N cycles; compact the active queue
4. **Priority bands**: Support at least 3 priority levels (HIGH=operator, MEDIUM=daily, LOW=reprocess)
5. **Intake reason codes**: `daily_run`, `gate_reprocess`, `operator_request`, `bootstrap`
6. **Registry health check**: Validate sample path existence before creating task
7. **Intake metrics**: Report `added`, `skipped`, `total_pending` per plan phase
8. **Moon attribution**: Tag each task with its creating `moon_id` and `cycle_number`
