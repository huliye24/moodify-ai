# MHP-067: Full Regression — All Tests + Real Audio + Slow Tests

**Status**: completed
**Direction**: NEM-MOODIFY-STUDIO-OS-001 / Harden-6 / V (Validation)
**Depends on**: MHP-066 (refactor complete)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

After MHP-065 (fixes) and MHP-066 (refactor), we need to prove that nothing broke. This is not just "run pytest again" — it's a systematic regression that includes:

1. All existing 107+ tests (unit + API + contract + edge cases)
2. Real audio tests (MHP-053 `@pytest.mark.slow` tests)
3. Console interaction tests (MHP-054)
4. Multi-job stability tests (MHP-055)
5. Full stack smoke test (MHP-056)

## Goal

Run the complete test suite and verify:

- 0 test failures
- 0 regressions from the fixes and refactor
- Slow tests pass (real audio processing works)
- Full stack smoke passes (server + CLI + UI)
- Test suite completes in under 10 minutes (excluding slow tests)

## Non-Goals

- Don't add new tests (this is a verification gate, not a test-writing task)
- Don't fix flaky tests (document and defer if any found)

## Acceptance Criteria
- All tests pass: `python3 -m pytest moodify_runtime/tests/ -v` → 0 failures
- Slow tests pass: `python3 -m pytest moodify_runtime/tests/ -v -m slow` → 0 failures
- Test count ≥120 (including slow + interaction + multi-job + full stack)
- Regression report written to `reports/nem_studio_os_001/regression_report.md`

## Test Plan
```bash
# Full suite
python3 -m pytest moodify_runtime/tests/ -v --tb=long

# Slow tests
python3 -m pytest moodify_runtime/tests/ -v -m slow --tb=long

# Count
python3 -m pytest moodify_runtime/tests/ -q --tb=no
```

## Done Means

The system is proven stable after production refactoring. We have confidence that Harden-6 did not introduce regressions.
