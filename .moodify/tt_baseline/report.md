# Moodify Temporal Texture Audit

- Generated: `2026-08-20T09:40:25.482940+00:00`
- Repository: `E:\moodify\.codex_tmp\ci-baseline`
- Files scanned: **625**
- Findings: **1422**
- Errors: **92**
- Warnings: **835**
- Information: **495**
- Weighted pressure score: **2625**

> Findings are review signals. Business risk and behavioral authority must determine refactor priority.

## Top paths

| Path | Findings |
|---|---:|
| `moodify-core-package/src/moodify/data_plane/control.py` | 65 |
| `ops/ear_batch/derive_outputs.py` | 49 |
| `moodify-core-package/src/moodify/data_plane/pipeline.py` | 33 |
| `moodify-core-package/src/moodify/orchestration/workflow_engine.py` | 28 |
| `apps/music-web/app/page.tsx` | 27 |
| `apps/music-web/app/studio/page.tsx` | 26 |
| `scripts/mrs_validate_five_experiments.py` | 25 |
| `moodify-core-package/src/moodify/knowledge/craft_chains.py` | 24 |
| `moodify-core-package/src/moodify/physics/experiments.py` | 22 |
| `moodify-core-package/tests/auditory/test_ch02_phase1_evidence.py` | 18 |
| `moodify-core-package/src/moodify/physics/experiments_2.py` | 17 |
| `moodify-core-package/tests/test_pipeline.py` | 17 |
| `moodify-music-package/src/moodify_music/bff/main.py` | 17 |
| `moodify-core-package/src/moodify/evaluation/judges.py` | 15 |
| `moodify-core-package/src/moodify_experimental/mamse006/features.py` | 15 |
| `moodify-music-package/src/moodify_music/api/routes_playlists.py` | 15 |
| `moodify-music-package/src/moodify_music/api/routes_tracks.py` | 15 |
| `ops/ear_batch/ear_batch.py` | 15 |
| `apps/music-web/lib/music-client.ts` | 13 |
| `moodify-core-package/src/moodify/diagnosis/engine.py` | 13 |
| `moodify-core-package/src/moodify/physics/batch_runner.py` | 13 |
| `apps/music-web/app/api/v1/tracks/[id]/audio/route.ts` | 12 |
| `moodify-music-package/tests/test_data_plane_behavior.py` | 12 |
| `apps/music-web/app/design/page.tsx` | 11 |
| `moodify-core-package/src/moodify/auditory/events/engine.py` | 11 |

## Findings

| Severity | Rule | Location | Symbol | Message |
|---|---|---|---|---|
| ERROR | `TT-COMPLEXITY` | `cloud_status.py:60` | `parse_reports` | Function complexity proxy is 26; branch pressure may hide decisions. |
| ERROR | `TT-NESTING` | `cloud_status.py:60` | `parse_reports` | Maximum nesting depth is 9; failure and decision paths are compressed. |
| ERROR | `TT-EMPTY-EXCEPTION` | `cloud_status.py:152` | `parse_reports` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/scripts/generate_calibration_versions.py:88` | `generate_versions` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/audio_io.py:15` | `load_audio` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/comparison.py:80` | `compute_deltas` | Function complexity proxy is 25; branch pressure may hide decisions. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/evidence/resolver.py:34` | `assemble_judgment_evidence` | Function complexity proxy is 28; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/evidence/resolver.py:34` | `assemble_judgment_evidence` | Function spans 167 lines; review responsibility boundaries. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/judgment.py:37` | `evaluate_risk_flags` | Function complexity proxy is 41; branch pressure may hide decisions. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/judgment.py:215` | `evaluate_processing_plan` | Function complexity proxy is 22; branch pressure may hide decisions. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/lab/evaluate.py:27` | `evaluate_experiment` | Function complexity proxy is 23; branch pressure may hide decisions. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/manifests.py:32` | `write_scan_manifest` | Function has 10 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/metrics.py:67` | `compute_metrics` | Function spans 139 lines; review responsibility boundaries. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/reports.py:50` | `build_auditory_report` | Function has 11 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/reports.py:143` | `build_comparison_report` | Function has 14 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/service.py:265` | `register_candidate` | Function has 11 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/service.py:322` | `compare_scans` | Function spans 140 lines; review responsibility boundaries. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/authority/escalation.py:52` | `evaluate_scope` | Function complexity proxy is 23; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/calibration/experiment.py:137` | `_calibrate_one` | Function spans 147 lines; review responsibility boundaries. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/calibration/online.py:84` | `load` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/calibration/server.py:80` | `_load_d_history` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/cli.py:273` | `cmd_batch` | Empty exception handler hides failure evidence. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/cli.py:446` | `main` | Function spans 141 lines; review responsibility boundaries. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/data_factory/runner.py:82` | `run_production_case` | Function spans 122 lines; review responsibility boundaries. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/data_plane/control.py:133` | `_append_event` | Function has 12 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/data_plane/object_key.py:97` | `parse_object_key` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/data_plane/object_key.py:103` | `parse_object_key` | Empty exception handler hides failure evidence. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/data_plane/pipeline.py:184` | `__init__` | Function has 10 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/data_plane/repository.py:173` | `register_object` | Function has 19 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/data_plane/repository.py:222` | `register_evidence` | Function has 14 declared parameters; implicit context may need a named structure. |
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
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/reconstruction/pipeline.py:72` | `check_hard_gates` | Function complexity proxy is 21; branch pressure may hide decisions. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/reconstruction/pipeline.py:94` | `run_golden_pipeline` | Function complexity proxy is 22; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/reconstruction/pipeline.py:94` | `run_golden_pipeline` | Function spans 130 lines; review responsibility boundaries. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/reconstruction/pipeline.py:94` | `run_golden_pipeline` | Function has 12 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/reconstruction_factory/agreement.py:32` | `analyze_agreement` | Function complexity proxy is 24; branch pressure may hide decisions. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/reconstruction_job/resource_meter.py:28` | `note_memory` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/safety/test_projection.py:123` | `test_partial_params_pass_through` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/stems/client.py:117` | `_extract_detail` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/stems/service.py:143` | `refresh` | Function complexity proxy is 23; branch pressure may hide decisions. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify/stems/store.py:147` | `create` | Function has 11 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/stems/store.py:301` | `delete_source_file` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/stems/store.py:318` | `prune_old_sources` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/v01_diagnostics.py:6` | `diagnose` | Function complexity proxy is 26; branch pressure may hide decisions. |
| ERROR | `TT-PARAMETERS` | `moodify-core-package/src/moodify_experimental/mamse015/objects.py:188` | `_close_region` | Function has 10 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/tests/auditory/test_ch02_phase1_evidence.py:81` | `test_epistemic_rejects_unknown_state` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/tests/auditory/test_ch02_phase1_evidence.py:94` | `test_evidence_node_validates_epistemic_and_scale` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/tests/auditory/test_ch02_phase1_evidence.py:135` | `test_scale_taxonomy_bounded` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/tests/auditory/test_ch02_phase1_evidence.py:187` | `test_section_validation` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/tests/auditory/test_ch02_phase1_evidence.py:192` | `test_section_validation` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/tests/auditory/test_ch02_phase1_evidence.py:203` | `test_structure_context_rejects_overlaps` | Empty exception handler hides failure evidence. |
| ERROR | `TT-NESTING` | `moodify-core-package/tests/baseline/check_regression.py:40` | `check_one` | Maximum nesting depth is 7; failure and decision paths are compressed. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/tests/baseline/run_baseline.py:95` | `test_fallback_search` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/tests/reconstruction_job/test_store.py:74` | `test_unique_idempotency_constraint` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `moodify-music-package/src/moodify_music/api/routes_bridge.py:65` | `create_request` | Function complexity proxy is 25; branch pressure may hide decisions. |
| ERROR | `TT-COMPLEXITY` | `moodify-music-package/src/moodify_music/bff/main.py:356` | `upload_media` | Function complexity proxy is 21; branch pressure may hide decisions. |
| ERROR | `TT-NESTING` | `moodify-music-package/tests/test_architecture.py:34` | `test_music_never_imports_ear_internals` | Maximum nesting depth is 7; failure and decision paths are compressed. |
| ERROR | `TT-EMPTY-EXCEPTION` | `ops/e2e_runner.py:66` | `stage_live_read` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `scripts/v01_aggregate_treatment_records.py:258` | `write_summary_md` | Function complexity proxy is 23; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `scripts/v01_aggregate_treatment_records.py:258` | `write_summary_md` | Function spans 170 lines; review responsibility boundaries. |
| ERROR | `TT-COMPLEXITY` | `scripts/v01_calibrate_presets.py:129` | `save_summary_md` | Function complexity proxy is 25; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `scripts/v01_inspector.py:324` | `write_markdown_report` | Function spans 210 lines; review responsibility boundaries. |
| ERROR | `TT-FUNCTION-LENGTH` | `scripts/v01_inspector.py:536` | `write_html_report` | Function spans 171 lines; review responsibility boundaries. |
| ERROR | `TT-FUNCTION-LENGTH` | `scripts/v01_inspector.py:732` | `main` | Function spans 134 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `apps/ear-workbench/assets/workbench.js:39` | `` | Line length is 134 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/ear-workbench/assets/workbench.js:150` | `` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/ear-workbench/assets/workbench.js:167` | `` | Line length is 158 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/ear-workbench/assets/workbench.js:225` | `` | Line length is 162 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/ear-workbench/assets/workbench.js:234` | `` | Line length is 187 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/ear-workbench/assets/workbench.js:248` | `` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/ear-workbench/assets/workbench.js:284` | `` | Line length is 191 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/ear-workbench/check_workbench.mjs:17` | `` | Line length is 138 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/ear-workbench/check_workbench.mjs:28` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/ear-workbench/check_workbench.mjs:48` | `` | Line length is 138 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/ear-workbench/check_workbench.mjs:69` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/ear-workbench/check_workbench.mjs:72` | `` | Line length is 139 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/ear-workbench/check_workbench.mjs:122` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/creators/[handle]/route.ts:9` | `` | Line length is 168 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/creators/[handle]/route.ts:11` | `` | Line length is 277 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/creators/[handle]/route.ts:12` | `` | Line length is 163 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/me/creator/route.ts:19` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/me/creator/route.ts:27` | `` | Line length is 163 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/tracks/[id]/audio/route.ts:8` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/tracks/[id]/audio/route.ts:23` | `` | Line length is 139 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/tracks/[id]/audio/route.ts:27` | `` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/tracks/[id]/audio/route.ts:28` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/tracks/[id]/audio/route.ts:32` | `` | Line length is 178 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/tracks/[id]/audio/route.ts:34` | `` | Line length is 148 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/tracks/[id]/audio/route.ts:35` | `` | Line length is 267 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/tracks/[id]/audio/route.ts:37` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/tracks/[id]/audio/route.ts:46` | `` | Line length is 133 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/tracks/[id]/audio/route.ts:47` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/tracks/[id]/audio/route.ts:52` | `` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/tracks/[id]/audio/route.ts:54` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/tracks/[id]/publish/route.ts:13` | `` | Line length is 142 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/tracks/[id]/publish/route.ts:18` | `` | Line length is 155 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/tracks/[id]/route.ts:9` | `` | Line length is 263 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/tracks/[id]/route.ts:10` | `` | Line length is 160 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/tracks/[id]/route.ts:11` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/api/v1/tracks/route.ts:18` | `` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/console/page.tsx:116` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/console/page.tsx:118` | `` | Line length is 138 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/design/page.tsx:9` | `` | Line length is 133 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/design/page.tsx:26` | `` | Line length is 178 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/design/page.tsx:43` | `` | Line length is 132 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/design/page.tsx:46` | `` | Line length is 146 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/design/page.tsx:50` | `` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/design/page.tsx:56` | `` | Line length is 142 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/design/page.tsx:140` | `` | Line length is 199 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/design/page.tsx:166` | `` | Line length is 159 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/design/page.tsx:175` | `` | Line length is 158 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/design/page.tsx:177` | `` | Line length is 140 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/design/page.tsx:183` | `` | Line length is 138 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/drafts/page.tsx:34` | `` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/drafts/page.tsx:72` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/inbox/page.tsx:47` | `` | Line length is 163 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/library/page.tsx:52` | `` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/library/page.tsx:64` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/library/page.tsx:81` | `` | Line length is 141 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/offline/page.tsx:10` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:23` | `` | Line length is 167 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:24` | `` | Line length is 162 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:25` | `` | Line length is 162 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:26` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:27` | `` | Line length is 162 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:58` | `` | Line length is 224 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:80` | `` | Line length is 152 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:82` | `` | Line length is 148 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:141` | `` | Line length is 154 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:150` | `` | Line length is 132 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:153` | `` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:157` | `` | Line length is 157 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:160` | `` | Line length is 173 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:168` | `` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:169` | `` | Line length is 173 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:170` | `` | Line length is 214 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:172` | `` | Line length is 160 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:173` | `` | Line length is 157 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:179` | `` | Line length is 194 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:181` | `` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:184` | `` | Line length is 480 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:185` | `` | Line length is 294 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:189` | `` | Line length is 195 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:194` | `` | Line length is 301 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:197` | `` | Line length is 831 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:201` | `` | Line length is 334 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/page.tsx:202` | `` | Line length is 1245 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/playlists/page.tsx:95` | `` | Line length is 142 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/playlists/page.tsx:96` | `` | Line length is 135 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/playlists/page.tsx:106` | `` | Line length is 146 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/studio/page.tsx:55` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/studio/page.tsx:224` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/studio/page.tsx:227` | `` | Line length is 191 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/studio/page.tsx:233` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/studio/page.tsx:235` | `` | Line length is 136 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/studio/page.tsx:251` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/t/[id]/page.tsx:33` | `` | Line length is 155 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/t/[id]/page.tsx:71` | `` | Line length is 138 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/app/t/[id]/page.tsx:76` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/components/ui/audio.tsx:79` | `` | Line length is 166 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/components/ui/data.tsx:82` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/components/ui/data.tsx:84` | `` | Line length is 140 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/components/ui/data.tsx:102` | `` | Line length is 168 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/components/ui/data.tsx:109` | `` | Line length is 158 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/components/ui/primitives.tsx:219` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/components/ui/primitives.tsx:260` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/components/ui/primitives.tsx:266` | `` | Line length is 144 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/components/ui/states.tsx:28` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/components/ui/states.tsx:118` | `` | Line length is 161 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/components/ui/status.tsx:172` | `` | Line length is 143 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/components/ui/status.tsx:175` | `` | Line length is 135 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/components/ui/status.tsx:204` | `` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/components/ui/surfaces.tsx:65` | `` | Line length is 206 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/components/ui/surfaces.tsx:150` | `` | Line length is 142 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/components/ui/surfaces.tsx:152` | `` | Line length is 169 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/db/index.ts:8` | `` | Line length is 185 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/db/schema.ts:63` | `` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/db/schema.ts:81` | `` | Line length is 140 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/db/schema.ts:87` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/db/schema.ts:99` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/examples/d1/app/api/notes/route.ts:12` | `` | Line length is 185 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/lib/api.ts:19` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/lib/music-client.ts:114` | `` | Line length is 133 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/lib/music-client.ts:119` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/lib/music-client.ts:121` | `` | Line length is 145 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/lib/music-client.ts:123` | `` | Line length is 159 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/lib/music-client.ts:125` | `` | Line length is 142 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/lib/music-client.ts:127` | `` | Line length is 144 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/lib/music-client.ts:131` | `` | Line length is 144 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/lib/music-client.ts:137` | `` | Line length is 132 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/lib/music-client.ts:140` | `` | Line length is 132 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/lib/music-client.ts:165` | `` | Line length is 132 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/lib/music-client.ts:171` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/lib/music-client.ts:207` | `` | Line length is 132 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/lib/music-client.ts:219` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/tests/creator-studio.test.mjs:26` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/tests/creator-studio.test.mjs:35` | `` | Line length is 154 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/tests/creator-studio.test.mjs:49` | `` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/tests/creator-studio.test.mjs:65` | `` | Line length is 138 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/tests/design-system.test.mjs:28` | `` | Line length is 186 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/tests/design-system.test.mjs:41` | `` | Line length is 159 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/tests/design-system.test.mjs:61` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/tests/design-system.test.mjs:64` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/tests/listening-product.test.mjs:46` | `` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/tests/listening-product.test.mjs:49` | `` | Line length is 137 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/tests/listening-product.test.mjs:66` | `` | Line length is 134 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/tests/rendered-html.test.mjs:11` | `` | Line length is 182 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/tests/surface-subtraction.test.mjs:35` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `apps/music-web/tests/surface-subtraction.test.mjs:60` | `` | Line length is 184 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `cloud_status.py:14` | `get_system` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `cloud_status.py:38` | `get_system` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `cloud_status.py:47` | `get_system` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `cloud_status.py:60` | `parse_reports` | Function spans 103 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `cloud_status.py:72` | `parse_reports` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `cloud_status.py:142` | `` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `cloud_status.py:152` | `parse_reports` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/benchmarks/reference_audio/generate_reference_suite.py:35` | `main` | Function spans 81 lines; review responsibility boundaries. |
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
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/scripts/mamse001_benchmark.py:27` | `_swap_kb` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/scripts/mamse002_benchmark.py:30` | `_swap_kb` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/scripts/mamse002_run_real_cases.py:66` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/scripts/mamse003_benchmark.py:30` | `_swap_kb` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/scripts/mamse003_run_real_cases.py:26` | `main` | Function spans 72 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/scripts/mamse003_run_real_cases.py:92` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/scripts/mamse003_run_real_cases.py:94` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/scripts/mamse007_benchmark.py:19` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/scripts/mamse009_run_real_cases.py:26` | `main` | Function spans 63 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/scripts/mamse010_benchmark.py:32` | `main` | Function spans 71 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/scripts/mamse010_run_real_cases.py:34` | `main` | Function spans 68 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/scripts/mamse011_benchmark.py:62` | `` | Line length is 142 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/scripts/mamse011_run_real_cases.py:42` | `main` | Function spans 95 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/scripts/mamse011_run_real_cases.py:96` | `` | Line length is 150 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/scripts/mamse011_run_real_cases.py:98` | `` | Line length is 169 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/scripts/mamse011_run_real_cases.py:114` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/scripts/mamse012_benchmark.py:38` | `main` | Function spans 77 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/scripts/mamse012_run_real_cases.py:41` | `main` | Function spans 78 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/scripts/mamse013_benchmark.py:30` | `_swap_kb` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/scripts/mamse014_benchmark.py:30` | `_swap_kb` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/scripts/mamse015_benchmark.py:30` | `_swap_kb` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/scripts/mamse016_benchmark.py:30` | `_swap_kb` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/scripts/prepare_ab_pairs.py:15` | `prepare_pairs` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/scripts/prepare_ab_pairs.py:65` | `` | Line length is 148 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/main.py:108` | `create_job` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/calibration.py:32` | `get_calibration_status` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/api/routes/reviews.py:41` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/api/routes/reviews.py:58` | `` | Line length is 146 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/api/routes/reviews.py:60` | `` | Line length is 140 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/api/routes/reviews.py:64` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/api/routes/reviews.py:75` | `` | Line length is 135 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/api/routes/reviews.py:79` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/sessions.py:63` | `list_sessions` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/sessions.py:88` | `submit_feedback` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/api/routes/stems.py:71` | `create_stem_job` | Function complexity proxy is 20; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/api/routes/stems.py:71` | `create_stem_job` | Function spans 70 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/api/routes/stems.py:92` | `` | Line length is 132 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/api/routes/stems.py:102` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/api/routes/stems.py:137` | `create_stem_job` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/api/routes/stems.py:174` | `` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/audio_io.py:15` | `load_audio` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/comparison.py:80` | `compute_deltas` | Function spans 69 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/auditory/decode.py:70` | `ffmpeg_version` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/decode.py:74` | `probe` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/errors.py:15` | `__init__` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/events/evaluate.py:13` | `evaluate_events` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/events/rules.py:125` | `_threshold_run` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/events/rules.py:146` | `_level_events` | Function complexity proxy is 17; branch pressure may hide decisions. |
| WARNING | `TT-NESTING` | `moodify-core-package/src/moodify/auditory/events/rules.py:146` | `_level_events` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/evidence/resolver.py:34` | `assemble_judgment_evidence` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/execution/cache.py:33` | `put` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/execution/engine.py:57` | `run` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/auditory/execution/engine.py:83` | `run` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/execution/pipeline.py:29` | `local_analysis_nodes` | Function spans 73 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/judgment.py:37` | `evaluate_risk_flags` | Function spans 111 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/auditory/judgment.py:215` | `` | Line length is 135 characters; expression may be compressed. |
| WARNING | `TT-NESTING` | `moodify-core-package/src/moodify/auditory/judgment.py:215` | `evaluate_processing_plan` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/lab/calibration.py:12` | `recommend_for_operator` | Function complexity proxy is 15; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/lab/evaluate.py:27` | `evaluate_experiment` | Function spans 70 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/lab/evaluate.py:109` | `aggregate_matrix` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/measurement_layers.py:89` | `map_metrics_to_findings` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/measurement_layers.py:89` | `map_metrics_to_findings` | Function spans 62 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/metrics.py:67` | `compute_metrics` | Function complexity proxy is 15; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/auditory/models.py:97` | `` | Line length is 172 characters; expression may be compressed. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/reports.py:103` | `build_contact_sheet` | Function has 9 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/run_golden.py:30` | `main` | Function spans 104 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/auditory/service.py:83` | `` | Line length is 155 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/service.py:123` | `scan_audio` | Function spans 111 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/auditory/service.py:164` | `scan_audio` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/auditory/service.py:322` | `compare_scans` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/auditory/spectrogram.py:62` | `_ffmpeg_version` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/spectrogram.py:81` | `generate_spectrogram` | Function spans 73 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/auditory/stereo.py:14` | `compute_stereo_metrics` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/auditory/timeline.py:13` | `compute_timeline` | Function spans 71 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/authority/escalation.py:62` | `` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/authority/escalation.py:64` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/authority/escalation.py:109` | `` | Line length is 167 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/authority/escalation.py:131` | `` | Line length is 139 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/authority/pipeline.py:28` | `run_scoped_review` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/authority/pipeline.py:81` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/authority/review_store.py:71` | `` | Line length is 138 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/authority/review_store.py:72` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/authority/review_store.py:85` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/authority/review_store.py:93` | `` | Line length is 138 characters; expression may be compressed. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/authority/review_store.py:93` | `decide` | Function has 8 declared parameters; implicit context may need a named structure. |
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
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/cli.py:100` | `cmd_legacy_analyze` | Function spans 76 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli.py:257` | `` | Line length is 169 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/cli.py:261` | `cmd_batch` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/cli.py:273` | `cmd_batch` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/data_factory/case_runner.py:72` | `submit` | Function spans 63 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/data_factory/case_runner.py:112` | `submit` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/data_factory/plan_generator.py:86` | `_derive_objective` | Function spans 107 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/data_factory/verification_contract.py:90` | `verify_intervention` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/data_plane/control.py:148` | `enqueue` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/data_plane/control.py:193` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/data_plane/control.py:199` | `` | Line length is 141 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/data_plane/control.py:222` | `claim` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/data_plane/control.py:245` | `heartbeat` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/data_plane/control.py:276` | `verify` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/data_plane/control.py:306` | `complete` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/data_plane/control.py:310` | `fail` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/data_plane/control.py:349` | `fail` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/data_plane/control.py:368` | `requeue` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/data_plane/control.py:395` | `cancel` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/data_plane/control.py:436` | `recover_expired_leases` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/data_plane/pipeline.py:243` | `run` | Function spans 77 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/data_plane/pipeline.py:342` | `_stage_acquire` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/data_plane/pipeline.py:379` | `_stage_stem` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/data_plane/pipeline.py:395` | `_stage_analyze` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/data_plane/pipeline.py:416` | `_stage_judge` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/data_plane/pipeline.py:435` | `_stage_intervene` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/data_plane/pipeline.py:470` | `_stage_render` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/data_plane/pipeline.py:492` | `_stage_verify` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/data_plane/repository.py:106` | `register_track` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/data_plane/repository.py:122` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/data_plane/repository.py:136` | `register_job` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/data_plane/repository.py:159` | `` | Line length is 144 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/data_plane/repository.py:161` | `` | Line length is 131 characters; expression may be compressed. |
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
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/era_diagnostic/engine.py:158` | `detect_dynamics` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/era_diagnostic/engine.py:213` | `detect_stereo` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/era_diagnostic/engine.py:343` | `_finding` | Function has 7 declared parameters; implicit context may need a named structure. |
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
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/identity_guard/ranking.py:63` | `rank_candidates` | Function spans 67 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/intervention/pipeline.py:158` | `run_intervention_pipeline` | Function complexity proxy is 17; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/intervention/pipeline.py:158` | `run_intervention_pipeline` | Function spans 103 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/intervention/registry.py:39` | `` | Line length is 157 characters; expression may be compressed. |
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
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/listening/protocol.py:71` | `` | Line length is 134 characters; expression may be compressed. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/listening/session_store.py:29` | `record_session` | Function has 9 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/llm/client.py:61` | `` | Line length is 138 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/llm/client.py:129` | `interpret_emotion` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/llm/client.py:132` | `narrate_diagnosis` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/llm/client.py:158` | `narrate_diagnosis` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/llm/client.py:228` | `_call` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/memory/history.py:89` | `load_all` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/memory/history.py:107` | `find_similar` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/node/queue.py:61` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/node/queue.py:112` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/node/worker.py:65` | `run_forever` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
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
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/processing/operators.py:40` | `apply_eq` | Function spans 76 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/processing/operators.py:147` | `apply_compressor` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/processing/pedalboard_chain.py:139` | `process_with_fingerprint` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/processing/pedalboard_chain.py:235` | `_compute_transient_preservation` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/processing/pedalboard_chain.py:255` | `_compute_centroid_shift` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/processing/pedalboard_chain.py:295` | `_estimate_dynamic_contribution` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/reconstruction_factory/factory.py:86` | `run_reconstruction_batch` | Function spans 67 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/reconstruction_factory/factory.py:135` | `run_reconstruction_batch` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/reconstruction_job/cli.py:41` | `main` | Function complexity proxy is 19; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/reconstruction_job/cli.py:41` | `main` | Function spans 119 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/reconstruction_job/engine.py:117` | `_finalize` | Function spans 84 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/reconstruction_job/engine.py:117` | `_finalize` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/reconstruction_job/engine.py:203` | `run_reconstruction_job` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/reconstruction_job/engine.py:203` | `run_reconstruction_job` | Function spans 114 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/reconstruction_job/engine.py:239` | `run_reconstruction_job` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/reconstruction_job/engine.py:256` | `run_reconstruction_job` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/reconstruction_job/engine.py:312` | `run_reconstruction_job` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/reconstruction_job/resource_meter.py:28` | `note_memory` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/reconstruction_job/routes_reconstruction.py:74` | `create_job` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/reconstruction_job/routes_reconstruction.py:74` | `create_job` | Function spans 81 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/reconstruction_job/routes_reconstruction.py:74` | `create_job` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/reconstruction_job/routes_reconstruction.py:109` | `create_job` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/reconstruction_job/routes_reconstruction.py:198` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/reconstruction_job/worker.py:104` | `_process_one` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/reconstruction_objective/generator.py:46` | `build_objectives` | Function spans 63 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/reconstruction_objective/objective.py:13` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/release.py:38` | `analyze_to_case` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/release.py:38` | `analyze_to_case` | Function spans 112 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/release.py:141` | `analyze_to_case` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-NESTING` | `moodify-core-package/src/moodify/release_cli.py:12` | `main` | Maximum nesting depth is 6; failure and decision paths are compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/safety/projection.py:11` | `project` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/safety/projection.py:72` | `_get_rec_params` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/safety/test_projection.py:88` | `test_pass_through` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/safety/test_projection.py:123` | `test_partial_params_pass_through` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/stems/service.py:50` | `estimate_duration` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/stems/service.py:90` | `submit` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-NESTING` | `moodify-core-package/src/moodify/stems/service.py:143` | `refresh` | Maximum nesting depth is 6; failure and decision paths are compressed. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/stems/store.py:251` | `update_status` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/v01_diagnostics.py:6` | `diagnose` | Function spans 78 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/v01_pipeline.py:22` | `process_audio` | Function spans 62 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/v01_pipeline.py:77` | `process_audio` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify_experimental/mamse001/evidence.py:39` | `_git_commit` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify_experimental/mamse001/evidence.py:57` | `_dependency_identity` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify_experimental/mamse001/evidence.py:73` | `_ffmpeg_version` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify_experimental/mamse001/evidence.py:110` | `build_cross_resolution_evidence` | Function spans 67 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify_experimental/mamse001/evidence.py:150` | `` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify_experimental/mamse001/sketch.py:41` | `compute_resolution_sketch` | Function spans 75 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify_experimental/mamse002/events.py:81` | `` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify_experimental/mamse002/evidence.py:42` | `_git_commit` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify_experimental/mamse002/evidence.py:119` | `save_case` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify_experimental/mamse003/evidence.py:30` | `_git_commit` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify_experimental/mamse003/sketch.py:70` | `analyze_texture` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify_experimental/mamse003/sketch.py:70` | `analyze_texture` | Function spans 77 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify_experimental/mamse004/evidence.py:27` | `_git_commit` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify_experimental/mamse004/stereo.py:39` | `analyze_stereo_phase` | Function spans 61 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify_experimental/mamse005/evidence.py:29` | `_git_commit` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify_experimental/mamse005/sketch.py:24` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify_experimental/mamse005/sketch.py:35` | `analyze_cepstral_structure` | Function spans 104 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify_experimental/mamse006/evidence.py:29` | `_git_commit` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify_experimental/mamse006/features.py:20` | `summarize_modulation` | Function spans 63 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify_experimental/mamse006/synthetic.py:28` | `ripple_surface` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify_experimental/mamse007/pca.py:46` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify_experimental/mamse007/preprocess.py:82` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify_experimental/mamse007/serialize.py:23` | `_git_commit` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify_experimental/mamse007/synthetic.py:14` | `` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify_experimental/mamse008/evidence.py:29` | `_git_commit` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify_experimental/mamse008/nmf.py:177` | `fit_nmf` | Function complexity proxy is 15; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify_experimental/mamse008/nmf.py:177` | `fit_nmf` | Function spans 75 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify_experimental/mamse009/evidence.py:30` | `_git_commit` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify_experimental/mamse009/evidence.py:64` | `` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify_experimental/mamse010/evidence.py:24` | `_git_commit` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify_experimental/mamse011/covariance.py:266` | `fit_covariance_model` | Function spans 76 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify_experimental/mamse011/evidence.py:25` | `_git_commit` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-NESTING` | `moodify-core-package/src/moodify_experimental/mamse012/contracts.py:144` | `connected_components` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify_experimental/mamse012/contracts.py:151` | `connected_components` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify_experimental/mamse012/evidence.py:25` | `_git_commit` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify_experimental/mamse013/evidence.py:41` | `_git_commit` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify_experimental/mamse013/evidence.py:115` | `save_case` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify_experimental/mamse014/evidence.py:35` | `_git_commit` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify_experimental/mamse014/evidence.py:103` | `save_case` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify_experimental/mamse015/evidence.py:35` | `_git_commit` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify_experimental/mamse015/evidence.py:98` | `save_case` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify_experimental/mamse015/objects.py:79` | `compute_soft_object_observation` | Function spans 77 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify_experimental/mamse016/evidence.py:35` | `_git_commit` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify_experimental/mamse016/evidence.py:113` | `save_case` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify_experimental/mamse016/pitch.py:147` | `compute_pitch_observation` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify_experimental/mamse016/pitch.py:147` | `compute_pitch_observation` | Function spans 73 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify_experimental/mamse016/pitch.py:248` | `_close_run` | Function has 9 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/tests/auditory/test_measurement_correctness.py:217` | `_ffmpeg_available` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/authority/test_authority_escalation.py:172` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/authority/test_authority_escalation.py:186` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/authority/test_authority_escalation.py:188` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/authority/test_authority_escalation.py:190` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/tests/baseline/check_regression.py:40` | `check_one` | Function complexity proxy is 17; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/tests/baseline/check_regression.py:82` | `main` | Function spans 61 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/tests/baseline/run_baseline.py:95` | `test_fallback_search` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/tests/baseline/run_baseline.py:114` | `test_fallback_preset` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/tests/baseline/run_baseline.py:218` | `run_all` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/tests/baseline/run_baseline.py:232` | `run_all` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/data_factory/test_case_runner.py:81` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/data_factory/test_verification_contract.py:68` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/data_factory/test_verification_contract.py:79` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/reconstruction_factory/test_factory.py:62` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/test_data_plane.py:48` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/test_data_plane.py:167` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/tests/test_mfy_1_0_representative.py:25` | `_tools_available` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-music-package/alembic/versions/001_identity_creator_catalog.py:21` | `upgrade` | Function spans 107 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-music-package/alembic/versions/002_relationships_intents.py:21` | `upgrade` | Function spans 77 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `moodify-music-package/src/moodify_music/api/idem.py:33` | `idempotent_write` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/main.py:25` | `` | Line length is 145 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-music-package/src/moodify_music/api/main.py:40` | `error_normalization` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/main.py:70` | `` | Line length is 176 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_bridge.py:122` | `` | Line length is 137 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-music-package/src/moodify_music/api/routes_bridge.py:127` | `update_request` | Function complexity proxy is 18; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_cwc.py:28` | `` | Line length is 138 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_cwc.py:32` | `` | Line length is 198 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_cwc.py:64` | `` | Line length is 139 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_cwc.py:68` | `` | Line length is 217 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-music-package/src/moodify_music/api/routes_intents.py:20` | `create_license_intent` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_intents.py:41` | `` | Line length is 142 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_intents.py:45` | `` | Line length is 185 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_intents.py:80` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_intents.py:110` | `` | Line length is 142 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_intents.py:114` | `` | Line length is 185 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_library.py:43` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_playlists.py:19` | `` | Line length is 142 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_playlists.py:20` | `` | Line length is 140 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_playlists.py:47` | `` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_playlists.py:51` | `` | Line length is 158 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_playlists.py:67` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_playlists.py:83` | `` | Line length is 161 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_playlists.py:97` | `` | Line length is 168 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_playlists.py:103` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_playlists.py:111` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_playlists.py:114` | `` | Line length is 146 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_playlists.py:117` | `` | Line length is 204 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_playlists.py:123` | `` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_playlists.py:128` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_playlists.py:132` | `` | Line length is 206 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_playlists.py:140` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_search.py:58` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_social.py:17` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_social.py:31` | `` | Line length is 142 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_social.py:35` | `` | Line length is 162 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_social.py:41` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_social.py:46` | `` | Line length is 166 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_social.py:59` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_social.py:73` | `` | Line length is 146 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_social.py:77` | `` | Line length is 164 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_social.py:83` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_social.py:88` | `` | Line length is 168 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_tracks.py:131` | `` | Line length is 140 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_tracks.py:135` | `` | Line length is 196 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_tracks.py:168` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_tracks.py:173` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_tracks.py:174` | `` | Line length is 142 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_tracks.py:187` | `` | Line length is 140 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_tracks.py:191` | `` | Line length is 187 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_tracks.py:213` | `` | Line length is 152 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_tracks.py:217` | `` | Line length is 198 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_tracks.py:245` | `` | Line length is 216 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_tracks.py:249` | `` | Line length is 186 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_tracks.py:273` | `` | Line length is 137 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_tracks.py:278` | `` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_tracks.py:282` | `` | Line length is 169 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_tracks.py:310` | `` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_users.py:41` | `` | Line length is 137 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_users.py:45` | `` | Line length is 161 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-music-package/src/moodify_music/api/routes_users.py:59` | `create_creator` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_users.py:83` | `` | Line length is 146 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_users.py:87` | `` | Line length is 158 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/api/routes_users.py:144` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-PARAMETERS` | `moodify-music-package/src/moodify_music/audit.py:21` | `record` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/bff/main.py:32` | `` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/bff/main.py:50` | `` | Line length is 189 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/bff/main.py:165` | `` | Line length is 186 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-music-package/src/moodify_music/bff/media.py:22` | `looks_like_audio` | Function complexity proxy is 15; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/src/moodify_music/bff/media.py:39` | `` | Line length is 136 characters; expression may be compressed. |
| WARNING | `TT-PARAMETERS` | `moodify-music-package/src/moodify_music/idempotency.py:52` | `finish` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_api.py:72` | `` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_api.py:144` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_api.py:145` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_api.py:147` | `` | Line length is 147 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_api.py:152` | `` | Line length is 179 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_api.py:163` | `` | Line length is 151 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_api.py:189` | `` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_api.py:208` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_api.py:219` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_api.py:221` | `` | Line length is 139 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_api.py:223` | `` | Line length is 132 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-music-package/tests/test_architecture.py:34` | `test_music_never_imports_ear_internals` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-NESTING` | `moodify-music-package/tests/test_architecture.py:52` | `test_music_does_not_import_ear_package_at_all` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-NESTING` | `moodify-music-package/tests/test_architecture.py:95` | `test_no_forbidden_product_identity_claims` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_bff.py:194` | `` | Line length is 136 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_bff.py:196` | `` | Line length is 137 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_console.py:27` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_console.py:87` | `` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_console.py:97` | `` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_console.py:100` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_creator_publishing.py:34` | `` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_creator_publishing.py:46` | `` | Line length is 141 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_data_plane_behavior.py:53` | `` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_data_plane_behavior.py:54` | `` | Line length is 142 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_data_plane_behavior.py:56` | `` | Line length is 138 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_data_plane_behavior.py:60` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_data_plane_behavior.py:126` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_data_plane_behavior.py:147` | `` | Line length is 133 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_data_plane_behavior.py:149` | `` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_data_plane_behavior.py:178` | `` | Line length is 142 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_data_plane_behavior.py:182` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_data_plane_behavior.py:190` | `` | Line length is 134 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_data_plane_constraints.py:54` | `` | Line length is 133 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_data_plane_constraints.py:56` | `` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_data_plane_constraints.py:75` | `` | Line length is 133 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_data_plane_constraints.py:77` | `` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_data_plane_constraints.py:81` | `` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_data_plane_constraints.py:84` | `` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_data_plane_constraints.py:88` | `` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_data_plane_constraints.py:90` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_data_plane_constraints.py:94` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_data_plane_constraints.py:96` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_evidence_bridge.py:35` | `` | Line length is 148 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_evidence_bridge.py:37` | `` | Line length is 144 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_evidence_bridge.py:65` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_evidence_bridge.py:67` | `` | Line length is 140 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_evidence_bridge.py:73` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_evidence_bridge.py:105` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_evidence_bridge.py:159` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-music-package/tests/test_freeze_contracts.py:103` | `test_env_variable_names_are_frozen` | Function complexity proxy is 18; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_identity.py:153` | `` | Line length is 141 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_identity.py:174` | `` | Line length is 146 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_identity.py:213` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_library.py:27` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_library.py:42` | `` | Line length is 141 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_library.py:47` | `` | Line length is 139 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_library.py:54` | `` | Line length is 161 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_library.py:89` | `` | Line length is 132 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_lifecycle.py:38` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_lifecycle.py:64` | `` | Line length is 136 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_playlists.py:27` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_playlists.py:59` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_playlists.py:92` | `` | Line length is 138 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_playlists.py:108` | `` | Line length is 141 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_search.py:71` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_security_matrix.py:72` | `` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_security_matrix.py:73` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-music-package/tests/test_security_matrix.py:99` | `` | Line length is 152 characters; expression may be compressed. |
| WARNING | `TT-NESTING` | `ops/data_node/daily_report.py:41` | `read_jobs` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `ops/data_node/daily_report.py:113` | `journal_counts` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `ops/data_node/daily_report.py:126` | `oom_count` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `ops/data_node/inbox_ingest.py:172` | `scan_inbox` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `ops/data_node/resource_probe.py:49` | `service_state` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `ops/data_node/validate_pilot_manifest.py:22` | `duration_seconds` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `ops/e2e_runner.py:42` | `get` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `ops/e2e_runner.py:100` | `` | Line length is 137 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `ops/e2e_runner.py:109` | `stage_local_ear` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:23` | `` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:57` | `` | Line length is 134 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:58` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:88` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:107` | `` | Line length is 136 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:109` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:111` | `` | Line length is 165 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:112` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:114` | `` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:137` | `` | Line length is 153 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:189` | `` | Line length is 183 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:193` | `` | Line length is 166 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:195` | `` | Line length is 162 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:197` | `` | Line length is 153 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:199` | `` | Line length is 172 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:201` | `` | Line length is 158 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:209` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:216` | `` | Line length is 179 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:270` | `` | Line length is 195 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:271` | `` | Line length is 172 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:272` | `` | Line length is 170 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:273` | `` | Line length is 182 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:274` | `` | Line length is 162 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:275` | `` | Line length is 144 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:281` | `` | Line length is 418 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:282` | `` | Line length is 442 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:283` | `` | Line length is 434 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:284` | `` | Line length is 502 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:285` | `` | Line length is 442 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:286` | `` | Line length is 412 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:287` | `` | Line length is 440 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:288` | `` | Line length is 475 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:289` | `` | Line length is 481 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:290` | `` | Line length is 445 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:291` | `` | Line length is 344 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:292` | `` | Line length is 451 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:309` | `` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:317` | `` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:320` | `` | Line length is 157 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:322` | `` | Line length is 195 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:328` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:338` | `` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:340` | `` | Line length is 154 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:342` | `` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/derive_outputs.py:343` | `` | Line length is 187 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `ops/ear_batch/ear_batch.py:193` | `cmd_promote` | Function spans 71 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `ops/ear_batch/ear_batch.py:271` | `cmd_validate` | Function complexity proxy is 17; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/knowledge_extract.py:65` | `` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/knowledge_extract.py:88` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-NESTING` | `ops/ear_batch/knowledge_extract.py:99` | `extract_disciplines` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/knowledge_extract.py:103` | `` | Line length is 150 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `ops/ear_batch/material_governance.py:38` | `package_consistency` | Function complexity proxy is 17; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `ops/ear_batch/material_governance.py:48` | `package_consistency` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `ops/ear_batch/material_governance.py:80` | `` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `ops/ear_batch/material_governance.py:90` | `text_integrity` | Function complexity proxy is 20; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `ops/verify_evidence.py:30` | `` | Line length is 149 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `ops/verify_evidence.py:43` | `main` | Function complexity proxy is 19; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `ops/web_origin/site/check_company_site.mjs:17` | `` | Line length is 175 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/web_origin/site/check_company_site.mjs:52` | `` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/web_origin/site/check_company_site.mjs:56` | `` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/web_origin/site/check_site.mjs:35` | `` | Line length is 152 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/web_origin/site/check_site.mjs:92` | `` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `ops/web_origin/site/check_site.mjs:94` | `` | Line length is 151 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `scripts/canon_guard.py:64` | `check_files` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/ear_50_case_pilot.py:113` | `main` | Function spans 65 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `scripts/ear_50_case_pilot.py:170` | `` | Line length is 124 characters; expression may be compressed. |
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
| WARNING | `TT-LINE-LENGTH` | `tests/ear_batch/test_knowledge_extract.py:13` | `` | Line length is 128 characters; expression may be compressed. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/app/studio/page.tsx:8` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/app/studio/page.tsx:17` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/app/studio/page.tsx:25` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/app/studio/page.tsx:28` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/app/studio/page.tsx:34` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/app/studio/page.tsx:36` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/app/studio/page.tsx:42` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/app/studio/page.tsx:56` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/app/studio/page.tsx:60` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/app/studio/page.tsx:62` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/app/studio/page.tsx:67` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/app/studio/page.tsx:70` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/app/studio/page.tsx:89` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/app/studio/page.tsx:90` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/app/studio/page.tsx:124` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/app/studio/page.tsx:148` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/app/studio/page.tsx:185` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/app/studio/page.tsx:189` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/app/studio/page.tsx:192` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/app/studio/page.tsx:193` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/components/ui/audio.tsx:42` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/components/ui/data.tsx:82` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/tests/creator-studio.test.mjs:49` | `` | Debt marker TODO requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `apps/music-web/worker/index.ts:1` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/scripts/mamse006_benchmark.py:36` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/scripts/mamse006_run_real_cases.py:47` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/scripts/mamse006_run_real_cases.py:48` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/scripts/mamse006_run_real_cases.py:54` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/scripts/mamse009_run_real_cases.py:6` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/scripts/mamse009_run_real_cases.py:18` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/scripts/mamse009_run_real_cases.py:57` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/scripts/mamse012_benchmark.py:18` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/scripts/mamse012_benchmark.py:23` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/scripts/mamse012_benchmark.py:47` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/scripts/mamse012_benchmark.py:67` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/scripts/mamse012_benchmark.py:71` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/scripts/mamse012_run_real_cases.py:4` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/scripts/mamse012_run_real_cases.py:19` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/scripts/mamse012_run_real_cases.py:24` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/scripts/mamse012_run_real_cases.py:72` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/scripts/mamse012_run_real_cases.py:73` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/scripts/mamse012_run_real_cases.py:75` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/api/main.py:6` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/api/main.py:153` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/decode.py:123` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/decode.py:127` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/__init__.py:1` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/__init__.py:3` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/__init__.py:6` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/__init__.py:9` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/__init__.py:13` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/__init__.py:14` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/__init__.py:15` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/__init__.py:17` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/engine.py:1` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/engine.py:17` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/engine.py:19` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/engine.py:25` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/engine.py:26` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/engine.py:28` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/engine.py:38` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/engine.py:39` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/engine.py:41` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/engine.py:56` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/engine.py:63` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/evaluate.py:4` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/evaluate.py:10` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/evaluate.py:13` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/evaluate.py:32` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/evaluate.py:54` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/merge.py:11` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/merge.py:12` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/merge.py:18` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/merge.py:21` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/merge.py:22` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/merge.py:23` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/merge.py:62` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/models.py:1` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/models.py:3` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/models.py:34` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/models.py:72` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/models.py:91` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/rules.py:14` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/rules.py:25` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/rules.py:96` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/temporal_profile.py:1` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/temporal_profile.py:17` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/temporal_profile.py:27` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/temporal_profile.py:28` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/events/temporal_profile.py:35` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/evidence/resolver.py:102` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/evidence/resolver.py:247` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/evidence/scale.py:1` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/cache.py:9` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/cache.py:38` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/cache.py:43` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/cache.py:45` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/cache.py:46` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/cache.py:47` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/cache.py:59` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/cache.py:62` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/cache.py:65` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/cache.py:66` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/checkpoints.py:29` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/checkpoints.py:30` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/checkpoints.py:31` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/engine.py:88` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/identity.py:14` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/pipeline.py:11` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/pipeline.py:53` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/pipeline.py:56` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/pipeline.py:70` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/pipeline.py:80` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/pipeline.py:92` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/pipeline.py:93` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/pipeline.py:96` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/pipeline.py:99` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/pipeline.py:110` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/planner.py:20` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/execution/planner.py:25` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/lab/calibration.py:22` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/lab/evaluate.py:3` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/lab/evaluate.py:15` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/lab/evaluate.py:21` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/lab/evaluate.py:63` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/lab/evaluate.py:75` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/lab/evaluate.py:105` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/lab/evaluate.py:123` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/lab/runner.py:4` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/lab/runner.py:12` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/lab/runner.py:57` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/measurement_layers.py:48` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/measurement_layers.py:68` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/representation/alignment.py:1` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/representation/build.py:25` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/representation/build.py:47` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/representation/build.py:52` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/representation/models.py:4` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/structure.py:41` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/structure.py:75` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/auditory/uncertainty.py:15` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/calibration/listener.py:143` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_factory/case_runner.py:8` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_factory/case_runner.py:99` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_factory/human_review.py:14` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:7` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:21` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:22` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:23` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:24` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:25` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:26` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:27` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:28` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:29` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:30` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:31` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:32` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:33` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:34` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:77` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:88` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:89` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:91` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:99` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:104` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:133` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:139` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:142` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:198` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:199` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:205` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:207` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:210` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:212` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:214` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:215` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:216` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:220` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:221` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:242` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:272` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:299` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:300` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:301` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:324` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:325` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:331` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:338` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:339` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:341` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:407` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:416` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:417` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:425` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:426` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/control.py:427` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/manifest.py:21` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:60` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:73` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:87` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:108` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:123` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:162` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:163` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:167` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:168` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:245` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:261` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:277` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:310` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:319` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:324` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:346` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:364` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:383` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:404` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:420` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:439` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:450` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:474` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/pipeline.py:497` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/data_plane/repository.py:37` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/era_diagnostic/engine.py:6` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/intervention/primitives.py:253` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/llm/client.py:208` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/llm/client.py:224` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/llm/client.py:229` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/node/config.py:19` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/node/config.py:35` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/node/db.py:14` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/node/models.py:22` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/node/queue.py:61` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/node/queue.py:92` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/node/queue.py:93` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/node/queue.py:96` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/node/queue.py:99` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/node/worker.py:62` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/node/worker.py:68` | `` | Debt marker TEMP requires a reason and exit condition. |
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
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reconstruction_factory/learning_record.py:37` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reconstruction_job/contract.py:114` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reconstruction_job/contract.py:124` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reconstruction_job/contract.py:150` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reconstruction_job/resource_meter.py:38` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reconstruction_job/retention.py:63` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reconstruction_job/store.py:42` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reconstruction_job/store.py:124` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reconstruction_job/store.py:134` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reconstruction_job/store.py:203` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reconstruction_job/store.py:314` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reconstruction_job/store.py:319` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reconstruction_job/store.py:323` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/reconstruction_job/worker.py:34` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/stems/store.py:4` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse001/__init__.py:4` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse001/registry.py:3` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse001/sketch.py:133` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse002/__init__.py:18` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse002/__init__.py:51` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse002/config.py:3` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse002/config.py:19` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse002/config.py:79` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse002/sketch.py:15` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse002/sketch.py:93` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse003/evidence.py:71` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse003/evidence.py:82` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse003/sketch.py:51` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse003/sketch.py:128` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/__init__.py:1` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/__init__.py:3` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/config.py:32` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/config.py:33` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/config.py:52` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/config.py:53` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/features.py:20` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/features.py:21` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/features.py:23` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/features.py:27` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/features.py:31` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/features.py:32` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/features.py:34` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/features.py:35` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/features.py:46` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/features.py:64` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/features.py:73` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/features.py:74` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/features.py:77` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/features.py:78` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/modulation.py:1` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/modulation.py:3` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/modulation.py:57` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/modulation.py:60` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/modulation.py:65` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/modulation.py:67` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/operator.py:21` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/operator.py:60` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/operator.py:61` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/synthetic.py:29` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse006/synthetic.py:32` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse011/__init__.py:6` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse011/covariance.py:4` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse012/__init__.py:3` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse012/__init__.py:12` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse012/__init__.py:47` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse012/builders.py:1` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse012/builders.py:50` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse012/builders.py:56` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse012/builders.py:58` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse012/builders.py:62` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse012/builders.py:80` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse012/builders.py:95` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify_experimental/mamse012/builders.py:99` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_ch02_phase1_evidence.py:3` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_ch02_phase1_evidence.py:25` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_ch02_phase1_evidence.py:58` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_ch02_phase1_evidence.py:62` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_ch02_phase1_evidence.py:107` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_ch02_phase1_evidence.py:123` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_ch02_phase1_evidence.py:163` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_ch02_phase1_evidence.py:211` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_ch02_phase1_evidence.py:261` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_ch02_phase1_evidence.py:269` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_ch02_phase1_evidence.py:281` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_ch02_phase1_evidence.py:290` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_evidence_uncertainty.py:19` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_evidence_uncertainty.py:53` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_evidence_uncertainty.py:57` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_evidence_uncertainty.py:76` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_evidence_uncertainty.py:105` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_evidence_uncertainty.py:133` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_evidence_uncertainty.py:149` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_lab.py:107` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_lab.py:115` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_lab.py:133` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_lab.py:191` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_lab.py:203` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_local_execution.py:26` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_multiscale_representation.py:16` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_multiscale_representation.py:145` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_multiscale_representation.py:219` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_temporal_hearing.py:1` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_temporal_hearing.py:13` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_temporal_hearing.py:15` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_temporal_hearing.py:45` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_temporal_hearing.py:46` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_temporal_hearing.py:55` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_temporal_hearing.py:56` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_temporal_hearing.py:100` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/auditory/test_temporal_hearing.py:111` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/conftest.py:18` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/data_factory/conftest.py:21` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/data_factory/test_algorithmic_review.py:103` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/data_factory/test_algorithmic_review.py:105` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/data_factory/test_case_runner.py:78` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/experimental/test_mamse001.py:111` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/experimental/test_mamse006.py:54` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/experimental/test_mamse006.py:55` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/experimental/test_mamse006.py:74` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/experimental/test_mamse006.py:75` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/experimental/test_mamse006.py:82` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/experimental/test_mamse006.py:88` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/experimental/test_mamse006.py:90` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/experimental/test_mamse006.py:92` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/experimental/test_mamse006.py:129` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/experimental/test_mamse006.py:131` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/experimental/test_mamse006.py:145` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/experimental/test_mamse010.py:65` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/experimental/test_mamse010.py:66` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/experimental/test_mamse012.py:25` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/experimental/test_mamse012.py:165` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/experimental/test_mamse012.py:174` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/experimental/test_mamse012.py:183` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/experimental/test_mamse015.py:87` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/node/test_queue.py:21` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/node/test_queue.py:30` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/node/test_queue.py:34` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/node/test_queue.py:65` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/node/test_queue.py:67` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/node/test_queue.py:68` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/node/test_queue.py:70` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/node/test_worker.py:80` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/ops/test_daily_report.py:32` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/reconstruction_job/test_store.py:145` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/reconstruction_job/test_store.py:146` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/reconstruction_job/test_store.py:147` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/reconstruction_job/test_store.py:148` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/reconstruction_job/test_store.py:149` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/reconstruction_job/test_store.py:150` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/reconstruction_job/test_store.py:151` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/reconstruction_job/test_store.py:152` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_control_plane.py:77` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_control_plane.py:93` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_control_plane.py:98` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_control_plane.py:99` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_control_plane.py:103` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_data_plane.py:76` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_fallback.py:55` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_fallback.py:63` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_pipeline.py:90` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_pipeline.py:116` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_pipeline.py:131` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_pipeline.py:150` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_pipeline.py:165` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_pipeline.py:198` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_pipeline.py:215` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_pipeline.py:235` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_pipeline.py:255` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_pipeline.py:269` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_pipeline.py:273` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_pipeline.py:283` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_pipeline.py:299` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_pipeline.py:307` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_pipeline.py:316` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_pipeline.py:335` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_pipeline.py:349` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/src/moodify_music/bff/main.py:49` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/src/moodify_music/bff/main.py:139` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/src/moodify_music/bff/main.py:201` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/src/moodify_music/bff/main.py:206` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/src/moodify_music/bff/main.py:208` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/src/moodify_music/bff/main.py:212` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/src/moodify_music/bff/main.py:277` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/src/moodify_music/bff/main.py:373` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/src/moodify_music/bff/main.py:379` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/src/moodify_music/bff/main.py:391` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/src/moodify_music/bff/main.py:392` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/src/moodify_music/bff/main.py:398` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/src/moodify_music/bff/main.py:399` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/src/moodify_music/bff/media.py:7` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/src/moodify_music/bff/media.py:47` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/src/moodify_music/bff/media.py:49` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/src/moodify_music/bff/media.py:52` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/src/moodify_music/bff/media.py:58` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/tests/test_bff.py:173` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/tests/test_data_plane_behavior.py:99` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/tests/test_data_plane_behavior.py:104` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/tests/test_identity.py:40` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-music-package/tests/test_security_matrix.py:102` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `ops/data_node/inbox_ingest.py:17` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `ops/data_node/inbox_ingest.py:74` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `ops/ear_batch/derive_outputs.py:62` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `ops/ear_batch/derive_outputs.py:261` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `ops/ear_batch/derive_outputs.py:273` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `ops/ear_batch/derive_outputs.py:290` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `ops/ear_batch/ear_batch.py:11` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `ops/ear_batch/ear_batch.py:33` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `ops/ear_batch/ear_batch.py:107` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `ops/ear_batch/ear_batch.py:123` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `ops/ear_batch/ear_batch.py:152` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `ops/ear_batch/ear_batch.py:216` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `ops/ear_batch/ear_batch.py:331` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `ops/ear_batch/ear_batch.py:337` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `ops/ear_batch/ear_batch.py:355` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `ops/ear_batch/ear_batch.py:360` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `ops/ear_batch/ear_batch.py:423` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `ops/ear_batch/ear_batch.py:448` | `` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `ops/ear_batch/ear_batch.py:450` | `` | Debt marker TEMP requires a reason and exit condition. |
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
