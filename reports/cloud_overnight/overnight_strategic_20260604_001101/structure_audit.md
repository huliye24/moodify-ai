# Moodify Overnight Structure Audit

- Source files: 146
- Total source lines: 30823
- Files >300 lines: 36
- Files >800 lines: 4

## Top Long Files

| Rank | Lines | Path |
|---:|---:|---|
| 1 | 970 | `moodify-core-package/src/moodify/physics/experiments_2.py` |
| 2 | 862 | `scripts/v01_inspector.py` |
| 3 | 850 | `moodify-core-package/src/moodify/orchestration/workflow_engine.py` |
| 4 | 809 | `workers/night_worker.py` |
| 5 | 760 | `moodify-core-package/src/moodify/diagnosis/engine.py` |
| 6 | 709 | `workers/mrs_metrics.py` |
| 7 | 695 | `moodify-core-package/src/moodify/knowledge/emotion_targets.py` |
| 8 | 686 | `night/workers/cloud_night_worker.py` |
| 9 | 667 | `moodify-core-package/src/moodify/physics/experiments.py` |
| 10 | 663 | `moodify-core-package/src/moodify/evaluation/judges.py` |
| 11 | 632 | `moodify-core-package/src/moodify/optimizer/search.py` |
| 12 | 627 | `workers/mrs_open_benchmark_v03.py` |
| 13 | 554 | `moodify-core-package/src/moodify/data_types.py` |
| 14 | 517 | `workers/mrs_formula_v02.py` |
| 15 | 500 | `moodify-core-package/src/moodify/physics/reliable_runner.py` |
| 16 | 489 | `moodify-core-package/src/moodify/cli.py` |
| 17 | 472 | `scripts/v01_aggregate_treatment_records.py` |
| 18 | 471 | `moodify-core-package/src/moodify/evaluation/batch.py` |
| 19 | 457 | `moodify-core-package/src/moodify/physics/experiments_3_engineering.py` |
| 20 | 451 | `moodify-core-package/src/moodify/reality_metrics.py` |
| 21 | 441 | `workers/report_builder.py` |
| 22 | 412 | `scripts/mrs_validate_five_experiments.py` |
| 23 | 405 | `moodify-core-package/src/moodify/diagnosis/defect_classifier.py` |
| 24 | 389 | `moodify-core-package/src/moodify/knowledge/craft_chains.py` |
| 25 | 378 | `moodify-core-package/src/moodify/diagnosis/metrics.py` |
| 26 | 378 | `moodify-core-package/src/moodify/processing/operators.py` |
| 27 | 344 | `moodify_runtime/utils.py` |
| 28 | 344 | `night/moodify_daily_run_system/moodify_runtime/utils.py` |
| 29 | 343 | `moodify-core-package/src/moodify/calibration/experiment.py` |
| 30 | 327 | `scripts/mt002_validate_mrs_matrix.py` |

## Strategic Priority

- Keep ruff and pytest green before new feature work.
- Split files over 800 lines first; they dominate X-CLP structure risk.
- Move runtime reports to MRS Open-first metrics and treat pseudo metrics as optional.
- Keep cloud runtime evidence reproducible by run_id and manifest path.
