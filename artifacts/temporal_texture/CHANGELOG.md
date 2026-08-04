# Temporal Texture Wave 1 — CHANGELOG

Task: DSK-MFY-TEMPORAL-TEXTURE-001 · 2026-08-04 · Baseline commit: `7ffec6b`
All changes are behavior-preserving unless explicitly listed under "Authorized behavior changes".

## Modules refactored (7 of 8; see UNRESOLVED.md for services.py)

### 1. `moodify-core-package/src/moodify/orchestration/workflow_engine.py` (5E → 0E)
- Removed 4 empty exception handlers (TT-EMPTY-EXCEPTION):
  - `_build_result` re-diagnose failure → `logger.warning` + explicit `ws_after_obj = None`
  - `_run_diagnosis` craft-match failure → recorded in `PhaseResult.warnings`
  - `_run_spatial` width resolution (2 handlers) → merged into `_resolve_spatial_width` helper that returns explicit warnings
- Split `_finalize` (complexity 23, 69 lines) into `_narrate_diagnosis` / `_save_history` / `_update_calibration`
- `_try_rag` silent broad catch → `logger.debug` with exception
- Fixed 124-char line in calibration log
- Added characterization tests: `tests/orchestration/test_workflow_engine_texture.py` (11 tests)

### 2. `moodify_runtime/operator_console.py` (3E → 1E)
- Split `run_operator_job` (179 lines) into thin shell + `_preflight_operator_job` /
  `_fail_operator_job` / `_handle_operator_run_outcome`; removed 4 duplicated failure-state writes
- Split `build_operator_report_bundle` (161 lines) into `_load_job_detail` / `_build_bundle_summary` /
  `_write_summary_md` / `_write_delivery_md` / `_write_manifest_csv`
- Extracted over-dark gate logic into `_over_dark_decision`
- Remaining error: `decide_candidate_gate` 12 params — public API, signature preserved (see UNRESOLVED.md)

### 3. `moodify_runtime/craft_processes.py` (4E → 0E)
- Split `execute_operation` (335 lines, complexity 47, nesting 23) into 22 dispatch handlers +
  `CRAFT_OPERATION_DISPATCH` table; DSP math untouched
- `validate_params` nesting 7 → 4 via guard clause (`if key not in params: continue`)
- Added characterization tests: `tests/test_craft_texture.py` (50 tests, all 22 ops)
- **Authorized behavior changes:**
  - `center_focus` on mono input: previously crashed with `NameError: name 'metrics' is not defined`;
    now returns explicit failure `center_focus requires stereo input` (error message text changed)
  - `_write_wav` stereo flattening behavior (single-channel output) is a **pre-existing bug**,
    frozen by tests as current behavior; fix deferred (see UNRESOLVED.md)

### 4. `moodify_runtime/runner.py` (2E → 0E)
- Split `run_daily` (307 lines, complexity 39) into orchestration shell +
  `_build_task_context` / `_execute_task_with_retries` / `_handle_rights_blocked` /
  `_build_manifest_row` / `_process_one_task` with `_RunSession` dataclass
- Removed stale local variables (`max_retries`, `stop_on_first`, `sleep_between`)
- Added characterization tests: `tests/test_runner_texture.py` (8 tests: dry-run, rights gate,
  retry, failure recording, disk-full)
- **Authorized behavior changes:** none. Note: the first splice attempt introduced a
  `NameError` on `sleep_between` inside `_process_one_task`; fixed during the session
  (tests caught the failure mode only after the fix; final state verified by 51 related tests).

### 5. `moodify-core-package/src/moodify/v01_pipeline.py` (4E → 1E)
- Removed 2 empty exception handlers:
  - `scan_audio` spectral-centroid failure → `scan.warnings.append(...)`
  - `_quality_gate` mrs_adapter failure → `logger.debug` fallback notice
- `_save_report` 11 params → `_ReportPayload` dataclass
- Extracted `_validate_input` from `process_audio`
- Remaining error: `process_audio` 179-line orchestrator (see UNRESOLVED.md)
- **Authorized behavior changes:** `scan_audio` now appends a warning when spectral-centroid
  computation fails (previously silent)

### 6. `moodify-core-package/src/moodify/v01_delivery.py` (3E → 0E)
- 3 empty exception handlers (`_git_hash`, `_git_branch`, `_installed_packages`) now log at
  debug level instead of silently swallowing
- **Authorized behavior changes:** none

### 7. `moodify_runtime/cli.py` (3E → 0E)
- Split `main` (472 lines, complexity 101) into domain dispatch: `_handle_core_commands` /
  `_handle_operator_commands` / `_handle_studio_commands` / `_handle_scheduler_commands` /
  `_handle_calibration_commands` / `_handle_craft_commands` / `_handle_runtime_commands` /
  `_handle_tidal_commands` / `_handle_pdf_commands` / `_handle_data_loop_commands`
- Split `build_parser` (342 lines) into 10 `_add_*_commands(sub)` registration functions
- CLI surface, flags, defaults and exit codes unchanged (verified by test_cli.py + operator tests)

### 8. `moodify-bridge/src/moodify_bridge/services.py` (partial)
- `_cleanup_promotion_marker` empty exception → `logger.warning` (added module logger)
- Fixed PEP 695 generic syntax in `serialization.py:read_model` (`def read_model[T: BaseModel]`
  is Python 3.12+; downgraded to `TypeVar` so the package imports on Python 3.11)
- **BLOCKED**: deeper splitting of `promote_rule_atomic` / `ppe_run` / `evaluate_gates` /
  `refine_prepare` requires a runnable bridge test environment (duckdb/pyarrow/typer not
  installed; pip install interrupted by user). See UNRESOLVED.md.

## Scaffolding installed (per pack manifest)

- `.moodify/temporal_texture.toml` — config; `.venv-basic-pitch` added to exclude_dirs
  (project-specific venv name); workspace/third-party copy dirs excluded as scope correction
- `docs/engineering/TEMPORAL_TEXTURE_POLICY.md`, `ADR_TEMPLATE.md`, `MODULE_CONTRACT_TEMPLATE.md`
- `tools/temporal_texture/temporal_texture_audit.py`, `temporal_texture_guard.py`
- `tests/temporal_texture/test_temporal_texture_audit.py`
- `.github/workflows/moodify-temporal-texture.yml` (optional CI)
- `artifacts/temporal_texture/` evidence package

## Test assets added

- `moodify-core-package/tests/orchestration/test_workflow_engine_texture.py` (11 tests)
- `moodify_runtime/tests/test_craft_texture.py` (50 tests)
- `moodify_runtime/tests/test_runner_texture.py` (8 tests)

## Baseline delta (core scope)

| Metric | Before | After | Delta |
|---|---|---|---|
| Files scanned | 335 (tracked HEAD) | 566 (working tree) | scope differs* |
| Findings | 1375 | 1984 | +609 (new test files + untracked files) |
| Errors | 147 | 166 | +19 (all attributable to scope, see VERIFICATION) |
| Resolved findings (guard) | — | 105 | −105 |

*Before baseline was audited from a git worktree at HEAD (tracked files only); after reflects the
full working tree including new characterization tests and previously untracked modules. Guard
false positives from line-shift fingerprints are documented in regression.md.
