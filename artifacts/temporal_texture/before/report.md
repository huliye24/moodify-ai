# Moodify Temporal Texture Audit

- Generated: `2026-08-04T05:38:35.611885+00:00`
- Repository: `C:\temp\moodify-before`
- Files scanned: **335**
- Findings: **1375**
- Errors: **147**
- Warnings: **809**
- Information: **419**
- Weighted pressure score: **2772**

> Findings are review signals. Business risk and behavioral authority must determine refactor priority.

## Top paths

| Path | Findings |
|---|---:|
| `scripts/gen_mhp_629_736.py` | 125 |
| `moodify_runtime/pdf_ct_builder.py` | 44 |
| `moodify_runtime/runner.py` | 30 |
| `moodify-core-package/src/moodify/orchestration/workflow_engine.py` | 28 |
| `moodify_runtime/operator_console.py` | 28 |
| `scripts/mrs_validate_five_experiments.py` | 25 |
| `moodify-core-package/src/moodify/knowledge/craft_chains.py` | 24 |
| `moodify-core-package/src/moodify/cli_v2/main.py` | 22 |
| `moodify-core-package/src/moodify/physics/experiments.py` | 22 |
| `moodify_runtime/pdf_report.py` | 19 |
| `moodify_runtime/craft_processes.py` | 18 |
| `moodify-core-package/src/moodify/api/routes/workspace_projects.py` | 17 |
| `moodify-core-package/src/moodify/physics/experiments_2.py` | 17 |
| `scripts/mt002_validate_mrs_matrix.py` | 17 |
| `moodify-core-package/src/moodify/v01_pipeline.py` | 16 |
| `moodify_runtime/tests/test_pdf_ct_builder.py` | 16 |
| `moodify-core-package/src/moodify/evaluation/judges.py` | 15 |
| `moodify-core-package/src/moodify/cli.py` | 14 |
| `moodify-core-package/src/moodify/diagnosis/engine.py` | 13 |
| `moodify-core-package/src/moodify/physics/batch_runner.py` | 13 |
| `moodify_runtime/tests/test_operator_console.py` | 13 |
| `moodify-core-package/src/moodify/storage/workspace_store.py` | 12 |
| `moodify_runtime/tests/test_utils.py` | 12 |
| `moodify_runtime/utils.py` | 12 |
| `moodify-core-package/src/moodify/physics/experiments_3_engineering.py` | 11 |

## Findings

| Severity | Rule | Location | Symbol | Message |
|---|---|---|---|---|
| ERROR | `TT-COMPLEXITY` | `cloud_status.py:60` | `parse_reports` | Function complexity proxy is 26; branch pressure may hide decisions. |
| ERROR | `TT-NESTING` | `cloud_status.py:60` | `parse_reports` | Maximum nesting depth is 9; failure and decision paths are compressed. |
| ERROR | `TT-EMPTY-EXCEPTION` | `cloud_status.py:152` | `parse_reports` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/scripts/generate_calibration_versions.py:88` | `generate_versions` | Empty exception handler hides failure evidence. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/api/main.py:257` | `process` | Function spans 134 lines; review responsibility boundaries. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/api/main.py:389` | `process` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/audio_io.py:15` | `load_audio` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/comparison.py:80` | `compute_deltas` | Function complexity proxy is 25; branch pressure may hide decisions. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/auditory/decode.py:138` | `decode` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/auditory/decode.py:145` | `decode` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/judgment.py:37` | `evaluate_risk_flags` | Function complexity proxy is 34; branch pressure may hide decisions. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/judgment.py:132` | `evaluate_processing_plan` | Function complexity proxy is 22; branch pressure may hide decisions. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/manifests.py:32` | `write_scan_manifest` | Function has 10 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/metrics.py:129` | `compute_metrics` | Function spans 130 lines; review responsibility boundaries. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/reports.py:51` | `build_comparison_report` | Function has 14 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/service.py:261` | `register_candidate` | Function has 11 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/calibration/experiment.py:137` | `_calibrate_one` | Function spans 147 lines; review responsibility boundaries. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/calibration/online.py:84` | `load` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/calibration/server.py:81` | `_load_d_history` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/cli.py:241` | `cmd_batch` | Empty exception handler hides failure evidence. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/cli.py:613` | `main` | Function spans 249 lines; review responsibility boundaries. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/diagnosis/defect_classifier.py:299` | `_get_severity` | Function complexity proxy is 22; branch pressure may hide decisions. |
| ERROR | `TT-NESTING` | `moodify-core-package/src/moodify/diagnosis/defect_classifier.py:335` | `_assign_priorities` | Maximum nesting depth is 9; failure and decision paths are compressed. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/diagnosis/engine.py:144` | `_resample_fast` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/diagnosis/engine.py:153` | `_resample_fast` | Empty exception handler hides failure evidence. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/diagnosis/engine.py:633` | `_extract_emotion_optimized` | Function has 11 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/diagnosis/health_scorer.py:149` | `_get_ideal_vector` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/diagnosis/preprocessing.py:100` | `_resample` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/diagnosis/preprocessing.py:115` | `_resample` | Empty exception handler hides failure evidence. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/evaluation/judges.py:453` | `evaluate` | Function has 15 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/evaluation/judges.py:626` | `evaluate_processing` | Function has 14 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/icc.py:58` | `compute_icc` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/knowledge/emotion_targets.py:666` | `resolve_emotion_from_nl` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/knowledge/emotion_targets.py:685` | `resolve_emotion_from_nl` | Empty exception handler hides failure evidence. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/learning/run_learning_golden.py:40` | `main` | Function spans 146 lines; review responsibility boundaries. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/learning/run_real_song.py:44` | `main` | Function spans 151 lines; review responsibility boundaries. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/memory/history.py:89` | `load_all` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/optimizer/search.py:350` | `_proxy_te_base` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/optimizer/search.py:526` | `search_optimal_strengths` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:408` | `_finalize` | Function complexity proxy is 23; branch pressure may hide decisions. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:484` | `_build_result` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:547` | `_run_diagnosis` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:629` | `_run_spatial` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:639` | `_run_spatial` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/physics/b_matrix_parallel.py:113` | `identify_b_matrix` | Function complexity proxy is 21; branch pressure may hide decisions. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/physics/experiments_2.py:65` | `experiment_G` | Function complexity proxy is 21; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/experiments_2.py:65` | `experiment_G` | Function spans 140 lines; review responsibility boundaries. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/physics/experiments_2.py:300` | `experiment_I` | Function complexity proxy is 22; branch pressure may hide decisions. |
| ERROR | `TT-NESTING` | `moodify-core-package/src/moodify/physics/experiments_2.py:300` | `experiment_I` | Maximum nesting depth is 7; failure and decision paths are compressed. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/experiments_3_engineering.py:66` | `experiment_P` | Function spans 138 lines; review responsibility boundaries. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/physics/reliable_runner.py:153` | `load` | Empty exception handler hides failure evidence. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/processing/operators.py:46` | `apply_eq` | Function has 11 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/safety/test_projection.py:123` | `test_partial_params_pass_through` | Empty exception handler hides failure evidence. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/services/archive.py:48` | `archive_project` | Function spans 166 lines; review responsibility boundaries. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/services/archive.py:201` | `archive_project` | Empty exception handler hides failure evidence. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/services/designer.py:125` | `_build_plan` | Function spans 127 lines; review responsibility boundaries. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/services/dsp_worker.py:59` | `process_variant` | Function spans 124 lines; review responsibility boundaries. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/services/version_compare.py:91` | `_extract_audio_properties` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/services/version_compare.py:197` | `compare` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/v01_delivery.py:112` | `_git_hash` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/v01_delivery.py:125` | `_git_branch` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/v01_delivery.py:141` | `_installed_packages` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/v01_diagnostics.py:6` | `diagnose` | Function complexity proxy is 26; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/v01_pipeline.py:30` | `process_audio` | Function spans 179 lines; review responsibility boundaries. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/v01_pipeline.py:278` | `scan_audio` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/v01_pipeline.py:328` | `_quality_gate` | Empty exception handler hides failure evidence. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/v01_pipeline.py:412` | `_save_report` | Function has 11 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-NESTING` | `moodify-core-package/tests/baseline/check_regression.py:39` | `check_one` | Maximum nesting depth is 7; failure and decision paths are compressed. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/tests/baseline/run_baseline.py:91` | `test_fallback_search` | Empty exception handler hides failure evidence. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/tests/v2/test_e2e_golden_path.py:40` | `test_full_golden_path` | Function spans 255 lines; review responsibility boundaries. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/tests/v2/test_registered_sample_golden_path.py:72` | `test_registered_two_stem_song_reaches_verified_final_archive` | Function spans 136 lines; review responsibility boundaries. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify_runtime/cli.py:73` | `build_parser` | Function spans 342 lines; review responsibility boundaries. |
| ERROR | `TT-COMPLEXITY` | `moodify_runtime/cli.py:417` | `main` | Function complexity proxy is 101; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify_runtime/cli.py:417` | `main` | Function spans 472 lines; review responsibility boundaries. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/collectors/queue_collector.py:99` | `_build_signal` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/collectors/queue_collector.py:111` | `_build_signal` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `moodify_runtime/craft_memory.py:28` | `seed_craft_memory` | Function complexity proxy is 21; branch pressure may hide decisions. |
| ERROR | `TT-NESTING` | `moodify_runtime/craft_processes.py:60` | `validate_params` | Maximum nesting depth is 7; failure and decision paths are compressed. |
| ERROR | `TT-COMPLEXITY` | `moodify_runtime/craft_processes.py:685` | `execute_operation` | Function complexity proxy is 47; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify_runtime/craft_processes.py:685` | `execute_operation` | Function spans 335 lines; review responsibility boundaries. |
| ERROR | `TT-NESTING` | `moodify_runtime/craft_processes.py:685` | `execute_operation` | Maximum nesting depth is 23; failure and decision paths are compressed. |
| ERROR | `TT-COMPLEXITY` | `moodify_runtime/craft_proposals.py:109` | `promote_proposal_to_craft` | Function complexity proxy is 21; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify_runtime/craft_proposals.py:109` | `promote_proposal_to_craft` | Function spans 143 lines; review responsibility boundaries. |
| ERROR | `TT-COMPLEXITY` | `moodify_runtime/craft_selector.py:213` | `select_craft` | Function complexity proxy is 29; branch pressure may hide decisions. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/data_loop_runner.py:313` | `_infer_run_id` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/metrics.py:51` | `_init_mrs_open` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/metrics.py:108` | `_safe_float` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `moodify_runtime/operator_api.py:72` | `_get_app` | Function complexity proxy is 22; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify_runtime/operator_api.py:72` | `_get_app` | Function spans 491 lines; review responsibility boundaries. |
| ERROR | `TT-PARAMETERS` | `moodify_runtime/operator_console.py:288` | `decide_candidate_gate` | Function has 12 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify_runtime/operator_console.py:764` | `run_operator_job` | Function spans 179 lines; review responsibility boundaries. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify_runtime/operator_console.py:1006` | `build_operator_report_bundle` | Function spans 161 lines; review responsibility boundaries. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/operator_dashboard.py:179` | `submit_approval` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `moodify_runtime/over_dark.py:150` | `detect_over_dark` | Function complexity proxy is 24; branch pressure may hide decisions. |
| ERROR | `TT-COMPLEXITY` | `moodify_runtime/pdf_ct_builder.py:255` | `build_summary_diagnosis_page` | Function complexity proxy is 23; branch pressure may hide decisions. |
| ERROR | `TT-PARAMETERS` | `moodify_runtime/pdf_ct_builder.py:255` | `build_summary_diagnosis_page` | Function has 11 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-PARAMETERS` | `moodify_runtime/pdf_ct_builder.py:397` | `generate_single_scan_pdf` | Function has 10 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify_runtime/pdf_ct_builder.py:505` | `generate_comparison_pdf` | Function spans 125 lines; review responsibility boundaries. |
| ERROR | `TT-PARAMETERS` | `moodify_runtime/pdf_ct_builder.py:505` | `generate_comparison_pdf` | Function has 11 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/pdf_templates.py:132` | `_draw_header` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `moodify_runtime/report.py:34` | `generate_daily_report` | Function complexity proxy is 32; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify_runtime/report.py:34` | `generate_daily_report` | Function spans 215 lines; review responsibility boundaries. |
| ERROR | `TT-COMPLEXITY` | `moodify_runtime/runner.py:67` | `run_daily` | Function complexity proxy is 39; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify_runtime/runner.py:67` | `run_daily` | Function spans 307 lines; review responsibility boundaries. |
| ERROR | `TT-NESTING` | `moodify_runtime/runtime_failures.py:55` | `classify_failure` | Maximum nesting depth is 7; failure and decision paths are compressed. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/runtime_state.py:134` | `find_abandoned_tasks` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/studio.py:248` | `get_order_context` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/tests/test_cli.py:36` | `test_register_empty` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/tests/test_cli.py:39` | `test_register_empty` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/tests/test_cli.py:52` | `test_plan_noop` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/tests/test_cli.py:54` | `test_plan_noop` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/tests/test_craft_memory.py:28` | `test_no_runs_raises` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/tests/test_craft_memory.py:40` | `test_empty_runs_handled` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/tests/test_failure.py:29` | `test_no_runs_raises` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/tests/test_metrics.py:61` | `test_accepts_metrics_dict` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/tests/test_metrics.py:83` | `test_nonexistent_may_succeed` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/tests/test_planner.py:15` | `test_handles_no_runs` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/tests/test_runtime_state.py:24` | `test_valid_transition` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/tidal_cycle.py:78` | `_mem_free_gb` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `moodify_runtime/tidal_intelligence.py:327` | `generate_morning_brief` | Function complexity proxy is 33; branch pressure may hide decisions. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/tidal_operations.py:74` | `get_tidal_state` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/tidal_operations.py:89` | `get_tidal_state` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/tidal_operations.py:103` | `get_tidal_state` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/tidal_operations.py:111` | `get_tidal_state` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/tidal_operations.py:213` | `get_dashboard_snapshot` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/tidal_operations.py:223` | `get_dashboard_snapshot` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/tidal_operations.py:254` | `get_cycle_timeline` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/utils.py:311` | `_kill_process_group` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify_runtime/utils.py:347` | `release` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `scripts/analyze_calibration_results.py:84` | `analyze` | Function complexity proxy is 52; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `scripts/analyze_calibration_results.py:84` | `analyze` | Function spans 204 lines; review responsibility boundaries. |
| ERROR | `TT-PARAMETERS` | `scripts/gen_mhp_629_736.py:96` | `make_mhp` | Function has 11 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-COMPLEXITY` | `scripts/mt002_mrs_score_manifest.py:136` | `_summary` | Function complexity proxy is 25; branch pressure may hide decisions. |
| ERROR | `TT-COMPLEXITY` | `scripts/run_calibration_pipeline.py:83` | `run_pipeline` | Function complexity proxy is 36; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `scripts/run_calibration_pipeline.py:83` | `run_pipeline` | Function spans 197 lines; review responsibility boundaries. |
| ERROR | `TT-EMPTY-EXCEPTION` | `scripts/run_validation.py:90` | `collect_metrics` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `scripts/v01_aggregate_treatment_records.py:294` | `_build_summary_md_lines` | Function complexity proxy is 24; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `scripts/v01_aggregate_treatment_records.py:294` | `_build_summary_md_lines` | Function spans 186 lines; review responsibility boundaries. |
| ERROR | `TT-COMPLEXITY` | `scripts/v01_calibrate_presets.py:129` | `save_summary_md` | Function complexity proxy is 25; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `scripts/v01_inspector.py:317` | `write_markdown_report` | Function spans 210 lines; review responsibility boundaries. |
| ERROR | `TT-FUNCTION-LENGTH` | `scripts/v01_inspector.py:529` | `write_html_report` | Function spans 171 lines; review responsibility boundaries. |
| ERROR | `TT-FUNCTION-LENGTH` | `scripts/v01_inspector.py:725` | `main` | Function spans 134 lines; review responsibility boundaries. |
| ERROR | `TT-FUNCTION-LENGTH` | `workers/mrs_metrics.py:516` | `compute_mrs` | Function spans 176 lines; review responsibility boundaries. |
| ERROR | `TT-COMPLEXITY` | `workers/mrs_open_benchmark_v03.py:140` | `compute_d_real` | Function complexity proxy is 35; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `workers/mrs_open_benchmark_v03.py:140` | `compute_d_real` | Function spans 222 lines; review responsibility boundaries. |
| ERROR | `TT-FUNCTION-LENGTH` | `workers/report_builder.py:166` | `_write_night_summary_md` | Function spans 138 lines; review responsibility boundaries. |
| ERROR | `TT-EMPTY-EXCEPTION` | `workers/resource_guard.py:261` | `_get_output_dir_size_gb` | Empty exception handler hides failure evidence. |
| WARNING | `TT-COMPLEXITY` | `cloud_status.py:14` | `get_system` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `cloud_status.py:38` | `get_system` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `cloud_status.py:47` | `get_system` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `cloud_status.py:60` | `parse_reports` | Function spans 103 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `cloud_status.py:72` | `parse_reports` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `cloud_status.py:142` | `` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `cloud_status.py:152` | `parse_reports` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/calibration/analyze.py:64` | `compute_listener_reliability` | Function complexity proxy is 19; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/calibration/analyze.py:133` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/calibration/analyze.py:188` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/calibration/analyze.py:199` | `` | Line length is 141 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/run_agent_b.py:45` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/run_agent_b.py:140` | `` | Line length is 155 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/scripts/compute_proxy_scores.py:130` | `main` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/scripts/generate_calibration_versions.py:30` | `generate_versions` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/scripts/generate_calibration_versions.py:30` | `generate_versions` | Function spans 87 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/scripts/generate_calibration_versions.py:88` | `generate_versions` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/scripts/generate_calibration_versions.py:134` | `` | Line length is 141 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/scripts/prepare_ab_pairs.py:15` | `prepare_pairs` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/scripts/prepare_ab_pairs.py:65` | `` | Line length is 148 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/main.py:222` | `operator_create_job` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/main.py:230` | `operator_list_jobs` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/main.py:238` | `operator_job_detail` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/main.py:253` | `operator_attach_run` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/api/main.py:257` | `process` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/main.py:384` | `process` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/calibration.py:32` | `get_calibration_status` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/sessions.py:63` | `list_sessions` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/sessions.py:88` | `submit_feedback` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/v1.py:243` | `v1_pair` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/v1.py:519` | `_run_job_worker` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/api/routes/v1.py:552` | `v1_uploads_create` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/v1.py:610` | `v1_projects_create` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/v1.py:810` | `_wav_duration` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/workspace_projects.py:177` | `create_workspace_project` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/workspace_projects.py:196` | `get_workspace_project` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/workspace_projects.py:213` | `patch_workspace_project` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/workspace_projects.py:233` | `create_creative_brief` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/workspace_projects.py:256` | `patch_creative_brief` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/workspace_projects.py:264` | `list_project_threads` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/workspace_projects.py:292` | `create_audio_version` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/workspace_projects.py:300` | `list_audio_versions` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/workspace_projects.py:310` | `get_audio_version` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/workspace_projects.py:337` | `stream_audio_version` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/workspace_projects.py:367` | `branch_audio_version` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/workspace_projects.py:408` | `rollback_audio_version` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/api/routes/workspace_projects.py:428` | `approve_audio_version` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/api/routes/workspace_projects.py:428` | `approve_audio_version` | Function spans 66 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/workspace_projects.py:492` | `approve_audio_version` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/workspace_projects.py:507` | `compare_audio_versions` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/workspace_projects.py:523` | `list_comparable_versions` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/audio_io.py:15` | `load_audio` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/comparison.py:80` | `compute_deltas` | Function spans 69 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/auditory/decode.py:67` | `ffmpeg_version` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/decode.py:71` | `probe` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/errors.py:15` | `__init__` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/judgment.py:37` | `evaluate_risk_flags` | Function spans 93 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/auditory/judgment.py:132` | `` | Line length is 135 characters; expression may be compressed. |
| WARNING | `TT-NESTING` | `moodify-core-package/src/moodify/auditory/judgment.py:132` | `evaluate_processing_plan` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/metrics.py:129` | `compute_metrics` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/reports.py:11` | `build_contact_sheet` | Function has 9 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/run_golden.py:30` | `main` | Function spans 104 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/auditory/service.py:79` | `` | Line length is 155 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/service.py:119` | `scan_audio` | Function spans 111 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/auditory/service.py:160` | `scan_audio` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/service.py:318` | `compare_scans` | Function spans 104 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/service.py:318` | `compare_scans` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/auditory/spectrogram.py:62` | `_ffmpeg_version` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/stereo.py:14` | `compute_stereo_metrics` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/timeline.py:13` | `compute_timeline` | Function spans 71 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/calibration/experiment.py:51` | `run_calibration` | Function complexity proxy is 15; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/calibration/experiment.py:51` | `run_calibration` | Function spans 84 lines; review responsibility boundaries. |
| WARNING | `TT-NESTING` | `moodify-core-package/src/moodify/calibration/experiment.py:51` | `run_calibration` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/calibration/experiment.py:95` | `run_calibration` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/calibration/experiment.py:137` | `_calibrate_one` | Function complexity proxy is 18; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/calibration/experiment.py:211` | `_calibrate_one` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/calibration/experiment.py:257` | `_calibrate_one` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/calibration/listener.py:96` | `is_discriminable` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/calibration/listener.py:130` | `rank_versions` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/calibration/online.py:84` | `load` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/calibration/online.py:109` | `update` | Function spans 73 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/calibration/online.py:109` | `update` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/calibration/online.py:216` | `estimate_rho` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/calibration/online.py:274` | `update_calibration` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/calibration/server.py:81` | `_load_d_history` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/cli.py:68` | `cmd_legacy_analyze` | Function spans 76 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli.py:225` | `` | Line length is 169 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/cli.py:229` | `cmd_batch` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/cli.py:241` | `cmd_batch` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/cli.py:429` | `cmd_transcribe_stems` | Function complexity proxy is 19; branch pressure may hide decisions. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/cli.py:521` | `_cmd_daw` | Function complexity proxy is 20; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/cli.py:521` | `_cmd_daw` | Function spans 90 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli_v2/main.py:105` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli_v2/main.py:152` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/cli_v2/main.py:193` | `cmd_run_execute` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli_v2/main.py:214` | `` | Line length is 141 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli_v2/main.py:216` | `` | Line length is 138 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli_v2/main.py:226` | `` | Line length is 140 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/cli_v2/main.py:238` | `cmd_run_verify` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli_v2/main.py:251` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/cli_v2/main.py:350` | `cmd_case_execute` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/cli_v2/main.py:375` | `cmd_case_verify` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/cli_v2/main.py:399` | `cmd_case_package` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/cli_v2/main.py:646` | `build_parser` | Function spans 82 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli_v2/main.py:655` | `` | Line length is 155 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli_v2/main.py:657` | `` | Line length is 176 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli_v2/main.py:659` | `` | Line length is 246 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli_v2/main.py:660` | `` | Line length is 187 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli_v2/main.py:662` | `` | Line length is 202 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli_v2/main.py:663` | `` | Line length is 158 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli_v2/main.py:664` | `` | Line length is 158 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/cli_v2/main.py:775` | `main` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-NESTING` | `moodify-core-package/src/moodify/diagnosis/defect_classifier.py:273` | `_get_param_value` | Maximum nesting depth is 6; failure and decision paths are compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/diagnosis/defect_classifier.py:296` | `_get_param_value` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/diagnosis/defect_classifier.py:335` | `_assign_priorities` | Function complexity proxy is 17; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/diagnosis/engine.py:74` | `diagnose` | Function spans 61 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/diagnosis/engine.py:153` | `_resample_fast` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/diagnosis/engine.py:290` | `_compute_lra` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/diagnosis/engine.py:342` | `_compute_chorus_impact` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/diagnosis/engine.py:372` | `_compute_micro_dynamics` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/diagnosis/engine.py:384` | `_compute_micro_dynamics` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/diagnosis/engine.py:477` | `_compute_rt60_consist` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/diagnosis/engine.py:530` | `_extract_layers_optimized` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/diagnosis/engine.py:597` | `_compute_drum_detect` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/diagnosis/engine.py:623` | `_extract_emotion` | Function has 9 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/diagnosis/health_scorer.py:149` | `_get_ideal_vector` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/diagnosis/metrics.py:280` | `diagnose` | Function spans 87 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/diagnosis/preprocessing.py:115` | `_resample` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/diagnosis/quality_gate.py:80` | `gate_2_separation` | Function spans 78 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/diagnosis/quality_gate.py:162` | `gate_3_output` | Function spans 65 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/domain/audio_version.py:118` | `validate_version_invariants` | Function complexity proxy is 17; branch pressure may hide decisions. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/domain/thread.py:133` | `validate_thread_invariants` | Function complexity proxy is 15; branch pressure may hide decisions. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/domain/thread.py:164` | `transition_to` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/domain/workflow.py:88` | `validate_state` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/domain/workflow.py:110` | `_transition` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/evaluation/batch.py:108` | `run` | Function spans 68 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/evaluation/batch.py:144` | `run` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/evaluation/batch.py:177` | `_evaluate_single` | Function spans 74 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/evaluation/batch.py:257` | `_load_d_value` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/evaluation/batch.py:289` | `cmd_evaluate_run` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/evaluation/batch.py:364` | `cmd_evaluate_status` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/evaluation/batch.py:371` | `cmd_evaluate_single` | Function spans 101 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/evaluation/batch.py:394` | `cmd_evaluate_single` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/evaluation/batch.py:446` | `cmd_evaluate_single` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/evaluation/batch.py:460` | `` | Line length is 146 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/evaluation/judges.py:145` | `_init_client` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/evaluation/judges.py:152` | `evaluate` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/evaluation/judges.py:192` | `evaluate` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/evaluation/judges.py:231` | `evaluate` | Function complexity proxy is 15; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/evaluation/judges.py:231` | `evaluate` | Function spans 106 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/evaluation/judges.py:231` | `evaluate` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/evaluation/judges.py:260` | `evaluate` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/evaluation/judges.py:371` | `evaluate` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/evaluation/judges.py:412` | `evaluate` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/evaluation/judges.py:453` | `evaluate` | Function spans 91 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/evaluation/judges.py:572` | `_write_feedback` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/evaluation/judges.py:601` | `_write_feedback` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/evaluation/judges.py:609` | `_get_current_d` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/fingerprint.py:52` | `compute_thd` | Function spans 62 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/fingerprint.py:109` | `compute_thd` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/icc.py:76` | `_icc_anova_fallback` | Function spans 70 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:80` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:82` | `` | Line length is 153 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:84` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:118` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:120` | `` | Line length is 151 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:121` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:155` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:157` | `` | Line length is 149 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:159` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:192` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:194` | `` | Line length is 150 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:195` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:228` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:230` | `` | Line length is 151 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:232` | `` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:265` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:267` | `` | Line length is 151 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:269` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:302` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:304` | `` | Line length is 149 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:306` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:339` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:341` | `` | Line length is 151 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/knowledge/craft_chains.py:343` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/knowledge/emotion_targets.py:685` | `resolve_emotion_from_nl` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/knowledge/risk_model.py:55` | `assess` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/knowledge/risk_model.py:227` | `_generate_warnings` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/knowledge/risk_model.py:243` | `_generate_recommendations` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/learning/run_v2_v3_compare.py:28` | `main` | Function spans 89 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/learning/run_v2_v3_compare.py:100` | `` | Line length is 139 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/learning/run_v2_v3_compare.py:101` | `` | Line length is 142 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/learning/run_v2v3_spectra.py:40` | `main` | Function spans 76 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/learning/service.py:33` | `build_learning_record` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/llm/client.py:62` | `` | Line length is 138 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/llm/client.py:127` | `interpret_emotion` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/llm/client.py:130` | `narrate_diagnosis` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/llm/client.py:156` | `narrate_diagnosis` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/llm/client.py:226` | `_call` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/memory/history.py:89` | `load_all` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/memory/history.py:107` | `find_similar` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/mrs_adapter.py:39` | `_try_load_mrs_engine` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/mrs_adapter.py:45` | `score_for_quality_gate` | Function complexity proxy is 15; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/mrs_adapter.py:45` | `score_for_quality_gate` | Function spans 107 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/mrs_adapter.py:126` | `score_for_quality_gate` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/mrs_adapter.py:159` | `_mrs_proxy_inline` | Function spans 76 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/mrs_adapter.py:233` | `_mrs_proxy_inline` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/mrs_adapter.py:237` | `_compute_deltas_and_warnings` | Function complexity proxy is 17; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/mrs_adapter.py:237` | `_compute_deltas_and_warnings` | Function spans 102 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/mrs_adapter.py:253` | `_compute_deltas_and_warnings` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/optimizer/calibrate.py:148` | `calibrate` | Function spans 104 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/optimizer/calibrate.py:209` | `calibrate` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/optimizer/search.py:266` | `proxy_evaluate` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/optimizer/search.py:350` | `_proxy_te_base` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/optimizer/search.py:400` | `search_3d` | Function spans 71 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/optimizer/search.py:421` | `search_3d` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/optimizer/search.py:475` | `search_optimal_strengths` | Function spans 93 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/optimizer/search.py:475` | `search_optimal_strengths` | Function has 9 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/optimizer/search.py:496` | `search_optimal_strengths` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/optimizer/search.py:526` | `search_optimal_strengths` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:131` | `process` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:164` | `process` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:186` | `_resolve_emotion` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:247` | `_select_parameters` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:329` | `_try_rag` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:395` | `_process_candidates` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:408` | `_finalize` | Function spans 69 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:426` | `_finalize` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:450` | `_finalize` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:473` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:475` | `_finalize` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:484` | `_build_result` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:547` | `_run_diagnosis` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:571` | `_run_load_audio` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:600` | `_run_spectral_enhancement_multi` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:629` | `_run_spatial` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:639` | `_run_spatial` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:690` | `_export_wav` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:701` | `_run_mastering` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:728` | `_run_mastering` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:739` | `_run_mastering` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:747` | `_run_strength_search` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:773` | `_run_strength_search` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/physics/b_matrix_parallel.py:36` | `_process_batch` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-NESTING` | `moodify-core-package/src/moodify/physics/b_matrix_parallel.py:36` | `_process_batch` | Maximum nesting depth is 6; failure and decision paths are compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/physics/b_matrix_parallel.py:73` | `_process_batch` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/b_matrix_parallel.py:113` | `identify_b_matrix` | Function spans 106 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/physics/b_matrix_parallel.py:132` | `identify_b_matrix` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/b_matrix_parallel.py:221` | `main` | Function spans 72 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/physics/batch_runner.py:57` | `` | Line length is 134 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/physics/batch_runner.py:65` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/physics/batch_runner.py:66` | `` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/physics/batch_runner.py:67` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/physics/batch_runner.py:80` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/physics/batch_runner.py:88` | `` | Line length is 135 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/physics/batch_runner.py:91` | `` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/physics/batch_runner.py:92` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/physics/batch_runner.py:93` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/physics/batch_runner.py:147` | `run_single_experiment` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/physics/batch_runner.py:156` | `generate_report` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/batch_runner.py:156` | `generate_report` | Function spans 85 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/batch_runner.py:243` | `main` | Function spans 61 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/experiments.py:64` | `experiment_D` | Function spans 66 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/experiments.py:202` | `experiment_F` | Function spans 92 lines; review responsibility boundaries. |
| WARNING | `TT-NESTING` | `moodify-core-package/src/moodify/physics/experiments.py:202` | `experiment_F` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/physics/experiments.py:260` | `experiment_F` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/experiments.py:300` | `experiment_C` | Function spans 68 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/physics/experiments.py:332` | `experiment_C` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/physics/experiments.py:374` | `experiment_A` | Function complexity proxy is 15; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/experiments.py:374` | `experiment_A` | Function spans 105 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/physics/experiments.py:442` | `experiment_A` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/physics/experiments.py:485` | `experiment_B` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/experiments.py:485` | `experiment_B` | Function spans 95 lines; review responsibility boundaries. |
| WARNING | `TT-NESTING` | `moodify-core-package/src/moodify/physics/experiments.py:485` | `experiment_B` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/physics/experiments.py:596` | `main` | Function complexity proxy is 15; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/experiments.py:596` | `main` | Function spans 68 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/physics/experiments.py:631` | `main` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/physics/experiments_2.py:154` | `experiment_G` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/physics/experiments_2.py:234` | `experiment_H` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/experiments_2.py:300` | `experiment_I` | Function spans 91 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/experiments_2.py:397` | `experiment_J` | Function spans 82 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/experiments_2.py:485` | `experiment_K` | Function spans 81 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/experiments_2.py:572` | `experiment_L` | Function spans 81 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/physics/experiments_2.py:609` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/experiments_2.py:659` | `experiment_M` | Function spans 85 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/experiments_2.py:750` | `experiment_N` | Function spans 64 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/experiments_2.py:820` | `experiment_O` | Function spans 75 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/physics/experiments_2.py:944` | `main` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/physics/experiments_3_engineering.py:66` | `experiment_P` | Function complexity proxy is 20; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/physics/experiments_3_engineering.py:128` | `experiment_P` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/experiments_3_engineering.py:211` | `experiment_Q` | Function spans 98 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/physics/experiments_3_engineering.py:263` | `experiment_Q` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/physics/experiments_3_engineering.py:316` | `experiment_R` | Function complexity proxy is 17; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/experiments_3_engineering.py:316` | `experiment_R` | Function spans 94 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/physics/experiments_3_engineering.py:361` | `experiment_R` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/physics/experiments_3_engineering.py:436` | `main` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/physics/reliable_runner.py:65` | `preflight_check` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/physics/reliable_runner.py:80` | `preflight_check` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/reliable_runner.py:245` | `run_with_guard` | Function spans 92 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/physics/reliable_runner.py:292` | `` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/physics/reliable_runner.py:324` | `run_with_guard` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/physics/reliable_runner.py:341` | `run_suite` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/reliable_runner.py:341` | `run_suite` | Function spans 74 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/physics/reliable_runner.py:417` | `_generate_reliability_report` | Function spans 62 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/physics/reliable_runner.py:441` | `` | Line length is 163 characters; expression may be compressed. |
| WARNING | `TT-NESTING` | `moodify-core-package/src/moodify/processing/operators.py:25` | `_resolve_eq_params` | Maximum nesting depth is 6; failure and decision paths are compressed. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/processing/operators.py:25` | `_resolve_eq_params` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/processing/operators.py:86` | `_apply_eq_rbj` | Function has 9 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/processing/operators.py:103` | `_apply_eq_legacy_fft` | Function has 9 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/processing/operators.py:187` | `apply_compressor` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/processing/pedalboard_chain.py:136` | `process_with_fingerprint` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/processing/pedalboard_chain.py:232` | `_compute_transient_preservation` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/processing/pedalboard_chain.py:252` | `_compute_centroid_shift` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/processing/pedalboard_chain.py:292` | `_estimate_dynamic_contribution` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/processing/spectral_chain.py:210` | `_decompose` | Function spans 63 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/processing/spectral_chain.py:276` | `_compute_audit_metrics` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/processing/spectral_chain.py:310` | `_compute_audit_metrics` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/reality_metrics.py:432` | `compare_mrs` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/safety/projection.py:11` | `project` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/safety/projection.py:72` | `_get_rec_params` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/safety/test_projection.py:88` | `test_pass_through` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/safety/test_projection.py:123` | `test_partial_params_pass_through` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/services/analyst.py:66` | `run_diagnosis` | Function spans 68 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/services/analyst.py:119` | `run_diagnosis` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/services/archive.py:201` | `archive_project` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/services/archive.py:206` | `archive_project` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/services/archive.py:232` | `verify_archive` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/services/designer.py:35` | `generate_plan` | Function spans 74 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/services/designer.py:94` | `generate_plan` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/services/dsp_worker.py:59` | `process_variant` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/services/dsp_worker.py:168` | `process_variant` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/services/judge.py:21` | `_run_quality_checks` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/services/judge.py:21` | `_run_quality_checks` | Function spans 92 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/services/judge.py:68` | `_run_quality_checks` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/services/judge.py:108` | `_run_quality_checks` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/services/judge.py:134` | `judge_version` | Function spans 99 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/services/judge.py:221` | `judge_version` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/services/retry.py:45` | `handle_judge_rejection` | Function spans 115 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/services/version_compare.py:75` | `_compare_treatment_plans` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/services/version_compare.py:91` | `_extract_audio_properties` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/services/version_compare.py:113` | `compare` | Function spans 88 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/services/version_compare.py:197` | `compare` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/services/version_compare.py:238` | `list_comparable_versions` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/v01_delivery.py:33` | `_sha256_hex` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/v01_delivery.py:41` | `_file_size` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/v01_delivery.py:112` | `_git_hash` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/v01_delivery.py:125` | `_git_branch` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/v01_diagnostics.py:6` | `diagnose` | Function spans 78 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/v01_diagnostics.py:101` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/v01_diagnostics.py:105` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/v01_diagnostics.py:110` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/v01_diagnostics.py:111` | `` | Line length is 137 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/v01_diagnostics.py:112` | `` | Line length is 135 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/v01_diagnostics.py:132` | `to_problem_vector` | Function spans 93 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/v01_pipeline.py:199` | `process_audio` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/v01_pipeline.py:211` | `scan_audio` | Function complexity proxy is 18; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/v01_pipeline.py:211` | `scan_audio` | Function spans 79 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/v01_pipeline.py:278` | `scan_audio` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/v01_pipeline.py:287` | `scan_audio` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/v01_pipeline.py:328` | `_quality_gate` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/v01_pipeline.py:459` | `_save_pdf_report` | Function spans 101 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/v01_pipeline.py:459` | `_save_pdf_report` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/v01_pipeline.py:469` | `_save_pdf_report` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/v01_pipeline.py:562` | `_generate_delivery_artifacts` | Function spans 70 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/v01_pipeline.py:562` | `_generate_delivery_artifacts` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/tests/api/test_v1_demo_flow.py:81` | `test_full_flow_end_to_end` | Function spans 91 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/api/test_v1_demo_flow.py:203` | `` | Line length is 146 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/tests/baseline/check_regression.py:39` | `check_one` | Function complexity proxy is 17; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/tests/baseline/check_regression.py:81` | `main` | Function spans 61 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/tests/baseline/run_baseline.py:91` | `test_fallback_search` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/tests/baseline/run_baseline.py:110` | `test_fallback_preset` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/tests/baseline/run_baseline.py:214` | `run_all` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/tests/baseline/run_baseline.py:228` | `run_all` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/tests/test_api_operator.py:56` | `test_operator_api_create_list_detail_and_attach` | Function spans 64 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/tests/test_v01_pipeline.py:14` | `test_v01_pipeline_processes_mock_wav_end_to_end` | Function spans 72 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/v2/test_e2e_golden_path.py:159` | `` | Line length is 159 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/acoustic_ct.py:29` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/acoustic_ct.py:352` | `generate_ct_scan` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/acoustic_ct.py:396` | `generate_comparison_report` | Function spans 61 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/atomic_pair_writer.py:45` | `write` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/atomic_pair_writer.py:45` | `write` | Function spans 107 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/atomic_pair_writer.py:130` | `write` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/atomic_pair_writer.py:211` | `recover` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/atomic_pair_writer.py:211` | `recover` | Function spans 81 lines; review responsibility boundaries. |
| WARNING | `TT-NESTING` | `moodify_runtime/atomic_pair_writer.py:211` | `recover` | Maximum nesting depth is 6; failure and decision paths are compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/atomic_pair_writer.py:260` | `recover` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/cli.py:115` | `` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/cli.py:335` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/cli.py:341` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/cli.py:423` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/cli.py:538` | `` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/cli.py:870` | `` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/cloud_worker.py:49` | `is_expired` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/cloud_worker.py:136` | `` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/cloud_worker.py:137` | `_run_one_task` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/cloud_worker.py:138` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-NESTING` | `moodify_runtime/collectors/queue_collector.py:77` | `_build_signal` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/collectors/summary_collector.py:204` | `_collect_craft` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/craft_chain.py:177` | `execute` | Function complexity proxy is 17; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/craft_chain.py:177` | `execute` | Function spans 102 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/craft_memory.py:24` | `_to_float` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/craft_memory.py:28` | `seed_craft_memory` | Function spans 110 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/craft_memory.py:144` | `writeback_delivery_to_craft_record` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/craft_memory.py:144` | `writeback_delivery_to_craft_record` | Function spans 88 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/craft_presets.py:113` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/craft_presets.py:118` | `` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/craft_presets.py:129` | `` | Line length is 137 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/craft_presets.py:144` | `run_preset_experiment` | Function spans 92 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/craft_probes.py:23` | `detect_over_bright` | Function spans 62 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/craft_probes.py:150` | `detect_stereo_collapse` | Function spans 67 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/craft_probes.py:324` | `query_failure_cases` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/craft_processes.py:60` | `validate_params` | Function complexity proxy is 15; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/craft_processes.py:718` | `execute_operation` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/craft_processes.py:777` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/craft_processes.py:779` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/craft_processes.py:864` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/craft_processes.py:905` | `` | Line length is 136 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/craft_processes.py:929` | `` | Line length is 153 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/craft_processes.py:945` | `` | Line length is 139 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/craft_processes.py:952` | `` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/craft_processes.py:957` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/craft_processes.py:958` | `` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/craft_processes.py:972` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/craft_processes.py:978` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/craft_processes.py:1018` | `execute_operation` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/craft_proposals.py:143` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/craft_selector.py:213` | `select_craft` | Function spans 101 lines; review responsibility boundaries. |
| WARNING | `TT-NESTING` | `moodify_runtime/craft_selector.py:213` | `select_craft` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/data_loop_runner.py:77` | `__init__` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/data_loop_runner.py:237` | `_format_report` | Function spans 63 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/data_loop_runner.py:258` | `` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/data_loop_runner.py:260` | `` | Line length is 147 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/data_loop_runner.py:261` | `` | Line length is 140 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/data_loop_runner.py:262` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/data_loop_runner.py:313` | `_infer_run_id` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/data_loop_runner.py:317` | `_infer_run_id` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/failure.py:11` | `classify_error` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/historical_compatibility.py:106` | `load_historical_record` | Function spans 102 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/historical_compatibility.py:220` | `migrate_historical_record` | Function spans 103 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/listening.py:83` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/listening.py:92` | `create_blind_review_batch` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/listening.py:138` | `analyze_genre_sensitivity` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/listening.py:181` | `explain_mrs_score` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/listening.py:375` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/metrics.py:51` | `_init_mrs_open` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/metrics.py:56` | `_init_mrs_open` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/metrics.py:98` | `compute_mrs_open_v031` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/metrics.py:108` | `_safe_float` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/metrics.py:113` | `analyze_wav_stdlib` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/metrics.py:113` | `analyze_wav_stdlib` | Function spans 101 lines; review responsibility boundaries. |
| WARNING | `TT-NESTING` | `moodify_runtime/metrics.py:113` | `analyze_wav_stdlib` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/metrics.py:211` | `analyze_wav_stdlib` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/metrics.py:284` | `compare_before_after` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/mrs_calibration.py:105` | `submit_calibration_review` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/mrs_calibration.py:139` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/mrs_engine.py:74` | `score_audio` | Function spans 93 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/mrs_engine.py:111` | `score_audio` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/mrs_engine.py:120` | `score_audio` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/operator_api.py:154` | `_get_app` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/operator_api.py:154` | `api_compact` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/operator_api.py:279` | `api_deliver` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/operator_api.py:450` | `api_record_run` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/operator_console.py:212` | `create_operator_job` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/operator_console.py:274` | `_load_genre_thresholds` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/operator_console.py:288` | `decide_candidate_gate` | Function complexity proxy is 20; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/operator_console.py:288` | `decide_candidate_gate` | Function spans 73 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/operator_console.py:363` | `build_operator_detail_from_run` | Function spans 102 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/operator_console.py:363` | `build_operator_detail_from_run` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/operator_console.py:467` | `attach_run_report_to_job` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/operator_console.py:529` | `create_delivery_record` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/operator_console.py:529` | `create_delivery_record` | Function spans 103 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/operator_console.py:529` | `create_delivery_record` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/operator_console.py:662` | `plan_operator_runtime` | Function spans 73 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/operator_console.py:860` | `run_operator_job` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/operator_console.py:983` | `show_operator_runtime_plan` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/operator_console.py:1006` | `build_operator_report_bundle` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/operator_console.py:1086` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/operator_console.py:1258` | `check_storage_health` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/operator_dashboard.py:58` | `add_to_board` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/over_dark.py:150` | `detect_over_dark` | Function spans 111 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/pdf_assets.py:79` | `load_image` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/pdf_ct_builder.py:255` | `build_summary_diagnosis_page` | Function spans 82 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/pdf_ct_builder.py:397` | `generate_single_scan_pdf` | Function complexity proxy is 17; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/pdf_ct_builder.py:397` | `generate_single_scan_pdf` | Function spans 102 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/pdf_ct_builder.py:505` | `generate_comparison_pdf` | Function complexity proxy is 17; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/pdf_qa.py:77` | `_file_size_kb` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/pdf_qa.py:195` | `qa_text_extraction_smoke` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/pdf_qa.py:236` | `qa_image_render_smoke` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/pdf_report.py:268` | `create_comparison_page` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/pdf_templates.py:132` | `_draw_header` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/product_integration.py:67` | `build_learning_dashboard` | Function spans 103 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/product_integration.py:303` | `check_release_learning_gate` | Function spans 71 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/recommenders/operator_next_mhp.py:25` | `decide` | Function complexity proxy is 19; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/recommenders/operator_next_mhp.py:25` | `decide` | Function spans 92 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/report.py:23` | `_to_float` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/report.py:53` | `` | Line length is 138 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/report.py:54` | `` | Line length is 138 characters; expression may be compressed. |
| WARNING | `TT-NESTING` | `moodify_runtime/runner.py:67` | `run_daily` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/runner.py:67` | `run_daily` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/runner.py:164` | `run_daily` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/runner.py:233` | `run_daily` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/runner.py:366` | `run_daily` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/runtime_events.py:76` | `make_task_completed` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/runtime_events.py:89` | `make_task_failed` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/runtime_failures.py:55` | `classify_failure` | Function complexity proxy is 17; branch pressure may hide decisions. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/scheduler.py:143` | `record_compute_run` | Function has 9 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/studio.py:156` | `create_order` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/studio.py:211` | `` | Line length is 134 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/studio.py:212` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/studio.py:217` | `` | Line length is 133 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/supervisor.py:51` | `run_supervised` | Function complexity proxy is 20; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/supervisor.py:51` | `run_supervised` | Function spans 76 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/supervisor.py:118` | `run_supervised` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/tests/test_acoustic_ct.py:52` | `test_spectrogram` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/tests/test_acoustic_ct.py:58` | `test_frequency_balance` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/tests/test_acoustic_ct.py:64` | `test_waveform` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/tests/test_acoustic_ct.py:88` | `test_returns_report` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/tests/test_acoustic_ct.py:99` | `test_returns_report` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_api_jobs.py:162` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/tests/test_cli.py:39` | `test_register_empty` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/tests/test_cli.py:54` | `test_plan_noop` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_craft.py:100` | `` | Line length is 144 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_craft.py:112` | `` | Line length is 136 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_craft.py:113` | `` | Line length is 143 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_craft.py:133` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_craft.py:162` | `` | Line length is 138 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/tests/test_craft_memory.py:40` | `test_empty_runs_handled` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_edge_cases.py:289` | `` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/tests/test_full_stack_smoke.py:77` | `live_server` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/tests/test_full_stack_smoke.py:172` | `test_api_job_create_attach_deliver_cycle` | Function spans 96 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_listening.py:99` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_listening.py:100` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_listening.py:108` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_listening.py:109` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_listening.py:120` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_listening.py:121` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_listening.py:122` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/tests/test_metrics.py:61` | `test_accepts_metrics_dict` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_mt002_mrs_score_manifest.py:18` | `` | Line length is 154 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_mt002_mrs_score_manifest.py:19` | `` | Line length is 177 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_mt002_mrs_score_manifest.py:45` | `` | Line length is 136 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_mt002_mrs_score_manifest.py:46` | `` | Line length is 145 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_mt002_validate_mrs_matrix.py:9` | `` | Line length is 140 characters; expression may be compressed. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/tests/test_mt002_validate_mrs_matrix.py:9` | `_record` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/tests/test_operator_console.py:178` | `test_attach_run_report_to_job_builds_detail` | Function spans 79 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/tests/test_operator_console.py:322` | `test_create_delivery_record_for_approved_candidate` | Function spans 73 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/tests/test_operator_console.py:412` | `test_delivery_override_allows_reprocess` | Function spans 70 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/tests/test_operator_console.py:484` | `test_list_delivery_records` | Function spans 70 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/tests/test_operator_console.py:556` | `test_operator_deliver_cli` | Function spans 92 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_operator_job_runner.py:15` | `` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/tests/test_operator_report_bundle.py:20` | `test_build_report_bundle_from_attached_run` | Function spans 69 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/tests/test_pdf_ct_builder.py:41` | `test_spectrogram` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/tests/test_pdf_ct_builder.py:49` | `test_frequency_balance` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/tests/test_pdf_ct_builder.py:57` | `test_waveform` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/tests/test_pdf_ct_builder.py:67` | `test_summary` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/tests/test_pdf_ct_builder.py:79` | `test_single_scan` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/tests/test_pdf_ct_builder.py:89` | `test_comparison` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_real_audio.py:23` | `` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/tests/test_real_audio.py:57` | `test_full_pipeline_with_real_audio` | Function spans 75 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_runner.py:21` | `` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_scheduler.py:32` | `` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_studio_os_alpha.py:40` | `` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/tests/test_studio_os_alpha.py:43` | `test_studio_os_alpha_end_to_end` | Function spans 117 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/tidal_cycle.py:78` | `_mem_free_gb` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/tidal_cycle.py:253` | `_run_one_cycle` | Function spans 63 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tidal_cycle.py:319` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/tidal_cycle.py:337` | `run` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/tidal_intelligence.py:264` | `decide_gate` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/tidal_intelligence.py:327` | `generate_morning_brief` | Function spans 91 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tidal_intelligence.py:388` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/tidal_intelligence.py:437` | `anti_loop_check` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/tidal_intelligence.py:507` | `select_craft_operations` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/tidal_operations.py:56` | `get_tidal_state` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-NESTING` | `moodify_runtime/tidal_operations.py:56` | `get_tidal_state` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/tidal_operations.py:74` | `get_tidal_state` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/utils.py:80` | `check_disk_space` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/utils.py:96` | `cleanup_old_runs` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/utils.py:289` | `run_command` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/utils.py:347` | `release` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/velocity.py:102` | `list_worktrees` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/velocity.py:115` | `remove_worktree` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `scripts/add_seal_protocol.py:42` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/add_seal_protocol.py:191` | `` | Line length is 187 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `scripts/add_seal_protocol.py:228` | `main` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `scripts/aep_worker_protocol.py:37` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `scripts/aep_worker_protocol.py:60` | `validate_output` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-COMPLEXITY` | `scripts/aep_worker_protocol.py:138` | `cmd_select` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-NESTING` | `scripts/analyze_calibration_results.py:84` | `analyze` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/analyze_calibration_results.py:259` | `` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/analyze_calibration_results.py:260` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/analyze_calibration_results.py:264` | `` | Line length is 200 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `scripts/calibrate_pseudo_mrs.py:30` | `_safe_float` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `scripts/calibrate_pseudo_mrs.py:125` | `grid_search` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-COMPLEXITY` | `scripts/calibrate_pseudo_mrs.py:208` | `main` | Function complexity proxy is 17; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/calibrate_pseudo_mrs.py:208` | `main` | Function spans 83 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `scripts/calibrate_pseudo_mrs.py:240` | `` | Line length is 155 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/calibrate_pseudo_mrs.py:286` | `` | Line length is 142 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/data_loop_runbook.py:117` | `build_deepseek_tasks` | Function spans 71 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/freeze_mvp_baseline.py:26` | `freeze_baseline` | Function spans 89 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `scripts/freeze_mvp_baseline.py:86` | `freeze_baseline` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/gen_mhp_629_736.py:17` | `make_mhp_seal_section` | Function spans 77 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:181` | `` | Line length is 209 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:184` | `` | Line length is 200 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:187` | `` | Line length is 180 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:190` | `` | Line length is 183 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:193` | `` | Line length is 183 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:196` | `` | Line length is 172 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:202` | `` | Line length is 202 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:205` | `` | Line length is 189 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:208` | `` | Line length is 192 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:211` | `` | Line length is 193 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:214` | `` | Line length is 192 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:217` | `` | Line length is 159 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:223` | `` | Line length is 167 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:226` | `` | Line length is 179 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:229` | `` | Line length is 155 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:232` | `` | Line length is 164 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:235` | `` | Line length is 177 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:238` | `` | Line length is 165 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:246` | `` | Line length is 182 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:249` | `` | Line length is 186 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:252` | `` | Line length is 181 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:255` | `` | Line length is 174 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:258` | `` | Line length is 194 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:261` | `` | Line length is 143 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:267` | `` | Line length is 183 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:270` | `` | Line length is 177 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:273` | `` | Line length is 186 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:276` | `` | Line length is 189 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:279` | `` | Line length is 184 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:282` | `` | Line length is 149 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:288` | `` | Line length is 161 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:291` | `` | Line length is 182 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:294` | `` | Line length is 167 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:297` | `` | Line length is 184 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:300` | `` | Line length is 175 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:303` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:311` | `` | Line length is 170 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:314` | `` | Line length is 172 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:317` | `` | Line length is 166 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:320` | `` | Line length is 181 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:323` | `` | Line length is 166 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:326` | `` | Line length is 153 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:332` | `` | Line length is 169 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:335` | `` | Line length is 175 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:338` | `` | Line length is 159 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:341` | `` | Line length is 185 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:344` | `` | Line length is 171 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:347` | `` | Line length is 139 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:353` | `` | Line length is 182 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:356` | `` | Line length is 186 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:359` | `` | Line length is 166 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:362` | `` | Line length is 181 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:365` | `` | Line length is 169 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:368` | `` | Line length is 167 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:419` | `` | Line length is 188 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:422` | `` | Line length is 184 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:425` | `` | Line length is 174 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:428` | `` | Line length is 177 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:431` | `` | Line length is 165 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:434` | `` | Line length is 144 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:440` | `` | Line length is 185 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:443` | `` | Line length is 177 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:446` | `` | Line length is 176 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:449` | `` | Line length is 189 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:452` | `` | Line length is 174 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:455` | `` | Line length is 142 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:461` | `` | Line length is 170 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:464` | `` | Line length is 181 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:467` | `` | Line length is 159 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:470` | `` | Line length is 174 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:473` | `` | Line length is 192 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:476` | `` | Line length is 167 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:484` | `` | Line length is 169 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:487` | `` | Line length is 167 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:490` | `` | Line length is 183 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:493` | `` | Line length is 153 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:496` | `` | Line length is 173 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:499` | `` | Line length is 145 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:505` | `` | Line length is 187 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:508` | `` | Line length is 167 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:511` | `` | Line length is 158 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:514` | `` | Line length is 159 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:517` | `` | Line length is 163 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:520` | `` | Line length is 149 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:526` | `` | Line length is 163 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:529` | `` | Line length is 168 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:532` | `` | Line length is 169 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:535` | `` | Line length is 150 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:538` | `` | Line length is 150 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:541` | `` | Line length is 147 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:549` | `` | Line length is 178 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:552` | `` | Line length is 192 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:555` | `` | Line length is 173 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:558` | `` | Line length is 181 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:561` | `` | Line length is 163 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:564` | `` | Line length is 138 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:570` | `` | Line length is 160 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:573` | `` | Line length is 171 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:576` | `` | Line length is 172 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:579` | `` | Line length is 163 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:582` | `` | Line length is 168 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:585` | `` | Line length is 157 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:591` | `` | Line length is 168 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:594` | `` | Line length is 164 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:597` | `` | Line length is 160 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:600` | `` | Line length is 180 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:603` | `` | Line length is 167 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/gen_mhp_629_736.py:606` | `` | Line length is 171 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `scripts/map_judge_check.py:87` | `check_scope` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `scripts/map_judge_check.py:167` | `check_runtime` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-NESTING` | `scripts/map_judge_check.py:313` | `main` | Maximum nesting depth is 6; failure and decision paths are compressed. |
| WARNING | `TT-PARAMETERS` | `scripts/mrs_validate_five_experiments.py:49` | `log_result` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/mrs_validate_five_experiments.py:66` | `experiment_1_spectrum` | Function spans 62 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mrs_validate_five_experiments.py:281` | `` | Line length is 148 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mrs_validate_five_experiments.py:323` | `` | Line length is 144 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `scripts/mrs_validate_five_experiments.py:332` | `main` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/mrs_validate_five_experiments.py:332` | `main` | Function spans 77 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `scripts/mrs_validate_five_experiments.py:371` | `main` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `scripts/mrs_validate_five_experiments.py:378` | `main` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `scripts/mrs_validate_five_experiments.py:385` | `main` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `scripts/mrs_validate_five_experiments.py:392` | `main` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `scripts/mrs_validate_five_experiments.py:399` | `main` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `scripts/mt002_mrs_score_manifest.py:56` | `_float_or_none` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `scripts/mt002_mrs_score_manifest.py:60` | `_record_from_row` | Function complexity proxy is 17; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_mrs_score_manifest.py:125` | `` | Line length is 235 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_mrs_score_manifest.py:218` | `` | Line length is 171 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_mrs_score_manifest.py:222` | `` | Line length is 149 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_mrs_score_manifest.py:223` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_mrs_score_manifest.py:226` | `` | Line length is 149 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_mrs_score_manifest.py:265` | `` | Line length is 205 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `scripts/mt002_validate_mrs_matrix.py:58` | `_number` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `scripts/mt002_validate_mrs_matrix.py:103` | `validate_monotonicity` | Function complexity proxy is 19; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_validate_mrs_matrix.py:122` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_validate_mrs_matrix.py:126` | `` | Line length is 140 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_validate_mrs_matrix.py:127` | `` | Line length is 147 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_validate_mrs_matrix.py:137` | `` | Line length is 149 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_validate_mrs_matrix.py:147` | `` | Line length is 136 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_validate_mrs_matrix.py:164` | `` | Line length is 135 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_validate_mrs_matrix.py:178` | `` | Line length is 227 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_validate_mrs_matrix.py:189` | `` | Line length is 171 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_validate_mrs_matrix.py:196` | `` | Line length is 148 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_validate_mrs_matrix.py:197` | `` | Line length is 160 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_validate_mrs_matrix.py:214` | `` | Line length is 150 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_validate_mrs_matrix.py:221` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_validate_mrs_matrix.py:223` | `` | Line length is 198 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_validate_mrs_matrix.py:313` | `` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/mt002_validate_mrs_matrix.py:315` | `` | Line length is 172 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `scripts/run_calibration_pipeline.py:79` | `process_one` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `scripts/run_calibration_pipeline.py:275` | `` | Line length is 141 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/run_validation.py:62` | `collect_metrics` | Function spans 64 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `scripts/run_validation.py:128` | `main` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/run_validation.py:128` | `main` | Function spans 117 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `scripts/run_validation.py:206` | `main` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `scripts/simulate_deepseek_outputs.py:32` | `` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/simulate_deepseek_outputs.py:41` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/simulate_deepseek_outputs.py:59` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/simulate_deepseek_outputs.py:68` | `` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/simulate_deepseek_outputs.py:77` | `` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/simulate_deepseek_outputs.py:78` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `scripts/v01_aggregate_treatment_records.py:79` | `load_records` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `scripts/v01_aggregate_treatment_records.py:134` | `compute_preset_stats` | Function complexity proxy is 17; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/v01_aggregate_treatment_records.py:134` | `compute_preset_stats` | Function spans 70 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/v01_aggregate_treatment_records.py:206` | `build_summary` | Function spans 68 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `scripts/v01_calibrate_presets.py:36` | `run_calibration` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/v01_calibrate_presets.py:36` | `run_calibration` | Function spans 79 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/v01_calibrate_presets.py:129` | `save_summary_md` | Function spans 101 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/v01_create_treatment_record.py:64` | `build_treatment_record` | Function spans 92 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `scripts/v01_inspector.py:151` | `compute_delta` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `scripts/v01_inspector.py:165` | `` | Line length is 134 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `scripts/v01_inspector.py:317` | `write_markdown_report` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `scripts/v01_inspector.py:629` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/v01_inspector.py:646` | `` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `scripts/v01_inspector.py:725` | `main` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/v01_update_treatment_feedback.py:85` | `main` | Function spans 85 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `scripts/validate_workspace_acceptance_sample.py:27` | `validate_manifest` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/validate_workspace_acceptance_sample.py:27` | `validate_manifest` | Function spans 61 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `workers/job_queue.py:133` | `_make_runner` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `workers/job_queue.py:133` | `runner` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `workers/mrs_formula_v02.py:67` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `workers/mrs_formula_v02.py:124` | `_lufs_estimate` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `workers/mrs_formula_v02.py:268` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `workers/mrs_formula_v02.py:293` | `` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `workers/mrs_formula_v02.py:296` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `workers/mrs_formula_v02.py:304` | `compute_mrs_abs` | Function spans 63 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `workers/mrs_formula_v02.py:312` | `compute_mrs_abs` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `workers/mrs_formula_v02.py:369` | `compute_overprocessing_risk` | Function complexity proxy is 15; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `workers/mrs_formula_v02.py:369` | `compute_overprocessing_risk` | Function spans 66 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `workers/mrs_metrics.py:551` | `compute_mrs` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-NESTING` | `workers/mrs_open_benchmark_v03.py:140` | `compute_d_real` | Maximum nesting depth is 6; failure and decision paths are compressed. |
| WARNING | `TT-LINE-LENGTH` | `workers/mrs_open_benchmark_v03.py:264` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `workers/mrs_open_benchmark_v03.py:335` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `workers/mrs_open_benchmark_v03.py:345` | `compute_d_real` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `workers/mrs_open_benchmark_v03.py:368` | `compute_mrs_open` | Function spans 65 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `workers/mrs_open_benchmark_v03.py:439` | `calibrate_dref` | Function spans 90 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `workers/mrs_open_benchmark_v03.py:535` | `verify_theoretical_properties` | Function complexity proxy is 15; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `workers/mrs_open_benchmark_v03.py:535` | `verify_theoretical_properties` | Function spans 76 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `workers/mrs_open_benchmark_v03.py:561` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `workers/night_worker.py:113` | `run` | Function spans 75 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `workers/night_worker.py:154` | `run` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `workers/night_worker.py:172` | `run` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `workers/night_worker.py:254` | `_stage_sweep` | Function spans 84 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `workers/night_worker.py:736` | `main` | Function spans 70 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `workers/report_builder.py:42` | `build_all` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `workers/report_builder.py:166` | `_write_night_summary_md` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `workers/resource_guard.py:220` | `_get_cpu_usage` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `workers/resource_guard.py:239` | `_get_memory_used_gb` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `workers/resource_guard.py:249` | `_get_free_disk_gb` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `workers/resource_guard.py:264` | `_get_output_dir_size_gb` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/api/main.py:20` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/api/main.py:295` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/api/routes/v1.py:125` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/calibration/listener.py:143` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/cli.py:468` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/cli.py:469` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/cli.py:503` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/cli.py:709` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/cli.py:754` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/cli_v2/main.py:14` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/cli_v2/main.py:72` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/learning/store.py:5` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/llm/client.py:206` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/llm/client.py:222` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/llm/client.py:227` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/mrs_adapter.py:28` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/physics/b_matrix_parallel.py:44` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/physics/b_matrix_parallel.py:59` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/physics/experiments.py:248` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/physics/experiments.py:249` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/physics/experiments.py:424` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/physics/experiments.py:425` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/physics/experiments.py:524` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/physics/experiments.py:525` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/physics/experiments.py:526` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/physics/experiments_2.py:127` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/physics/experiments_2.py:704` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/physics/experiments_3_engineering.py:49` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/physics/experiments_3_engineering.py:50` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reality_metrics.py:32` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reality_metrics.py:222` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reality_metrics.py:224` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reality_metrics.py:318` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reality_metrics.py:330` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reality_metrics.py:344` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reality_metrics.py:373` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/services/retry.py:169` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/storage/workspace_store.py:10` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/storage/workspace_store.py:115` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/storage/workspace_store.py:119` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/storage/workspace_store.py:121` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/storage/workspace_store.py:126` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/storage/workspace_store.py:128` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/storage/workspace_store.py:129` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/storage/workspace_store.py:372` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/storage/workspace_store.py:375` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/storage/workspace_store.py:381` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/storage/workspace_store.py:383` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/storage/workspace_store.py:384` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/v01_diagnostics.py:98` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/v01_pipeline.py:371` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/conftest.py:18` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_api_operator.py:39` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_api_operator.py:93` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_fallback.py:56` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_fallback.py:64` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/v2/test_e2e_golden_path.py:13` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/v2/test_e2e_golden_path.py:22` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/v2/test_failure_recovery.py:9` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/v2/test_failure_recovery.py:19` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/v2/test_failure_recovery.py:146` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/v2/test_failure_recovery.py:150` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/v2/test_failure_recovery.py:151` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/v2/test_failure_recovery.py:160` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/v2/test_workspace_store.py:199` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/cli.py:845` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/config.py:40` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/config.py:42` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/craft_chain.py:11` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/craft_chain.py:152` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/craft_chain.py:218` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/craft_chain.py:281` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/craft_presets.py:156` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/craft_presets.py:163` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/historical_compatibility.py:29` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/historical_compatibility.py:50` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/operator_console.py:399` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/operator_console.py:693` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/operator_console.py:702` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/operator_console.py:955` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/operator_console.py:975` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/operator_console.py:977` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/operator_console.py:980` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/operator_console.py:986` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/operator_console.py:987` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:32` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:34` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:106` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:110` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:112` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:118` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:119` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:121` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:130` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:146` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:158` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:179` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:180` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:187` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:210` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:222` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:225` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:231` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:246` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:256` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:274` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:276` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:429` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:446` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:450` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:454` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:459` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:534` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:551` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:556` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:561` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:566` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:571` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:576` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_ct_builder.py:586` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_report.py:26` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_report.py:28` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_report.py:152` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_report.py:169` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_report.py:182` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_report.py:196` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_report.py:197` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_report.py:199` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_report.py:283` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_report.py:285` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_report.py:288` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_report.py:292` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_report.py:295` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_report.py:300` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_report.py:327` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_report.py:329` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_report.py:334` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_report.py:341` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_templates.py:1` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_templates.py:3` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_templates.py:85` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/pdf_templates.py:89` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/planner.py:26` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/queue.py:57` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/recommenders/runtime_reliability.py:126` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:21` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:29` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:127` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:150` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:162` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:163` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:165` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:193` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:205` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:221` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:223` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:225` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:230` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:232` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:234` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:239` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:240` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:258` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:273` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:274` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:276` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:320` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:321` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runtime_events.py:90` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runtime_events.py:98` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runtime_failures.py:33` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runtime_failures.py:48` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runtime_failures.py:55` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runtime_failures.py:65` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runtime_failures.py:106` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runtime_failures.py:114` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runtime_failures.py:117` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runtime_failures.py:118` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runtime_failures.py:119` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/supervisor.py:29` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/supervisor.py:44` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/supervisor.py:87` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/supervisor.py:88` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/supervisor.py:108` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/supervisor.py:115` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/supervisor.py:121` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_acoustic_ct.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_acoustic_ct.py:33` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_acoustic_ct.py:85` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_acoustic_ct.py:97` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_api_contract.py:47` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_api_contract.py:114` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_api_contract.py:194` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_api_contract.py:201` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_api_contract.py:208` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_api_contract.py:274` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_api_jobs.py:63` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_api_jobs.py:197` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_api_jobs.py:234` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_api_jobs.py:276` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_api_jobs.py:347` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_atomic_pair_writer.py:10` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_atomic_pair_writer.py:798` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_cli.py:32` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_cli.py:33` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_cli.py:44` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_cli.py:45` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_cloud_worker.py:3` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_collectors.py:13` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_command_safety.py:5` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_command_safety.py:8` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_command_safety.py:10` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_command_safety.py:64` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_command_safety.py:83` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_command_safety.py:101` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_command_safety.py:110` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_command_safety.py:118` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_config.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_config.py:34` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_console_interaction.py:98` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_craft.py:3` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_craft.py:93` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_craft_chain_direct.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_craft_memory.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_craft_memory.py:23` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_craft_memory.py:32` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_craft_memory.py:46` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_craft_processes.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_craft_processes.py:119` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_craft_proposals.py:421` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_craft_proposals.py:559` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_craft_proposals.py:813` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_data_loop_integration.py:14` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_data_loop_integration.py:110` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_data_loop_integration.py:112` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_edge_cases.py:53` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_edge_cases.py:83` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_edge_cases.py:136` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_failure.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_failure.py:26` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_full_stack_smoke.py:201` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_full_stack_smoke.py:212` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_historical_compatibility.py:650` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_listening.py:3` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_metrics.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_metrics.py:42` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_metrics.py:72` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_metrics.py:89` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_metrics.py:93` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_metrics.py:99` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_mrs_calibration.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_mrs_calibration.py:15` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_mrs_engine.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_mrs_engine.py:78` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_mrs_engine.py:84` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_mt001_gate3_config.py:4` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_mt001_gate3_config.py:18` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_mt001_gate3_config.py:21` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_mt001_gate3_config.py:22` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_mt001_smoke_config.py:6` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_mt001_smoke_config.py:33` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_mt001_smoke_config.py:36` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_mt001_smoke_config.py:37` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_multi_job.py:68` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_multi_job.py:104` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_multi_job.py:135` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_multi_job.py:172` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_multi_job.py:218` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_operator_console.py:161` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_operator_console.py:204` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_operator_console.py:224` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_operator_console.py:281` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_operator_console.py:354` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_operator_console.py:443` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_operator_console.py:519` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_operator_console.py:581` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_operator_report_bundle.py:47` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_operator_report_bundle.py:118` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_operator_report_bundle.py:175` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_operator_report_bundle.py:223` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_over_dark.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_over_dark.py:20` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_over_dark.py:32` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_over_dark.py:39` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_ct_builder.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_ct_builder.py:10` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_ct_builder.py:27` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_ct_builder.py:37` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_ct_builder.py:45` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_ct_builder.py:53` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_ct_builder.py:73` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_ct_builder.py:74` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_ct_builder.py:83` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_ct_builder.py:84` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_report.py:1` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_report.py:8` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_report.py:28` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_report.py:48` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_report.py:53` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_report.py:54` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_templates.py:1` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_templates.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_templates.py:18` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_templates.py:20` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_pdf_templates.py:23` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_planner.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_planner.py:9` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_product_integration.py:13` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_queue.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_queue.py:10` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_real_audio.py:26` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_real_audio.py:33` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_real_audio.py:49` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_real_audio.py:50` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_registry.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_registry.py:20` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_registry.py:28` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_registry.py:38` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_report.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_report.py:31` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_report.py:39` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_report_runner.py:4` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_report_runner.py:21` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_report_runner.py:68` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runner.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runtime_events.py:7` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runtime_events.py:22` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runtime_failures.py:16` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runtime_failures.py:19` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runtime_state.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runtime_state.py:10` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runtime_supervisor.py:4` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runtime_supervisor.py:27` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runtime_supervisor.py:35` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runtime_supervisor.py:42` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runtime_supervisor.py:61` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runtime_supervisor.py:62` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runtime_supervisor.py:63` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runtime_supervisor.py:81` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runtime_supervisor.py:200` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runtime_supervisor.py:201` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_scheduler.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_scheduler.py:15` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_studio.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_studio.py:19` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_studio_os_alpha.py:102` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_tidal_core.py:3` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_tidal_core.py:67` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_tidal_core.py:75` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_tidal_core.py:83` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_tidal_core.py:91` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_tidal_core.py:96` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_tidal_core.py:103` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_tidal_core.py:110` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_tidal_cycle.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_tidal_cycle.py:42` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_tidal_cycle.py:49` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_tidal_cycle.py:57` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_tidal_cycle.py:64` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_tidal_cycle.py:69` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_tidal_cycle.py:76` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_tidal_cycle.py:83` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_tidal_operations.py:3` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_utils.py:2` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_utils.py:8` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_utils.py:18` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_utils.py:26` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_utils.py:29` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_utils.py:34` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_utils.py:40` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_utils.py:51` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_utils.py:56` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_utils.py:62` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_utils.py:68` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_utils.py:76` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_velocity.py:3` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tidal_cycle.py:132` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tidal_cycle.py:288` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/utils.py:135` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/utils.py:143` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/utils.py:170` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/utils.py:173` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/utils.py:246` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/utils.py:247` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/add_seal_protocol.py:19` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/gen_mhp_629_736.py:151` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/gen_mhp_629_736.py:156` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/gen_mhp_629_736.py:171` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/gen_mhp_629_736.py:196` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/gen_mhp_629_736.py:200` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/gen_mhp_629_736.py:203` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/gen_mhp_629_736.py:204` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/gen_mhp_629_736.py:205` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/gen_mhp_629_736.py:206` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/gen_mhp_629_736.py:209` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/gen_mhp_629_736.py:212` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/gen_mhp_629_736.py:215` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/gen_mhp_629_736.py:217` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/gen_mhp_629_736.py:246` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/gen_mhp_629_736.py:356` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/mrs_validate_five_experiments.py:10` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/mrs_validate_five_experiments.py:78` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/mrs_validate_five_experiments.py:143` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/mrs_validate_five_experiments.py:200` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/mrs_validate_five_experiments.py:241` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/mrs_validate_five_experiments.py:243` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/mrs_validate_five_experiments.py:245` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/mrs_validate_five_experiments.py:253` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/mrs_validate_five_experiments.py:259` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/mrs_validate_five_experiments.py:278` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/mrs_validate_five_experiments.py:279` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/mrs_validate_five_experiments.py:280` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/mrs_validate_five_experiments.py:281` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/mrs_validate_five_experiments.py:389` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/run_validation.py:55` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/v01_create_treatment_record.py:22` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/v01_create_treatment_record.py:36` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/v01_create_treatment_record.py:148` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/v01_create_treatment_record.py:149` | `` | Debt marker TEMP requires a reason and exit condition. |
