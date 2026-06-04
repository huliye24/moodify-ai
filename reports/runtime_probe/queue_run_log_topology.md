# Queue Run Log Topology Audit — MHP-091

**Date**: 2026-06-04

## Data Flow Topology

```
input_dirs/
    ↓ register_inputs()
registry.jsonl   (sample_id, path, genre, source)
    ↓ plan_queue()
queue.jsonl      (task_id, sample_id, input_path, preset, status, priority, attempts)
    ↓ run_daily()
outputs/{run_id}/
    ├── {sample_id}/{preset}/   ← processed WAVs
    ├── manifest.csv            ← per-task results
    ├── summary.json            ← aggregate stats
    ├── daily_run.log           ← text log (unstructured)
    └── daily_run.lock          ← concurrency guard
```

### Queue State Machine (current)

```
pending ──→ running ──→ done
  │                      │
  └── retry ←── failed ←─┘
```

### Missing states for resumability

```
pending ──→ claimed ──→ running ──→ done
              │           │
              └── abandoned └── failed ──→ retry
```

`claimed` prevents duplicate work after restart. `abandoned` detects crashed workers.

## JSONL Store Analysis

| Store | Path | Append-Only? | Atomic Write? | Compaction? |
|-------|------|-------------|---------------|-------------|
| operator_jobs.jsonl | data/ | ✅ append | ✅ atomic_write_jsonl for full rewrites | ✅ compact_operator_jobs() |
| operator_deliveries.jsonl | data/ | ✅ append | — | ❌ |
| registry.jsonl | data/validation/ | ✅ append | — | ❌ |
| queue.jsonl | outputs/ | ✅ append + status update | — | ❌ |
| calibration/*.jsonl | data/calibration/ | ✅ append | — | ❌ |

### Risk: Read-Modify-Write Race

`_update_job()` reads all rows, finds one by job_id, modifies it, rewrites all. This is safe for single-runner but vulnerable under concurrent access. Build NEM should add advisory file locking to JSONL writes.

## Log Completeness

| Log Source | Format | Queryable? | Retained? |
|------------|--------|-----------|-----------|
| daily_run.log | Free text | ❌ grep only | ❌ overwritten per run |
| manifest.csv | Structured | ✅ CSV | ✅ per run_id |
| summary.json | Structured | ✅ JSON | ✅ per run_id |
| gate_decisions.jsonl | Structured | ✅ JSONL | ✅ per job |
| run.log (validation) | Free text | ❌ | ❌ |
