# MHP-032: Operator Job Runner

Status: proposed
Direction: MHP-031 continuation
Depends on: MHP-031 Operator Job records and API

## Context

MHP-031 made Operator Jobs visible and attachable to existing runtime run evidence. MHP-032 closes the next gap: an Operator Job should be able to request a runtime execution path instead of only attaching evidence after the fact.

## Goal

Connect Operator Jobs to the runtime queue and runner so an internal operator can move a job from intake to running to gate review.

```text
Operator Job -> runtime queue task(s) -> run_daily -> manifest -> operator detail
```

## Non-Goals

- Do not build the full UI yet.
- Do not add a new audio processing engine.
- Do not replace the existing runtime queue.
- Do not make this a public user workflow.

## Product Requirements

- A job can be marked as ready for runtime processing.
- A job can create one or more runtime queue tasks.
- A job can trigger or reference a runtime run.
- Job status changes are persisted: `waiting`, `running`, `gate_review`, `reprocess`, `failed`.
- Runtime errors are reflected back onto the Operator Job.

## Engineering Requirements

- Add a job-to-runtime adapter that maps:
  - `OperatorJob.source_audio` -> runtime task input
  - `processing_depth` -> preset/candidate strategy
  - `priority` -> runtime queue priority
  - `project_label` -> run metadata
- Add CLI/API entry points:

```text
POST /operator/jobs/{job_id}/plan-runtime
POST /operator/jobs/{job_id}/run
moodify-runtime operator-plan-runtime
moodify-runtime operator-run
```

- Reuse `run_daily` where possible.
- Keep generated audio and run outputs outside git.

## Acceptance Criteria

- A test can create an Operator Job and generate runtime queue rows from it.
- A dry-run path can show the commands that would execute.
- A successful run updates the job with `run_id` and `run_dir`.
- A failed run updates `last_error`.
- Existing runtime tests still pass.

## Test Plan

```bash
python -m pytest moodify_runtime/tests/test_operator_console.py -q
python -m pytest moodify_runtime/tests/test_operator_job_runner.py -q
```

## Done Means

Operator Jobs no longer just hold metadata. They can initiate the production line.
