# Moodify Temporal Texture Audit

- Generated: `2026-08-09T07:57:24.108545+00:00`
- Repository: `E:\moodify`
- Files scanned: **157**
- Findings: **394**
- Errors: **57**
- Warnings: **288**
- Information: **49**
- Weighted pressure score: **910**

> Findings are review signals. Business risk and behavioral authority must determine refactor priority.

## Top paths

| Path | Findings |
|---|---:|
| `moodify-core-package/src/moodify/orchestration/workflow_engine.py` | 28 |
| `scripts/mrs_validate_five_experiments.py` | 25 |
| `moodify-core-package/src/moodify/knowledge/craft_chains.py` | 24 |
| `moodify-core-package/src/moodify/physics/experiments.py` | 22 |
| `moodify-core-package/src/moodify/physics/experiments_2.py` | 17 |
| `moodify-core-package/src/moodify/evaluation/judges.py` | 15 |
| `moodify-core-package/src/moodify/diagnosis/engine.py` | 13 |
| `moodify-core-package/src/moodify/physics/batch_runner.py` | 13 |
| `moodify-core-package/src/moodify/physics/experiments_3_engineering.py` | 11 |
| `cloud_status.py` | 10 |
| `moodify-core-package/src/moodify/evaluation/batch.py` | 10 |
| `moodify-core-package/src/moodify/optimizer/search.py` | 10 |
| `moodify-core-package/src/moodify/physics/reliable_runner.py` | 10 |
| `moodify-core-package/src/moodify/physics/b_matrix_parallel.py` | 9 |
| `scripts/v01_inspector.py` | 9 |
| `moodify-core-package/src/moodify/calibration/experiment.py` | 8 |
| `moodify-core-package/src/moodify/llm/client.py` | 8 |
| `moodify-core-package/src/moodify/reality_metrics.py` | 7 |
| `moodify-core-package/src/moodify/auditory/service.py` | 6 |
| `moodify-core-package/src/moodify/calibration/online.py` | 6 |
| `moodify-core-package/src/moodify/cli.py` | 6 |
| `scripts/v01_aggregate_treatment_records.py` | 6 |
| `moodify-core-package/scripts/generate_calibration_versions.py` | 5 |
| `moodify-core-package/src/moodify/auditory/judgment.py` | 5 |
| `moodify-core-package/src/moodify/diagnosis/defect_classifier.py` | 5 |

## Findings

| Severity | Rule | Location | Symbol | Message |
|---|---|---|---|---|
| ERROR | `TT-COMPLEXITY` | `cloud_status.py:60` | `parse_reports` | Function complexity proxy is 26; branch pressure may hide decisions. |
| ERROR | `TT-NESTING` | `cloud_status.py:60` | `parse_reports` | Maximum nesting depth is 9; failure and decision paths are compressed. |
| ERROR | `TT-EMPTY-EXCEPTION` | `cloud_status.py:152` | `parse_reports` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/scripts/generate_calibration_versions.py:88` | `generate_versions` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/audio_io.py:15` | `load_audio` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/comparison.py:80` | `compute_deltas` | Function complexity proxy is 25; branch pressure may hide decisions. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/judgment.py:37` | `evaluate_risk_flags` | Function complexity proxy is 35; branch pressure may hide decisions. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/judgment.py:191` | `evaluate_processing_plan` | Function complexity proxy is 22; branch pressure may hide decisions. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/manifests.py:32` | `write_scan_manifest` | Function has 10 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/metrics.py:129` | `compute_metrics` | Function spans 130 lines; review responsibility boundaries. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/reports.py:50` | `build_auditory_report` | Function has 11 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/reports.py:143` | `build_comparison_report` | Function has 14 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/service.py:265` | `register_candidate` | Function has 11 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/service.py:322` | `compare_scans` | Function spans 140 lines; review responsibility boundaries. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/calibration/experiment.py:137` | `_calibrate_one` | Function spans 147 lines; review responsibility boundaries. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/calibration/online.py:84` | `load` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/calibration/server.py:80` | `_load_d_history` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/cli.py:194` | `cmd_batch` | Empty exception handler hides failure evidence. |
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
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/processing/operators.py:40` | `apply_eq` | Function has 10 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/safety/test_projection.py:123` | `test_partial_params_pass_through` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/v01_diagnostics.py:6` | `diagnose` | Function complexity proxy is 26; branch pressure may hide decisions. |
| ERROR | `TT-NESTING` | `moodify-core-package/tests/baseline/check_regression.py:39` | `check_one` | Maximum nesting depth is 7; failure and decision paths are compressed. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/tests/baseline/run_baseline.py:91` | `test_fallback_search` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `scripts/v01_aggregate_treatment_records.py:258` | `write_summary_md` | Function complexity proxy is 23; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `scripts/v01_aggregate_treatment_records.py:258` | `write_summary_md` | Function spans 170 lines; review responsibility boundaries. |
| ERROR | `TT-COMPLEXITY` | `scripts/v01_calibrate_presets.py:129` | `save_summary_md` | Function complexity proxy is 25; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `scripts/v01_inspector.py:324` | `write_markdown_report` | Function spans 210 lines; review responsibility boundaries. |
| ERROR | `TT-FUNCTION-LENGTH` | `scripts/v01_inspector.py:536` | `write_html_report` | Function spans 171 lines; review responsibility boundaries. |
| ERROR | `TT-FUNCTION-LENGTH` | `scripts/v01_inspector.py:732` | `main` | Function spans 134 lines; review responsibility boundaries. |
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
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/calibration.py:32` | `get_calibration_status` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/sessions.py:63` | `list_sessions` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/sessions.py:88` | `submit_feedback` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/audio_io.py:15` | `load_audio` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/comparison.py:80` | `compute_deltas` | Function spans 69 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/auditory/decode.py:70` | `ffmpeg_version` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/decode.py:74` | `probe` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/errors.py:15` | `__init__` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/judgment.py:37` | `evaluate_risk_flags` | Function spans 93 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/auditory/judgment.py:191` | `` | Line length is 135 characters; expression may be compressed. |
| WARNING | `TT-NESTING` | `moodify-core-package/src/moodify/auditory/judgment.py:191` | `evaluate_processing_plan` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/metrics.py:129` | `compute_metrics` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/auditory/models.py:97` | `` | Line length is 172 characters; expression may be compressed. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/reports.py:103` | `build_contact_sheet` | Function has 9 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/run_golden.py:30` | `main` | Function spans 104 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/auditory/service.py:83` | `` | Line length is 155 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/service.py:123` | `scan_audio` | Function spans 111 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/auditory/service.py:164` | `scan_audio` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/service.py:322` | `compare_scans` | Function has 8 declared parameters; implicit context may need a named structure. |
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
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/calibration/server.py:80` | `_load_d_history` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/cli.py:21` | `cmd_legacy_analyze` | Function spans 76 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli.py:178` | `` | Line length is 169 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/cli.py:182` | `cmd_batch` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/cli.py:194` | `cmd_batch` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/cli.py:367` | `main` | Function spans 119 lines; review responsibility boundaries. |
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
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/llm/client.py:61` | `` | Line length is 138 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/llm/client.py:129` | `interpret_emotion` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/llm/client.py:132` | `narrate_diagnosis` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/llm/client.py:158` | `narrate_diagnosis` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/llm/client.py:228` | `_call` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/memory/history.py:89` | `load_all` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/memory/history.py:107` | `find_similar` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
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
| WARNING | `TT-NESTING` | `moodify-core-package/src/moodify/processing/operators.py:19` | `_resolve_eq_params` | Maximum nesting depth is 6; failure and decision paths are compressed. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/processing/operators.py:19` | `_resolve_eq_params` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/processing/operators.py:40` | `apply_eq` | Function spans 74 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/processing/operators.py:145` | `apply_compressor` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/processing/pedalboard_chain.py:136` | `process_with_fingerprint` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/processing/pedalboard_chain.py:232` | `_compute_transient_preservation` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/processing/pedalboard_chain.py:252` | `_compute_centroid_shift` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/processing/pedalboard_chain.py:292` | `_estimate_dynamic_contribution` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/release.py:38` | `analyze_to_case` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/release.py:38` | `analyze_to_case` | Function spans 112 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/release.py:141` | `analyze_to_case` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/safety/projection.py:11` | `project` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/safety/projection.py:72` | `_get_rec_params` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/safety/test_projection.py:88` | `test_pass_through` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/safety/test_projection.py:123` | `test_partial_params_pass_through` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/v01_diagnostics.py:6` | `diagnose` | Function spans 78 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/v01_pipeline.py:22` | `process_audio` | Function spans 62 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/v01_pipeline.py:77` | `process_audio` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/tests/baseline/check_regression.py:39` | `check_one` | Function complexity proxy is 17; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/tests/baseline/check_regression.py:81` | `main` | Function spans 61 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/tests/baseline/run_baseline.py:91` | `test_fallback_search` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/tests/baseline/run_baseline.py:110` | `test_fallback_preset` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/tests/baseline/run_baseline.py:214` | `run_all` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/tests/baseline/run_baseline.py:228` | `run_all` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/tests/test_mfy_1_0_representative.py:24` | `_tools_available` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
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
| WARNING | `TT-LINE-LENGTH` | `scripts/pr15_extraction_enrich.py:24` | `` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `scripts/v01_aggregate_treatment_records.py:45` | `load_records` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `scripts/v01_aggregate_treatment_records.py:100` | `compute_preset_stats` | Function complexity proxy is 17; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/v01_aggregate_treatment_records.py:100` | `compute_preset_stats` | Function spans 70 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/v01_aggregate_treatment_records.py:172` | `build_summary` | Function spans 66 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `scripts/v01_calibrate_presets.py:36` | `run_calibration` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/v01_calibrate_presets.py:36` | `run_calibration` | Function spans 79 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/v01_calibrate_presets.py:129` | `save_summary_md` | Function spans 101 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/v01_create_treatment_record.py:64` | `build_treatment_record` | Function spans 92 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `scripts/v01_inspector.py:158` | `compute_delta` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `scripts/v01_inspector.py:172` | `` | Line length is 134 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `scripts/v01_inspector.py:324` | `write_markdown_report` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `scripts/v01_inspector.py:636` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `scripts/v01_inspector.py:653` | `` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `scripts/v01_inspector.py:732` | `main` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/v01_update_treatment_feedback.py:85` | `main` | Function spans 85 lines; review responsibility boundaries. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/api/main.py:6` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/api/main.py:45` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/decode.py:123` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/decode.py:127` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/calibration/listener.py:143` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/llm/client.py:208` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/llm/client.py:224` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/llm/client.py:229` | `` | Debt marker TEMP requires a reason and exit condition. |
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
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reality_metrics.py:29` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reality_metrics.py:228` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reality_metrics.py:230` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reality_metrics.py:324` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reality_metrics.py:336` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reality_metrics.py:350` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reality_metrics.py:379` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/conftest.py:18` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_fallback.py:56` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_fallback.py:64` | `` | Debt marker TEMP requires a reason and exit condition. |
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
| INFO | `TT-DEBT-MARKER` | `scripts/v01_create_treatment_record.py:22` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/v01_create_treatment_record.py:36` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/v01_create_treatment_record.py:148` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/v01_create_treatment_record.py:149` | `` | Debt marker TEMP requires a reason and exit condition. |
