# Cloud Scheduler Handoff Protocol — MHP-134

**E-Chain**: ECHAIN-MOODIFY-RUNTIME-001

## Current State

`scheduler.py` has data models (`allocate_lease`, `schedule_job`, `record_compute_run`) but no real cloud backend. The API exposes `/scheduler/*` routes that write to local JSONL stores.

## Handoff Contract

When a cloud backend is implemented (next E-Chain):

1. **Queue handoff**: Cloud scheduler reads `queue.jsonl` and distributes tasks to workers
2. **Result ingestion**: Workers write `manifest.csv` rows back to the local output dir
3. **Heartbeat from workers**: Each cloud worker POSTs to `/runtime/heartbeat` (or writes to a shared heartbeat file)
4. **Lease coordination**: `RuntimeLease` model prevents duplicate task execution across workers

## Migration Path

```text
Local single-runner (current)
  → Local multi-worker (multiprocessing)
  → Hybrid local + cloud (scheduler distributes)
  → Full cloud workers (queue in object storage)
```
