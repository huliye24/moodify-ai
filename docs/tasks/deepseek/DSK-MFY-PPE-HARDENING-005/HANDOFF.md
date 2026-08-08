# DSK-MFY-PPE-HARDENING-005 HANDOFF (REWORK)

**Status:** REWORK_COMPLETE_READY_FOR_REVIEW
**Worker:** DeepSeek
**Date:** 2026-08-01 UTC
**Branch:** `codex/mainline-cloud-dev-20260603`
**HEAD:** `df3a8a3c8ead4eae0675733169614efe59bf395d`
**Previous Verdict:** HOLD (3 HOLD items, 5 REWORK items)
**This Rework:** All 8 steps addressed

## Rework Summary

### H-01 (readonly ledger contamination) — DOCUMENTED, NOT REVERSED
The 2026-08-01 baseline `ledger.duckdb` remains unchanged by this rework. The append-only contamination from Batch A verification is documented in FAILURE_LEDGER.md FL-001. Codex must specify a new baseline for re-verification.

### H-02 (promotion atomicity) — IMPLEMENTED
`promote_rule_atomic()` implements a 6-step transaction protocol:
1. Stale marker detection + recovery
2. Precondition validation (no side effects)
3. Temp file write (`_write_rule_file`)
4. `.promoting` marker written to disk
5. `store.add_approval()` — DB write
6. `os.replace()` — atomic file swap
7. Marker + temp cleanup

Inject points `_write_rule_file` and `_replace_file` are monkeypatchable for testing.
Test `test_no_partial_state_on_write_failure` proves zero approvals remain in DB after simulated write failure.
Test `test_no_db_approval_after_failed_transition` proves illegal transition leaves zero DB state.

### H-03 (python -m entry broken) — FIXED
`if __name__ == "__main__": app()` restored at end of cli.py.
Verified: `py -3.12 -m moodify_bridge.cli ppe run demo/case.yaml --output-dir NEW_DIR` produces all 9 artifacts, exit code 0.

### R-01 (duplicate PASS+FAIL) — FIXED
`case_validate` now records exactly one `CommandResult` (PASS if valid, FAIL if not). Verified by `test_command_results_no_duplicate_pass_fail`.

### R-02 (PyYAML marked absent) — FIXED
`_collect_environment()` now uses `__import__("yaml")` for PyYAML detection. Environmental report correctly shows `PyYAML: 6.0.3`. Verified by `test_environment_collects_pyyaml_correctly`.

### R-03 (missing stable error codes) — FIXED
All expected CLI failures use `[CODE]` prefix:
- `[APPROVAL_FILE_MISSING]` — exit 2
- `[RULE_FILE_MISSING]` — exit 2
- `[APPROVAL_RULE_MISMATCH]` — exit 2
- `[INVALID_RULE_TRANSITION]` — exit 2
- `[OUTPUT_DIR_NOT_EMPTY]` — exit 2
All verified by automated tests in `test_cli_errors.py`.

### R-04 (missing automated tests) — IMPLEMENTED
New test files:
- `tests/test_cli_errors.py` — 10 tests: 4 error code tests, no-traceback test, output-dir test, missing-case test, 3 atomicity tests (no-DB-after-fail, successful promotion, write-failure injection)
- `tests/test_ppe_runner.py` — 9 tests: 9-artifact existence, PASS_WITH_WARNINGS status, manifest references exist, nonexistent case→FAIL, empty gates→FAIL, PyYAML detection, deterministic gates, no-duplicate commands, WARN gates semantics

Total: **42 tests, 0 failures**

### R-05 (manifest artifact hash contract) — ADDRESSED
`test_artifact_hashes_in_manifest_are_stable` verifies gate results, evidence digest, measurement IDs, and FINAL_STATUS are deterministic across two independent runs. `test_manifest_references_exist` verifies referenced paths are present.

### Remaining known limitation
Cross-DB/filesystem transaction is not truly atomic at the OS level. The `.promoting` marker protocol provides recoverability (re-run promotion completes the stalled operation) but a power failure between `add_approval` and `os.replace` leaves the approval in DB with a recoverable marker. This is documented as a known limitation.

## Exact Reproduction Commands

```powershell
cd E:\moodify\moodify-bridge

# Full test suite
py -3.12 -m pytest -v          # 42 passed
py -3.12 -m ruff check src tests   # All checks passed
py -3.12 -m mypy src               # Success: no issues found

# Unified PPE baseline
py -3.12 -m moodify_bridge.cli ppe run demo/case.yaml --output-dir NEW_RUN_DIR

# CLI error verification
py -3.12 -m moodify_bridge.cli rule promote demo/rule.yaml experimental NOSUCH.yaml --root tmpdb
# → [APPROVAL_FILE_MISSING] ... exit 2

py -3.12 -m moodify_bridge.cli ppe run demo/case.yaml --output-dir E:\moodify
# → [OUTPUT_DIR_NOT_EMPTY] ... exit 2
```

## Modified File Inventory

| File | Change |
|---|---|
| `cli.py` | Restored `if __name__` entry; stable error codes; atomic promotion call |
| `services.py` | Atomic promotion protocol; fixed PyYAML detection; fixed duplicate PASS/FAIL; gate evaluation |
| `schemas.py` | PPE models (unchanged from previous round) |
| `README.md` | Updated PPE entry, gate semantics, error codes |
| `tests/test_cli_errors.py` | NEW: 10 CLI error + atomicity tests |
| `tests/test_ppe_runner.py` | NEW: 9 runner + artifact tests |
| `tests/test_store_workflow.py` | Fixed test to use explicit proposed rule |
| `tests/test_gates.py` | Unchanged |
| `tests/test_promotion_atomicity.py` | Unchanged |

## Codex Acceptance Commands

```powershell
cd E:\moodify\moodify-bridge

# 1. Full suite
py -3.12 -m pytest -v
py -3.12 -m ruff check src tests
py -3.12 -m mypy src

# 2. Independent dual-run
py -3.12 -m moodify_bridge.cli ppe run demo/case.yaml --output-dir COdex_A
py -3.12 -m moodify_bridge.cli ppe run demo/case.yaml --output-dir COdex_B

# 3. Verify no duplicate PASS+FAIL in hash mismatch
# (create tampered case, run PPE, check command_results.jsonl has exactly 1 case_validate entry)

# 4. Verify all error codes
py -3.12 -m moodify_bridge.cli rule promote demo/rule.yaml experimental NOSUCH.yaml --root tmpdb
py -3.12 -m moodify_bridge.cli ppe run demo/case.yaml --output-dir E:\moodify

# 5. Verify PyYAML in environment.json
# grep PyYAML <RUN_DIR>/environment.json  → "6.0.3", not "absent"
```

DeepSeek Worker stops here. Final judgment belongs to Codex.
