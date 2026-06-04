# Cloud State Map — MHP-251 | **Date**: 2026-06-04

## Current Cloud Surface

| Component | Module | Status | Notes |
|-----------|--------|--------|-------|
| ComputeRequest | scheduler.py | ✅ Data model | request_id, job_id, compute_class, priority |
| ComputeLease | scheduler.py | ✅ Data model | lease_id, node_id, ttl_minutes, expires_at |
| ComputeRun | scheduler.py | ✅ Data model | run_id, lease_id, node_id, started_at, finished_at |
| CostRecord | scheduler.py | ✅ Data model | record_id, compute_class, duration_s, cost_estimate |
| Scheduler API | operator_api.py | ✅ Routes exist | /scheduler/requests, /scheduler/leases, /scheduler/runs |
| Process supervisor | supervisor.py | ✅ | run_supervised() with timeout/retry |
| Runtime heartbeat | runtime_state.py | ✅ | Heartbeat class, file-based liveness |
| Runtime lease | runtime_state.py | ✅ | RuntimeLease model |
| Multi-worker support | — | ❌ | No queue partitioning, no worker ID assignment |
| Real cloud backend | — | ❌ | Models exist, no actual cloud orchestration |
| Artifact sync | — | ❌ | Output files local-only, no shared storage |
| Cost tracking | scheduler.py | ⚠️ | CostRecord exists but never populated |
| Fleet dashboard | — | ❌ | Console has scheduler view, no fleet status |

## Deployment State

| Aspect | Current | Target |
|--------|---------|--------|
| Execution model | Single-machine, single-process | Multi-worker, multi-machine |
| Queue distribution | Local JSONL only | Partitioned queue with worker assignment |
| Worker coordination | Lock file (local only) | Distributed leases with TTL |
| Output storage | Local filesystem | Shared artifact store (S3/NFS) |
| Scaling | Manual restart | Auto-scale based on queue depth |
