# Temporal Texture Wave 1 — UNRESOLVED

Task: DSK-MFY-TEMPORAL-TEXTURE-001 · 2026-08-04

## Blocked by environment / authority

### 1. `moodify-bridge` deep refactor — BLOCKED_BY_HUMAN_AUTHORITY
`promote_rule_atomic` (136 lines), `evaluate_gates` (complexity 25), `ppe_run` (143 lines),
`refine_prepare` (192 lines, complexity 26), `_build_manifest` (11 params) still carry
error-level findings. Splitting them without a runnable test environment violates the
task's "protect behavior before structure" rule. Required first: install duckdb/pyarrow/typer
(attempt was interrupted), then run `moodify-bridge/tests` to green, then refactor.
Only `_cleanup_promotion_marker` (empty exception) and the PEP 695 syntax fix were applied.

### 2. `moodify_runtime/operator_console.py:decide_candidate_gate` — 12 params (TT-PARAMETERS error)
Public API used by build_operator_detail_from_run and CLI. Changing the signature requires a
migration plan. Candidate: `GateInputs` dataclass + thin wrapper preserving the old signature.

### 3. `moodify-core-package/src/moodify/v01_pipeline.py:process_audio` — 179 lines (TT-FUNCTION-LENGTH error)
Deliberately kept: it is the only v0.1.0-mainline orchestration file and the function is a
sequential stage conductor. Splitting requires introducing a state object across 7 stages;
deferred as a design decision (would benefit from the PipelineContext pattern used in
workflow_engine).

## Pre-existing bugs discovered (frozen, not fixed)

### 4. `moodify_runtime/craft_processes.py:_write_wav` — stereo flattening
`out.flatten()` discards channels; `setnchannels(1 if out.ndim == 1 else nch)` always writes
mono. `stereo_width_control` / `center_focus` therefore emit interleaved garbage as mono.
Characterization tests freeze this as current behavior. Fixing changes audio output semantics
and needs product authority (and probably a delivery migration note).

### 5. `center_focus` mono input (resolved as authorized change)
Previously crashed with `NameError: name 'metrics' is not defined`; now returns explicit
failure "center_focus requires stereo input". Recorded here because it changes observable
failure text.

## Process notes

### 6. Baseline scope asymmetry
Before baseline was generated from a git worktree at HEAD (tracked files only) because the
working tree contains large untracked trees (moodify-bridge/, experiments/, docs/, ...) that
were not part of the refactor. The after audit covers the full working tree. Comparing the two
reports therefore shows scope artifacts (new files' findings) alongside genuine improvements.
For per-module truth, see the per-file scans in CHANGELOG.md.

### 7. Auditor fingerprint limitation
TT-BROAD-EXCEPTION / TT-EMPTY-EXCEPTION fingerprints embed line numbers, so any line shift
(e.g. adding a module logger) re-attributes pre-existing findings as "new". Consider a
line-independent message key for these rules in a future auditor version.

### 8. `ruff` baseline (360 pre-existing errors, mostly F401)
Not addressed in wave 1; F401 unused-import cleanup in refactored modules is recommended as
a cheap follow-up (partially achieved implicitly by the CLI domain split).

## Next-wave candidates (ranked)

1. `moodify-bridge/services.py` (after test env is green)
2. `moodify-core-package/src/moodify/diagnosis/engine.py` + `auditory/decode.py` empty handlers
3. `moodify_runtime/pdf_ct_builder.py` (5E, debt markers)
4. `moodify-core-package/src/moodify/physics/*` experiments modules
5. Kotlin-side audit (Android app) — requires extending the auditor or a separate tool
