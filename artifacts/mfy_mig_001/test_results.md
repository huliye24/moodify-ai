# MFY-MIG-001 Test Results

Recorded: 2026-08-08 (Asia/Shanghai)

| Check | Result |
|---|---|
| Contract and architecture tests | PASS — 37 passed |
| Complete core test suite | PASS — 146 passed, 7 existing matplotlib warnings |
| Changed/new Python Ruff scope | PASS |
| Schema generation `--check` | PASS |
| `verify_mfy_mig_001.py` | PASS |
| `git diff --check` | PASS |

## Full Ruff baseline comparison

`python -m ruff check src/moodify tests` continues to report the same 23
violations recorded before implementation. All occur in pre-existing test
files. No new contract or script file contributes a Ruff violation.

Classification: `PRE_EXISTING_BASELINE_FAILURE`, not `NEW_REGRESSION`.

## Non-regression conclusion

The original 109 tests and all 37 new tests pass. Existing v0.1 runtime,
Android, cloud, MRS, B-matrix, and DSP behavior was not modified.
