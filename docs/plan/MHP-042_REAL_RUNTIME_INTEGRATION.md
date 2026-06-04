# MHP-042: Real Runtime Integration — Operator Jobs with Live Audio Processing

**Status**: proposed  
**Direction**: 6-Step Plan Cycle — E2 (Execution 2)  
**Depends on**: MHP-041 API Deepening  
**Protocol**: 泫榛 6-Step Plan Protocol — Plan = 2E + 2V + 1S + 1N

## Context

MHP-032 built `run_operator_job()` but it is **only tested with `dry_run=True`**. The function calls `run_daily()` internally, but:

- No test exercises the real audio processing path
- No test verifies that `run_operator_job()` correctly calls `attach_run_report_to_job()` after a real run
- The `run_operator_job` flow has no status polling — the caller must wait for completion with no progress feedback
- Error handling: if `run_daily` fails mid-way, the job status update path is untested
- There's no way to run a single operator job with a specific audio file and see the full pipeline work end-to-end with real processing

MHP-040's integration test uses *simulated* runs (manifest.csv injection) rather than real audio processing. This was correct for v0.1 alpha — now we need the real path proven.

## Goal

Make `run_operator_job` work with real audio processing. A single CLI command or API call should be able to:

1. Take a real WAV file
2. Register it
3. Plan queue tasks
4. Execute `run_daily` with real DSP processing
5. Attach the resulting manifest as job evidence
6. Reflect errors back onto the job status

And all of this must be **testable**.

## Non-Goals

- Do not add async/background job execution (synchronous CLI is sufficient for alpha)
- Do not add progress streaming
- Do not add multi-job parallel execution
- Do not replace `run_daily` — wrap it, don't rewrite it

## Engineering Requirements

### 1. `run_operator_job` real-path hardening

```python
# Current flow (broken for real runs):
#   1. Update job to "running"
#   2. Call run_daily(cfg)
#   3. If dry_run → revert to "waiting"
#   4. If fatal_error → update to "failed"
#   5. Otherwise → attach_run_report_to_job()

# Required hardening:
#   - Verify that queue tasks exist before calling run_daily
#   - If queue is empty, return clear error (don't silently succeed)
#   - Track which run_id was generated
#   - After run_daily completes, verify manifest.csv exists
#   - If manifest.csv is missing or empty, treat as failure
#   - Test with a real audio file through the full pipeline
```

### 2. Add `--live` flag to CLI

```text
moodify-runtime operator-run --job-id <id>           # dry-run (default safe)
moodify-runtime operator-run --job-id <id> --live    # real audio processing
```

### 3. Add status field: `run_started_at`, `run_finished_at` to job

The job should record when the run started and finished, not just the generic `updated_at`.

### 4. Test with baseline audio

Use `moodify-core-package/tests/baseline/test_audio/` WAV files as test inputs. The `run_daily` function processes real audio through the `moodify` CLI or `moodify.cli` module. The test must verify:

- A job can be created with a real WAV source
- Runtime planning creates queue tasks
- `run_operator_job` with `--live` calls the processing engine
- The job status transitions through: waiting → running → gate_review
- The attached detail contains non-empty candidate_versions
- The gate decisions are based on actual MRS metrics (not synthetic data)

## Acceptance Criteria

- `run_operator_job(cfg, job_id)` works with real audio (not just dry-run)
- Real run produces manifest.csv with at least one row
- Job status correctly reflects: waiting → running → gate_review (or failed)
- `run_started_at` and `run_finished_at` are recorded on the job
- Empty queue before `run_operator_job` produces a clear error
- Missing manifest after run produces a clear error
- Existing 38 tests still pass
- At least 1 test exercises the real audio path (may be slow — mark with `@pytest.mark.slow`)

## Test Plan

```bash
# Fast tests (unit-level, no audio processing)
python3 -m pytest moodify_runtime/tests/test_operator_job_runner.py -v

# Slow test (real audio processing)
python3 -m pytest moodify_runtime/tests/test_operator_job_runner.py -v -m slow
```

## Done Means

An operator can type `moodify-runtime operator-run --job-id <id> --live` and watch real audio get processed through the full pipeline — not just see a dry-run plan.
