# MHP-038: Cloud GPU Scheduler

Status: proposed
Direction: cloud production capacity
Depends on: MHP-037 Craft Library Writeback

## Context

Deep processing and studio processing need cloud capacity, scheduling, cost tracking, and failure recovery. MHP-038 turns runtime execution into a cloud production scheduler.

## Goal

Introduce a cloud scheduling layer for long-running and GPU-backed jobs.

## Non-Goals

- Do not require Kubernetes unless current scale demands it.
- Do not introduce vendor lock-in.
- Do not rewrite the audio engine.

## Product Requirements

- Jobs can request compute class:
  - `cpu_standard`
  - `gpu_standard`
  - `gpu_deep`
  - `studio_reserved`
- Scheduler tracks:
  - queue time
  - execution time
  - node id
  - estimated cost
  - retry count
  - failure class

## Engineering Requirements

- Add scheduler records:

```text
ComputeRequest
ComputeLease
ComputeRun
CostRecord
```

- Add API/CLI:

```text
POST /operator/jobs/{job_id}/schedule
GET  /scheduler/runs
moodify-runtime scheduler-plan
moodify-runtime scheduler-run
```

- Keep local fallback path for tests and small jobs.

## Acceptance Criteria

- A job can be scheduled without immediate execution.
- Scheduler can record a completed compute run.
- Cost records are produced for each run.
- Failed leases can be retried.
- Tests use a fake scheduler backend.

## Test Plan

```bash
python -m pytest moodify_runtime/tests/test_cloud_scheduler.py -q
```

## Done Means

Moodify has a production capacity layer, not just a script runner.
