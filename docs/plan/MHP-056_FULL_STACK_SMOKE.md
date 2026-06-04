# MHP-056: Full Stack Smoke Test — Server + CLI + UI

**Status**: completed
**Direction**: 6-Step Plan — V2 (Validation)
**Depends on**: MHP-055
**Protocol**: 泫榛 6-Step Plan Protocol

## Evidence

- API tests use TestClient (in-process)
- CLI tests use `main()` directly
- No test verifies that a uvicorn server process, CLI, and Console UI all work together
- The "real" startup path (`uvicorn ...`) has never been tested automatically

## Goal

Run a one-command smoke test that:
1. Starts a uvicorn server on a random port
2. Hits `/health` via HTTP
3. Creates a job via CLI
4. Lists jobs via the API
5. Verifies the Console HTML loads
6. Stops the server

## Acceptance Criteria

- 1 smoke test script that exercises all 3 interfaces (server, CLI, UI)
- Test can be run with a single command
- Test cleans up after itself
- Existing 107+ tests still pass

## Test Plan
```bash
python3 -m pytest moodify_runtime/tests/test_full_stack_smoke.py -v
```
