# MHP-066: Production Refactor — Error Handling, Logging, Config Externalization

**Status**: proposed
**Direction**: NEM-MOODIFY-STUDIO-OS-001 / Harden-6 / E (Execution)
**Depends on**: MHP-065 (issues fixed)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

The codebase was built rapidly across 2 six-step plan cycles. It works (107 tests prove it), but it has technical debt that matters for production:

- Error handling: some API handlers catch exceptions broadly, others let them propagate
- Logging: operator_console functions have no structured logging
- Config: some paths are hardcoded in test files, others use RuntimeConfig
- Import hygiene: some modules import from sibling modules at function scope (lazy imports for circular dependency avoidance are fine, but undocumented)
- Storage: JSONL files grow unbounded — no rotation, no compaction

## Goal

Refactor for production without changing behavior:

1. **Error handling**: Every API handler returns proper HTTP status codes (4xx for client errors, 5xx for server errors). No bare 500s from unhandled exceptions.
2. **Logging**: Add structured log calls at entry/exit of key functions (create_operator_job, run_operator_job, attach_run_report_to_job, create_delivery_record, build_operator_report_bundle)
3. **Config**: Ensure zero hardcoded paths in production code. All paths flow from RuntimeConfig.
4. **Storage**: Add a `compact_operator_jobs()` function that deduplicates and prunes old records
5. **Startup**: Add a health-check endpoint that verifies all data directories exist and are writable

## Non-Goals

- Don't change function signatures
- Don't change data models
- Don't change the API contract
- Don't optimize performance

## Acceptance Criteria
- 0 unhandled exceptions in the API layer (all caught and returned as proper HTTP errors)
- Key functions have structured log calls
- 0 hardcoded paths outside of test files
- `compact_operator_jobs()` exists and is tested
- Health check verifies directory access
- Existing 107+ tests still pass
- New tests for error handling paths

## Test Plan
```bash
python3 -m pytest moodify_runtime/tests/ -v
python3 -m pytest moodify_runtime/tests/test_production_refactor.py -v
```
