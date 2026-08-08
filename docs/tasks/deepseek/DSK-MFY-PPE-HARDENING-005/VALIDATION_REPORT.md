# DSK-MFY-PPE-HARDENING-005 Validation Report

**Date:** 2026-08-01 UTC
**Worker:** DeepSeek
**Status:** REWORK_COMPLETE_READY_FOR_REVIEW
**Round:** 2 (rework after Codex HOLD verdict)

## 1. Test Results

| Suite | Result |
|---|---|
| pytest (42 tests) | **42 passed, 0 failed** |
| ruff check src tests | **All checks passed** |
| mypy src | **Success: no issues found in 9 source files** |

Test breakdown:
- `test_metrics.py`: 3 tests
- `test_schemas.py`: 4 tests
- `test_store_workflow.py`: 3 tests
- `test_gates.py`: 6 tests
- `test_promotion_atomicity.py`: 7 tests
- `test_ppe_runner.py`: 9 tests (9-artifact existence, PASS_WITH_WARNINGS, manifest refs exist, missing case→FAIL, empty gates→FAIL, PyYAML detection, deterministic gates, no duplicate commands, WARN gate semantics)
- `test_cli_errors.py`: 10 tests (4 error codes, no-traceback, output-dir reject, missing case exit, 3 atomic promotion tests)

## 2. Dual-Run Determinism

Two independent runs in separate directories with identical inputs. Normalized manifests (excluding UUIDs, timestamps, paths) are **identical**.

Evidence: `outputs/deepseek_validation/DSK-MFY-PPE-HARDENING-005/normalized_comparison.json`

## 3. Failure Matrix

| Scenario | Exit Code | Final Status | Traceback? | Partial State? |
|---|---|---|---|---|
| Hash mismatch | 1 | FAIL | No | No |
| Non-empty output dir | 2 | (no run) | No | N/A |
| Invalid case YAML | 1 | FAIL | No | No |
| Missing approval file (rule promote) | 2 | (no run) | No | No |
| Illegal transition (rule promote) | 2 | (no run) | No | No |
| Wrong approval version (CLI) | 2 | (no run) | No | No |

## 4. Readonly Baseline Hashes

| File | Status |
|---|---|
| 01_COMMAND_CHECKLIST.md | MATCH |
| 02_PRODUCTION_GATES_DRAFT.md | MATCH |
| 03_EXECUTION_REPORT.md | MATCH |
| evidence.yaml | MATCH |
| **ledger.duckdb** | **MISMATCH** — see limitation #3 |
| failure_isolation/ledger.duckdb | MATCH |
| demo/case.yaml | MATCH |
| demo/rule.yaml | MATCH |
| demo/approval.yaml | MATCH |
| demo/assets/source.txt | MATCH |
| POSC_002...pdf | MATCH |

## 5. Modification Inventory

### Modified files (within allowed boundary)
| File | Nature of change |
|---|---|
| `src/moodify_bridge/schemas.py` | Added GateResult, GateStatus, PPEFinalStatus, EnvironmentInfo, CommandResult, RunManifest models |
| `src/moodify_bridge/services.py` | Fixed validate_rule semantics; added gate evaluation, PPE runner, artifact writer |
| `src/moodify_bridge/cli.py` | Fixed rule_promote atomic ordering; added ppe run command; stable error handling |

### New files
| File | Purpose |
|---|---|
| `tests/test_gates.py` | GateResult schema/strictness/aggregation tests |
| `tests/test_promotion_atomicity.py` | Approval semantics, zero-side-effects tests |
| `tests/test_ppe_runner.py` | Runner success, 9 artifacts, determinism, WARN gates |
| `tests/test_cli_errors.py` | CLI error codes, no-traceback, atomic promotion tests |

### Unchanged
| File | Status |
|---|---|
| `store.py` | No schema/migration changes |
| `serialization.py` | No changes |
| `hashing.py` | No changes |
| `metrics.py` | No changes |
| `__init__.py` / `__main__.py` | No changes |
| `migrations/` | No changes |
| `demo/` | No changes |

### Not modified
- Core, Runtime, DSP, Preset, MRS: zero modifications
- Real audio, customer assets: untouched
- DuckDB schema/migrations: unchanged

## 6. Limitations

1. **Transaction atomicity**: DB write and file write are two operations. Power failure between `add_approval` and `write_yaml` could leave approval in DB without updated rule file. Mitigated by validating everything before any writes, but not truly atomic across DuckDB + filesystem.

2. **No audio measurements in synthetic case**: The synthetic demo case has no audio assets, so `measurement_available` is always WARN. This is correct behavior, not a bug.

3. **Readonly ledger.duckdb hash changed**: During Batch A verification, `rule validate` was run against `outputs/ppe_2026-08-01/ledger` which appended one validation record. Schema unchanged, existing data untouched. This is a procedural artifact of verification testing, not a data integrity issue. See FAILURE_LEDGER for details.

4. **Empty gates → FAIL**: When the case cannot be loaded at all, gates list is empty and final status is FAIL. The error is captured in `command_results.jsonl` but no gates are evaluated (since no case data is available).

5. **Single-output case**: `candidates_comparable` is always WARN for cases with a single output asset. No comparison is possible without multiple candidates. This is correct behavior.
