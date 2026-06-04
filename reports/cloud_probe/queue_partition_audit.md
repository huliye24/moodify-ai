# Queue Partition Audit — MHP-254 | **Date**: 2026-06-04

## Current Queue Model

```
queue.jsonl (single file)
  → run_daily() reads all rows
  → select_pending_tasks() filters by status
  → processes sequentially
  → writes results to manifest.csv
```

## Partitioning Strategy

| Strategy | Pros | Cons | Feasibility |
|----------|------|------|-------------|
| **Round-robin by task_id hash** | Even distribution, simple | Requires worker count known upfront | ✅ Simple to implement |
| **Genre-based partition** | Genre-specific workers, preset affinity | Uneven distribution (vocal=16, ambient=6) | ⚠️ Workable but imbalanced |
| **Priority-based partition** | High-priority tasks go to fast workers | Complex priority system needed | ❌ Over-engineered for v0.1 |
| **Claim-based (worker pulls)** | Dynamic, fault-tolerant | Needs distributed coordination | ✅ Best for production |

## Recommendation

**Claim-based with TTL**: each worker claims N tasks with a lease TTL. If worker doesn't complete within TTL, tasks are reclaimed. This is the pattern already designed in `runtime_state.py:RuntimeLease`.
