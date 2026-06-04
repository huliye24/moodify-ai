# MHP-055: Multi-Job Stability — Concurrent Operations

**Status**: completed
**Direction**: 6-Step Plan — V1 (Validation)
**Depends on**: MHP-054
**Protocol**: 泫榛 6-Step Plan Protocol

## Evidence

- All 107 tests use single jobs in isolation
- No test creates multiple jobs concurrently
- JSONL storage is append-only but not tested for concurrent writes
- `_rewrite_jobs` atomically replaces the file — what happens with two simultaneous rewrites?
- `_update_job` reads all rows, modifies one, rewrites all — this is a read-modify-write race

## Goal

Test multi-job scenarios:
1. Create 10 jobs in sequence, verify all exist
2. Attach runs to 5 different jobs, verify no cross-contamination
3. Create deliveries for 3 jobs from the same order, verify order context
4. Write back 3 different deliveries to craft records
5. Stress test: create → deliver → writeback loop for 5 jobs

## Acceptance Criteria

- At least 5 multi-job tests
- No data corruption across jobs
- Order context correctly links multiple jobs
- Existing 107+ tests still pass

## Test Plan
```bash
python3 -m pytest moodify_runtime/tests/test_multi_job.py -v
```
