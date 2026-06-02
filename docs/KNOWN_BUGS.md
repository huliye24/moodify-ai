# Known Bugs

Last updated: 2026-06-02 (stabilization-sprint-001)

## Fixed Bugs

### Bug 1: _run_mastering output filename overwrite
- **Status**: FIXED (MHP-026 era)
- **Fix**: Added `version_suffix` parameter to `_run_mastering()`. Each candidate version gets unique filename via `_v{i}` suffix.
- **Files**: `orchestration/workflow_engine.py`

### Bug 2: DeepSeek LLM vector_bias calculated but discarded
- **Status**: FIXED (MHP-026 era)
- **Fix**: `vector_bias` threaded through `search_optimal_strengths()`, `proxy_evaluate()`, `compute_eds()`. Applied to ideal target vector before distance computation.
- **Files**: `optimizer/search.py`, `diagnosis/health_scorer.py`, `orchestration/workflow_engine.py`

### Bug 3: RAG eval path missing source count validation
- **Status**: FIXED (MHP-026 era)
- **Fix**: Added `_validate_rag_params()` static method that clamps LLM-recommended parameters to craft_chain min/max bounds, fills missing parameters, and clamps strength values to [0.05, 0.95].
- **Files**: `orchestration/workflow_engine.py`

### Bug 4: DefectClassifier duplicate instantiation
- **Status**: FIXED (MHP-026 era)
- **Fix**: `defects` list computed once in Phase 1 and passed through to `_run_strength_search()` and RAG path. `search_optimal_strengths()` only instantiates DefectClassifier when `defects=None`.
- **Files**: `optimizer/search.py`, `orchestration/workflow_engine.py`

## Known Issues (Not Yet Fixed)

### API /process legacy emotion compatibility
- **Severity**: Medium
- **Description**: API `/process` uses v01_pipeline, but legacy `emotion` parameter compatibility mapping may produce unexpected results for some inputs.
- **Recommendation**: Add integration tests for all emotion-to-preset mappings.

### Real audio regression coverage is limited
- **Severity**: Low
- **Description**: Only 3 test audio files in baseline suite. Coverage for edge cases (clipping, silence, mono, extreme dynamics) is missing.
- **Recommendation**: Expand test audio suite to 10+ files covering edge cases.

### Feedback coverage is low (33%)
- **Severity**: Low
- **Description**: Only 3 of 9 treatment records have completed human feedback.
- **Recommendation**: Continue MHP-026 treatment record collection.

### Hardcoded paths in physics modules
- **Severity**: Low
- **Description**: Some physics modules contained hardcoded paths to `/home/ubuntu/`. Migrated to `config.py` in stabilization-sprint-001.
- **Recommendation**: Done in this sprint.

## Bug Fix Protocol

1. Always create a new branch from main for fixes.
2. Add a test that reproduces the bug before fixing.
3. Fix with minimal change; do not refactor adjacent code.
4. Verify with `pytest -m v01` and full `pytest`.
5. Update this file.
