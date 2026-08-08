# DSK-MFY-PPE-HARDENING-005 Failure Ledger

## FL-001: Readonly ledger.duckdb hash changed

- **Batch:** A (verification phase)
- **Severity:** Procedural — append-only, no data loss
- **Status:** Documented, NOT blocking
- **Root cause:** Running `rule validate demo/rule.yaml --root outputs/ppe_2026-08-01/ledger` during Batch A verification appended a new ValidationRecord to the baseline DuckDB. The baselines were specified as readonly but the verification command wrote to the ledger.
- **Impact:** One additional row in `validations` table (subject_type=rule, subject_id=R-DEMO-001@1.0.0, valid=true). One additional row in `ledger_events` (event_type=validated). Schema unchanged. No existing data modified or deleted.
- **Hash before:** `f58b62c91f5242c74fbbc26524fcd0a9c603b45d19ef80844a7a890fbbb4e7de`
- **Hash after:** changed (new validation + event rows appended)
- **Recovery:** None needed — append-only operation, data integrity preserved. Codex may choose to re-create the baseline ledger from scratch if pristine state is required.
- **Prevention:** Future verification commands must use a temporary ledger root, never the baseline.

## FL-002: Empty gates produce PASS before fix

- **Batch:** B (initial implementation)
- **Severity:** Bug — fixed
- **Status:** Resolved
- **Root cause:** `determine_final_status([])` returned `PASS` because no gates meant no failures. Missing/invalid case files produced empty gate lists with misleading PASS status.
- **Fix:** Empty gates list now produces `FAIL`. `determine_final_status` returns `FAIL` when `not gates`.
- **Verified:** Missing case and invalid YAML now correctly produce FAIL with exit code 1.

## FL-003: EvidencePacket case_digest validation blocks error reports

- **Batch:** C (failure matrix testing)
- **Severity:** Bug — fixed
- **Status:** Resolved
- **Root cause:** Error paths in `ppe_run` created `EvidencePacket(case_digest="")` but `Sha256` pattern requires `^[0-9a-f]{64}$`. This caused Pydantic validation errors during error reporting.
- **Fix:** Changed placeholder to `case_digest="0" * 64` (valid 64-char hex string).
- **Verified:** Hash mismatch failure reports now generate correctly.

## FL-004: FileNotFoundError swallowed by generic Exception handler

- **Batch:** B (initial implementation)
- **Severity:** Bug — fixed
- **Status:** Resolved
- **Root cause:** CLI had `except FileNotFoundError` before `except Exception`, but `ppe_run` internally catches all exceptions. The FileNotFoundError never propagated to CLI.
- **Fix:** Simplified CLI handler to let ppe_run catch all errors and rely on manifest final_status. FileNotFoundError is now captured in command_results with CASE_CREATE_FAILED error code.
- **Verified:** Missing case file → FAIL with exit code 1, error recorded in command_results.jsonl.

## FL-005: `python -m` entry point missing

- **Batch:** HOLD review (Codex acceptance)
- **Severity:** Bug — fixed in rework
- **Status:** Resolved
- **Root cause:** `if __name__ == "__main__": app()` was lost during editing of cli.py. `python -m moodify_bridge.cli` produced exit 0 with no output and no artifacts.
- **Fix:** Restored `if __name__ == "__main__": app()` at end of cli.py.
- **Verified:** `py -3.12 -m moodify_bridge.cli ppe run demo/case.yaml --output-dir NEW_DIR` produces all 9 artifacts.

## FL-006: Duplicate PASS+FAIL for same validation step

- **Batch:** B (implementation)
- **Severity:** Bug — fixed in rework
- **Status:** Resolved
- **Root cause:** `ppe_run` Step 2 first recorded PASS (exit_code=0), then if validation.valid was False, recorded a second FAIL (exit_code=1) for the same `case_validate` action. This produced contradictory audit records.
- **Fix:** Only one CommandResult is recorded per action — PASS if valid, FAIL if not.
- **Verified:** `test_command_results_no_duplicate_pass_fail` ensures each action appears exactly once.

## FL-007: PyYAML reported as absent in environment

- **Batch:** B (implementation)
- **Severity:** Bug — fixed in rework
- **Status:** Resolved
- **Root cause:** `__import__("PyYAML")` fails because the actual module name is `yaml`. The package name and import name differ.
- **Fix:** Added `import_map` that maps display names to actual module names: `"PyYAML": "yaml"`.
- **Verified:** `test_environment_collects_pyyaml_correctly` asserts PyYAML version is detected.

## FL-008: Stable error codes missing from CLI

- **Batch:** B (implementation)  
- **Severity:** Missing requirement — fixed in rework
- **Status:** Resolved
- **Root cause:** CLI errors only output natural language messages without machine-readable codes.
- **Fix:** All expected errors now use `[CODE]` prefix format: `APPROVAL_FILE_MISSING`, `RULE_FILE_MISSING`, `APPROVAL_RULE_MISMATCH`, `INVALID_RULE_TRANSITION`, `OUTPUT_DIR_NOT_EMPTY`.
- **Verified:** 10 `test_cli_errors.py` tests assert error codes in output.
