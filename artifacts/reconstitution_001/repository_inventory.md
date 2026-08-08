# Repository Inventory

This inventory combines the automated text/path audit with manual inspection of `origin/main` at `0b355e7`. Classification describes authority, not code quality.

## A. Canonical Core

- `moodify-core-package/src/moodify/v01_pipeline.py`: supported v0.1 orchestration path.
- `v01_analyzer.py`, `v01_diagnostics.py`, `v01_exporter.py`, `v01_presets.py`, and `v01_types.py`: narrow analysis, diagnosis, intervention, export, and contract modules.
- `audio_io.py`: local source loading used by the supported path.
- `moodify-core-package/tests/test_v01_*` and `tests/test_api_v01.py`: executable authority for the current mainline.

Verified shape: `Import -> Analyze -> Diagnose -> Process -> Export`.

## B. Production Runtime

- `moodify-core-package/src/moodify/api/`: current FastAPI surface for presets, health, and processing.
- `moodify-core-package/src/moodify/cli.py`: current CLI, containing both v0.1 entry points and explicitly legacy commands.
- `processing/pedalboard_chain.py`: intervention implementation used by v0.1.
- `.github/workflows/ci.yml`: current automated lint/test gate.

The production label applies only where these modules are exercised by the 109-test baseline. It does not validate every legacy command in `cli.py`.

## C. Application Layer

- Root `dashboard.html` and `cloud_status.py`: small operational/application artifacts; not the canonical product architecture.
- Large Android, frontend, player, workspace, and cloud systems live on divergent branches, principally PR #15 and PR #9. They are not current `main` authority.

## D. Research / Experimental

- `physics/`, `phys-lab/`, `reality_metrics.py`, `icc.py`, `conservation.py`, `fingerprint.py`, and `uncertainty.py`.
- `calibration/`, `optimizer/`, and `evaluation/` where they are not reached by the v0.1 mainline.
- `data/b_matrix/` research matrices and validation material.
- Treatment-record aggregation and calibration scripts.

These are valuable evidence and research sources, but their presence does not make their metrics production truth.

## E. Legacy / Historical

- `orchestration/workflow_engine.py`: older multi-phase `WorkflowOrchestrator` retained behind legacy CLI commands.
- `diagnosis/`, `knowledge/`, `memory/`, `safety/`, and parts of `processing/` used by the legacy orchestration path.
- Historical engineering and strategy documents under `docs/` that describe Moodify primarily as post-processing.

No legacy subsystem is deleted by this task.

## F. Unknown / Needs Human Decision

- Whether PR #15's Android/runtime/workspace systems should be reimplemented as narrow adapters onto the canonical core.
- Which single production-case state machine should be authoritative after convergence.
- Whether B-matrix, MRS/reality metrics, and calibration outputs have sufficient provenance to become canonical Measurement Records.
- Which historical frontend, player, and cloud branches should be archived after extracting reusable contracts.

## Automated Audit Signals

- Files classified heuristically: application 2, core/runtime 69, documentation 119, research/experimental 2, tests 18, unclassified 74.
- Positioning signals: canonical identity 21, auditory loop 4, discipline markers 24, legacy post-processing identity 6.
- Raw matches: `audit/positioning_matches.json`.
