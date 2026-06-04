# Restart Resume Validation — MHP-121

**Date**: 2026-06-04

## Test

Simulated crash after 50% of queue tasks completed. On restart, the resumable state machine (`runtime_state.py:resume_queue()`) detected tasks in `claimed`/`running` state and recycled them to `pending`.

| Metric | Before Crash | After Resume | Delta |
|--------|-------------|--------------|-------|
| Completed tasks | 45 | 45 (skipped) | 0 |
| Remaining tasks | 45 | 45 | 0 |
| Total re-run time | — | ~1s (skip only) | — |

Resumable state machine correctly skips completed tasks and re-queues abandoned ones.
