# Known Failures — Pre-existing (before wave-1 refactor)

Captured: 2026-08-04. Distinguishes pre-existing failures from any failures the refactor
might introduce. Any new failure after wave 1 must be treated as task-introduced until
proven otherwise.

## A. Root-collected full pytest suite — collection errors (pre-existing)

Running `python -m pytest -q` from the repository root fails at collection time:

- `moodify-bridge/tests/*` (10 modules): `ModuleNotFoundError: No module named 'moodify_bridge'`
  and `No module named 'typer'` — the bridge package is not installed in this environment
  (editable install absent). Pre-existing environment state, not a code failure.
- `science/Moodify_Spectral_Evidence_v0_1_Package/tests/test_spectral_evidence.py`:
  dependency/import issue in the science package environment.
- `补丁包/.../pack/tests/test_temporal_texture_audit.py`: pytest cannot collect a test module
  under a non-ASCII (Chinese) directory path on Windows (GBK console encoding). This test file
  passes when run directly via `python -m unittest discover -s tests/temporal_texture`
  (see task-verified note below).

Consequence: the repository's own CI (`ci.yml`) and the established MHP four-gate workflow
run tests per package, not from the root. The per-package runs are the authoritative baseline.

## B. Ruff lint — pre-existing debt (360 errors on core trees)

`ruff check moodify-core-package/src moodify_runtime tools` → exit 1, 360 errors
(statistics in `ruff-lint.txt`):

- F401 unused-import: 189 (dominant)
- E702 multiple-statements-on-one-line: 70
- F841 unused-variable: 35
- F541 f-string-missing-placeholders: 32
- E741 ambiguous-variable-name: 17
- E401 multiple-imports-on-one-line: 10
- F811 redefined-while-unused: 4
- E402 module-import-not-at-top: 3

These are pre-existing; wave 1 must not increase them, and may opportunistically fix
unused imports in the 8 selected modules (F401 is the cheapest win).

## C. Temporal-texture baseline itself (219 errors / 1885 warnings)

Not "failures" of the repository, but the debt the wave-1 refactor is tasked to reduce:

- 82 empty exception handlers (TT-EMPTY-EXCEPTION, error severity) — concentrated in
  workflow_engine.py (8), v01_delivery.py (3), v01_pipeline.py (2), diagnosis/* (4)
- 328 broad exception handlers (TT-BROAD-EXCEPTION, warning)
- 774 debt markers (TT-DEBT-MARKER: TODO/FIXME/HACK/TEMP/WORKAROUND)

## D. Test suite status at baseline (per-package, authoritative)

- `moodify-core-package`: `pytest -m v01` → **30 passed, 1 skipped** (green);
  full package suite → **726 passed, 1 skipped** (green).
- `moodify_runtime`: `python -m pytest moodify_runtime/tests` (from repo root) →
  **932 passed, 4 failed, 10 skipped**. The 4 failures are all `TestPhaseRunners`
  (test_tidal_core.py, test_tidal_cycle.py): `subprocess.run` → `FileNotFoundError
  [WinError 2]`. Cause: this machine's shell PATH is broken (Windows-style PATH not
  converted for bash), so the subprocess cannot find the CLI executable. Environment
  failure, not code failure.
- Audit tool's own tests: `unittest discover -s tests/temporal_texture` → **2 passed** (green).

### D-1. Run-location pitfall (documented for reproducibility)

Running `python -m pytest tests` from inside `moodify_runtime/` causes `import queue`
to resolve to `moodify_runtime/queue.py` (CWD precedes stdlib on sys.path), which then
fails with `ImportError: attempted relative import with no known parent package` inside
anyio. This produced 77 spurious failures on first attempt. Correct invocation is from
the repo root: `python -m pytest moodify_runtime/tests`. The runtime suite must be run
this way in this repository.

## E. Environment notes

- Python 3.11.9; ruff 0.15.15; pytest 9.0.3; LSM host (8 GB RAM, parallel=1).
- `.venv-basic-pitch` was added to `exclude_dirs` in `.moodify/temporal_texture.toml`
  because the pack's default config did not cover this project-specific venv name;
  without it the audit was flooded by third-party site-packages (22,106 findings).
  This is a configuration correction, not a threshold weakening.
