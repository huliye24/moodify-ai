# MFY-CR-P08 — RESOURCE BUDGET

## Accounting

Every job records `ResourceUsage` into the result payload:
`cpu_time_s, wall_time_s, peak_memory_mb, disk_temp_usage_mb,
external_api_usage, candidate_count, stem_count`.

- wall/cpu: `time.perf_counter` / `time.process_time`.
- peak memory: tracemalloc when enabled; Windows has no getrusage RSS, so the
  value is honestly reported (0.0 when not tracing) — documented limitation.
- disk: workspace temp usage measured at finalize.

## Budget

| Limit | Value | Behavior on breach |
|---|---|---|
| wall_time | 1800 s (configurable `EngineConfig.max_wall_time_s`) | FAILED `RESOURCE_LIMIT` (PERMANENT, no retry loop) |
| candidate_count | 4 | FAILED `RESOURCE_LIMIT` |
| stem_count | 0 (v0.1) | FAILED if ever produced |

MemoryError at any stage -> FAILED `RESOURCE_LIMIT` (PERMANENT). The worker
never blindly retries OOM; the job is preserved for operator review.

## Worker precheck

Before each lease, `safe_to_start` (node resources) checks available memory
(≥256 MiB default) and free disk (≥1 GiB default); on failure the worker
DEFERs (logs, waits, re-checks) — it never starts a job it cannot finish.

## Concurrency

Worker concurrency = 1 (single process, single lease). This is deliberate:
no evidence of capacity for parallel reconstruction jobs exists yet; raising
concurrency is deferred until the LA product node shows real headroom.

## Observability

Structured logs per job: `job_id, case_id, stage, duration, status, failure,
resource, external_api_usage, result id`. Logs never include raw audio,
secrets, private keys, or auth tokens.
