# Temporal Texture Regression Guard

- Baseline: `E:\moodify\artifacts\temporal_texture\before\report.json`
- Current: `E:\moodify\artifacts\temporal_texture\after\report.json`
- New findings: **714**
- Resolved findings: **105**

## New findings

| Severity | Rule | Location | Message |
|---|---|---|---|
| ERROR | `TT-FUNCTION-LENGTH` | `docs/strategy/DOC-MFY-003/generate_docx.py:127` | Function spans 340 lines; review responsibility boundaries. |
| ERROR | `TT-FUNCTION-LENGTH` | `docs/strategy/DOC-MFY-003/generate_docx.py:472` | Function spans 194 lines; review responsibility boundaries. |
| ERROR | `TT-FUNCTION-LENGTH` | `docs/strategy/DOC-MFY-003/generate_docx.py:671` | Function spans 188 lines; review responsibility boundaries. |
| ERROR | `TT-COMPLEXITY` | `experiments/physics/EXP-PHYS-002/code/analyze.py:85` | Function complexity proxy is 21; branch pressure may hide decisions. |
| ERROR | `TT-EMPTY-EXCEPTION` | `experiments/physics/EXP-PHYS-002/code/scan.py:30` | Empty exception handler hides failure evidence. |
| ERROR | `TT-EMPTY-EXCEPTION` | `experiments/physics/EXP-PHYS-002/code/scan.py:53` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `experiments/validate_mrs_open_v03.py:316` | Function complexity proxy is 23; branch pressure may hide decisions. |
| ERROR | `TT-COMPLEXITY` | `experiments/validate_mrs_open_v03.py:423` | Function complexity proxy is 23; branch pressure may hide decisions. |
| ERROR | `TT-COMPLEXITY` | `experiments/validate_mrs_open_v03.py:526` | Function complexity proxy is 32; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `experiments/validate_mrs_open_v03.py:526` | Function spans 163 lines; review responsibility boundaries. |
| ERROR | `TT-COMPLEXITY` | `experiments/validate_mrs_open_v03.py:929` | Function complexity proxy is 40; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `experiments/validate_mrs_open_v03.py:929` | Function spans 309 lines; review responsibility boundaries. |
| ERROR | `TT-COMPLEXITY` | `experiments/validate_mrs_open_v03.py:1273` | Function complexity proxy is 28; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `experiments/validate_mrs_open_v03.py:1273` | Function spans 228 lines; review responsibility boundaries. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-bridge/src/moodify_bridge/services.py:168` | Function spans 136 lines; review responsibility boundaries. |
| ERROR | `TT-COMPLEXITY` | `moodify-bridge/src/moodify_bridge/services.py:364` | Function complexity proxy is 25; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-bridge/src/moodify_bridge/services.py:473` | Function spans 143 lines; review responsibility boundaries. |
| ERROR | `TT-PARAMETERS` | `moodify-bridge/src/moodify_bridge/services.py:618` | Function has 11 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-COMPLEXITY` | `moodify-bridge/src/moodify_bridge/services.py:1072` | Function complexity proxy is 26; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-bridge/src/moodify_bridge/services.py:1072` | Function spans 192 lines; review responsibility boundaries. |
| ERROR | `TT-EMPTY-EXCEPTION` | `moodify-core-package/src/moodify/adapters/audacity/runtime.py:170` | Empty exception handler hides failure evidence. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/capability_registry/adapters/base.py:177` | Function complexity proxy is 23; branch pressure may hide decisions. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/craft_slider.py:139` | Function complexity proxy is 26; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/craft_slider.py:139` | Function spans 147 lines; review responsibility boundaries. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/features/f0.py:220` | Function complexity proxy is 25; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/features/f0.py:220` | Function spans 154 lines; review responsibility boundaries. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/score_engine/midi_ingest.py:106` | Function complexity proxy is 26; branch pressure may hide decisions. |
| ERROR | `TT-NESTING` | `moodify-core-package/src/moodify/score_engine/midi_ingest.py:106` | Maximum nesting depth is 8; failure and decision paths are compressed. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/score_engine/musescore_backend.py:129` | Function complexity proxy is 29; branch pressure may hide decisions. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/transcription_pipeline/midi_cleanup.py:66` | Function complexity proxy is 32; branch pressure may hide decisions. |
| ERROR | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/transcription_pipeline/runner.py:68` | Function complexity proxy is 27; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/transcription_pipeline/runner.py:68` | Function spans 138 lines; review responsibility boundaries. |
| ERROR | `TT-PARAMETERS` | `moodify_runtime/fusion_scorer.py:163` | Function has 17 declared parameters; implicit context may need a named structure. |
| ERROR | `TT-COMPLEXITY` | `moodify_runtime/significance_evaluator.py:118` | Function complexity proxy is 22; branch pressure may hide decisions. |
| ERROR | `TT-COMPLEXITY` | `tools/architecture/budget.py:82` | Function complexity proxy is 30; branch pressure may hide decisions. |
| ERROR | `TT-NESTING` | `tools/score_asset_pipeline.py:49` | Maximum nesting depth is 7; failure and decision paths are compressed. |
| ERROR | `TT-COMPLEXITY` | `tools/studio_session_prep/candidate_plan.py:120` | Function complexity proxy is 27; branch pressure may hide decisions. |
| ERROR | `TT-FUNCTION-LENGTH` | `tools/studio_session_prep/candidate_plan.py:120` | Function spans 163 lines; review responsibility boundaries. |
| ERROR | `TT-FUNCTION-LENGTH` | `tools/studio_session_prep/reporting.py:104` | Function spans 187 lines; review responsibility boundaries. |
| ERROR | `TT-FUNCTION-LENGTH` | `tools/studio_session_prep/studio_prep.py:116` | Function spans 144 lines; review responsibility boundaries. |
| ERROR | `TT-EMPTY-EXCEPTION` | `tools/studio_session_prep/studio_prep.py:234` | Empty exception handler hides failure evidence. |
| INFO | `TT-DEBT-MARKER` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:376` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `docs/strategy/DOC-MFY-003/generate_docx.py:331` | Debt marker TODO requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `docs/strategy/DOC-MFY-003/generate_docx.py:799` | Debt marker TODO requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `experiments/physics/EXP-PHYS-001/code/run.py:10` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `experiments/physics/EXP-PHYS-001/code/run.py:56` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `experiments/validate_mrs_open_v03.py:1348` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:149` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:154` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:164` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:175` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:179` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:181` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:182` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:185` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:189` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:196` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:221` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:223` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:227` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:230` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:234` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:240` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:241` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:255` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:257` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:261` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:263` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:265` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:271` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:280` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:287` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:293` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:296` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/src/moodify_bridge/services.py:302` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/tests/test_cli_errors.py:233` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-bridge/tests/test_cli_errors.py:245` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/app/engines.py:113` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/app/production_control.py:25` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/app/production_control.py:485` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/capability_registry/adapters/base.py:14` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/capability_registry/adapters/base.py:193` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/capability_registry/adapters/basic_pitch_adapter.py:11` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/capability_registry/adapters/basic_pitch_adapter.py:83` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/capability_registry/adapters/rubberband_adapter.py:48` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/capability_registry/adapters/rubberband_adapter.py:49` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/capability_registry/bootstrap.py:111` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/capability_registry/execution/gateway.py:11` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/cli_daw/adapters/rubberband.py:41` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/cli_daw/project.py:71` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/mrs_robust.py:10` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/perception/masking.py:58` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/perception/masking.py:59` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/perception/masking.py:94` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/perception/masking.py:124` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/perception/masking.py:276` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/perception/masking.py:285` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/perception/masking.py:288` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/perception/masking.py:310` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/perception/masking.py:363` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/__init__.py:15` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/__init__.py:29` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/midi_ingest.py:3` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/midi_ingest.py:22` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/midi_ingest.py:32` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/midi_ingest.py:66` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/midi_ingest.py:75` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/midi_ingest.py:144` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/midi_ingest.py:146` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/midi_ingest.py:148` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/midi_ingest.py:219` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/midi_ingest.py:221` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/midi_ingest.py:222` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/midi_ingest.py:234` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/midi_ingest.py:238` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/midi_ingest.py:305` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/midi_ingest.py:308` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/model.py:18` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/model.py:39` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/model.py:42` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/musescore_backend.py:14` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/musescore_backend.py:142` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/musicxml_exporter.py:3` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/musicxml_exporter.py:82` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/musicxml_exporter.py:85` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/musicxml_exporter.py:131` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/musicxml_exporter.py:132` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/musicxml_exporter.py:133` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/roundtrip.py:3` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/roundtrip.py:76` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/roundtrip.py:85` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/serialization.py:23` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/serialization.py:95` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/serialization.py:98` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/serialization.py:220` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/serialization.py:223` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/serialization.py:224` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/serialization.py:232` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/score_engine/serialization.py:235` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/transcription.py:24` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/transcription.py:32` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/transcription.py:33` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/transcription.py:80` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/transcription_pipeline/midi_cleanup.py:46` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/transcription_pipeline/midi_cleanup.py:47` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/transcription_pipeline/midi_cleanup.py:48` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/transcription_pipeline/midi_cleanup.py:177` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/transcription_pipeline/midi_cleanup.py:188` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/transcription_pipeline/profiles.py:10` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/transcription_pipeline/profiles.py:22` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/transcription_pipeline/profiles.py:23` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/transcription_pipeline/profiles.py:34` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/transcription_pipeline/profiles.py:45` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/transcription_pipeline/profiles.py:56` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/transcription_pipeline/profiles.py:67` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/transcription_pipeline/profiles.py:79` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/transcription_pipeline/runner.py:124` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/transcription_pipeline/runner.py:172` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/src/moodify/v01_pipeline.py:384` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/orchestration/test_workflow_engine_texture.py:1` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/orchestration/test_workflow_engine_texture.py:4` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/midi_fixtures.py:28` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/midi_fixtures.py:83` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/midi_fixtures.py:96` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/midi_fixtures.py:110` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/midi_fixtures.py:112` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/midi_fixtures.py:113` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/midi_fixtures.py:115` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/midi_fixtures.py:124` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/midi_fixtures.py:135` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/midi_fixtures.py:149` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/test_midi_ingest.py:19` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/test_midi_ingest.py:73` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/test_midi_ingest.py:75` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/test_midi_ingest.py:76` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/test_midi_ingest.py:77` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/test_midi_ingest.py:94` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/test_midi_ingest.py:95` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/test_midi_ingest.py:96` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/test_midi_ingest.py:97` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/test_musescore_backend.py:53` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/test_musescore_backend.py:56` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/test_musicxml_exporter.py:18` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/test_musicxml_exporter.py:65` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/test_musicxml_exporter.py:76` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/test_musicxml_exporter.py:78` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/test_musicxml_exporter.py:79` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/test_musicxml_exporter.py:84` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/test_musicxml_exporter.py:85` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/score_engine/test_musicxml_exporter.py:141` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify-core-package/tests/test_transcription_stems.py:200` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/data_asset.py:14` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/data_asset.py:339` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/operator_console.py:411` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/operator_console.py:705` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/operator_console.py:714` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/operator_console.py:961` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/operator_console.py:981` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/operator_console.py:983` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/operator_console.py:992` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/operator_console.py:993` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:22` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:30` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:96` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:98` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:102` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:104` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:107` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:112` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:114` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:116` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:121` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:122` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:140` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:155` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:156` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:158` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:166` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:177` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:196` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:197` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:254` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:291` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:297` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:298` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:300` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:317` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:325` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/runner.py:351` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_atomic_run_outputs.py:30` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_atomic_run_outputs.py:50` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_atomic_run_outputs.py:52` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_craft_texture.py:4` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_data_asset.py:133` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_data_asset.py:134` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_data_asset.py:135` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_data_asset.py:136` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runner_rights_gate.py:36` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runner_rights_gate.py:71` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runner_rights_gate.py:73` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runner_rights_gate.py:193` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runner_rights_gate.py:194` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runner_rights_gate.py:216` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runner_texture.py:1` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runner_texture.py:4` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runner_texture.py:27` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runner_texture.py:47` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runner_texture.py:49` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `moodify_runtime/tests/test_runner_texture.py:153` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `outputs/deepseek_validation/DSK-MFY-SCORE-ENGINE-009/stage3_e2e.py:33` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `outputs/deepseek_validation/DSK-MFY-SCORE-ENGINE-009/stage3_e2e.py:40` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/deepseek_worker_client.py:102` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/download_cloud_data.py:19` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/download_cloud_data.py:21` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/download_cloud_data.py:28` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/golden_runtime_exercise.py:16` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `scripts/golden_runtime_exercise.py:56` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/studio_session_prep/test_hash_safety.py:5` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/studio_session_prep/test_wse_profile.py:302` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/studio_session_prep/test_wse_profile.py:303` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_backfill_loader.py:3` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_backfill_loader.py:14` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_backfill_loader.py:25` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_backfill_loader.py:36` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_backfill_loader.py:68` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_backfill_loader.py:84` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_benchmark_builder.py:3` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_benchmark_builder.py:47` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_comparison_report.py:3` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_comparison_report.py:77` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_craft_evidence.py:3` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_craft_evidence.py:62` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_deepseek_worker_client.py:3` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_deepseek_worker_client.py:19` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_deepseek_worker_client.py:28` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_deepseek_worker_client.py:41` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_deepseek_worker_client.py:50` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_deepseek_worker_client.py:143` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_deepseek_worker_client.py:168` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_deepseek_worker_client.py:181` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_deepseek_worker_client.py:194` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_learning_store.py:3` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_learning_store.py:69` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_learning_store.py:78` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_learning_store.py:87` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_learning_store.py:96` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_learning_store.py:103` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_learning_store.py:114` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_learning_store.py:120` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_learning_surface.py:3` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_learning_surface.py:23` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_learning_surface.py:47` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_mainline_registry.py:2` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_mainline_registry.py:21` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_mainline_registry.py:30` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_mainline_registry.py:39` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_mainline_registry.py:50` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_mainline_registry.py:66` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_mainline_registry.py:78` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_mainline_registry.py:87` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_mainline_registry.py:94` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_mainline_registry.py:99` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_significance_evaluator.py:2` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_significance_evaluator.py:90` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_trend_analyzer.py:2` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_trend_analyzer.py:48` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_trend_analyzer.py:58` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tests/test_trend_analyzer.py:65` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tools/architecture/enforcer.py:62` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tools/architecture/enforcer.py:95` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tools/generate_midi_anchored_lrc.py:46` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tools/score_asset_pipeline.py:19` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tools/studio_session_prep/models.py:87` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tools/studio_session_prep/studio_prep.py:175` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tools/studio_session_prep/studio_prep.py:295` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tools/studio_session_prep/studio_prep.py:314` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tools/studio_session_prep/studio_prep.py:320` | Debt marker TEMP requires a reason and exit condition. |
| INFO | `TT-DEBT-MARKER` | `tools/studio_session_prep/studio_prep.py:323` | Debt marker TEMP requires a reason and exit condition. |
| WARNING | `TT-BROAD-EXCEPTION` | `apps/tools/audacity_cli.py:116` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:216` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:232` | Line length is 152 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:242` | Line length is 150 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:254` | Line length is 151 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:257` | Line length is 196 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:258` | Line length is 152 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:261` | Line length is 219 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:276` | Line length is 171 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:303` | Line length is 164 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:304` | Line length is 154 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:311` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:314` | Line length is 178 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:315` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:329` | Line length is 213 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:353` | Line length is 133 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:357` | Line length is 191 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:361` | Line length is 168 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:369` | Line length is 158 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:370` | Line length is 161 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:376` | Line length is 176 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:395` | Line length is 151 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:399` | Line length is 136 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:403` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:407` | Line length is 149 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:420` | Line length is 173 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:425` | Line length is 135 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:435` | Line length is 133 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:448` | Line length is 145 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/build_docx.py:479` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/generate_diagrams.py:44` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `docs/strategy/DOC-MFY-001/assets/generate_diagrams.py:69` | Function spans 65 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `docs/strategy/DOC-MFY-001/assets/generate_diagrams.py:137` | Function spans 63 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-001/assets/generate_diagrams.py:228` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `docs/strategy/DOC-MFY-003/assets/generate_diagrams.py:34` | Function spans 71 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `docs/strategy/DOC-MFY-003/assets/generate_diagrams.py:110` | Function spans 85 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `docs/strategy/DOC-MFY-003/assets/generate_diagrams.py:200` | Function spans 69 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `docs/strategy/DOC-MFY-003/executions/ACU-005/generate_limiter_ab.py:25` | Function spans 72 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `docs/strategy/DOC-MFY-003/generate_docx.py:572` | Line length is 152 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `experiments/engineering/EXP-ENG-001/code/analyze.py:64` | Function complexity proxy is 19; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `experiments/engineering/EXP-ENG-001/code/analyze.py:133` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `experiments/engineering/EXP-ENG-001/code/analyze.py:188` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `experiments/engineering/EXP-ENG-001/code/analyze.py:199` | Line length is 141 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `experiments/physics/EXP-PHYS-002/code/analyze.py:56` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `experiments/physics/EXP-PHYS-002/code/scan.py:30` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `experiments/physics/EXP-PHYS-002/code/scan.py:53` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-NESTING` | `experiments/validate_mrs_open_v03.py:131` | Maximum nesting depth is 6; failure and decision paths are compressed. |
| WARNING | `TT-COMPLEXITY` | `experiments/validate_mrs_open_v03.py:164` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `experiments/validate_mrs_open_v03.py:231` | Function spans 79 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `experiments/validate_mrs_open_v03.py:316` | Function spans 101 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `experiments/validate_mrs_open_v03.py:423` | Function spans 97 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `experiments/validate_mrs_open_v03.py:458` | Line length is 172 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `experiments/validate_mrs_open_v03.py:546` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `experiments/validate_mrs_open_v03.py:695` | Function complexity proxy is 15; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `experiments/validate_mrs_open_v03.py:695` | Function spans 72 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `experiments/validate_mrs_open_v03.py:740` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `experiments/validate_mrs_open_v03.py:773` | Function complexity proxy is 15; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `experiments/validate_mrs_open_v03.py:773` | Function spans 108 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `experiments/validate_mrs_open_v03.py:857` | Line length is 133 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `experiments/validate_mrs_open_v03.py:860` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `experiments/validate_mrs_open_v03.py:1064` | Line length is 134 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `experiments/validate_mrs_open_v03.py:1065` | Line length is 140 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `experiments/validate_mrs_open_v03.py:1066` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `experiments/validate_mrs_open_v03.py:1128` | Line length is 175 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `experiments/validate_mrs_open_v03.py:1263` | Line length is 161 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `experiments/validate_mrs_open_v03.py:1277` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `experiments/validate_mrs_open_v03.py:1351` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `experiments/validate_mrs_open_v03.py:1352` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `experiments/validate_mrs_open_v03.py:1460` | Line length is 172 characters; expression may be compressed. |
| WARNING | `TT-PARAMETERS` | `moodify-bridge/src/moodify_bridge/cli.py:119` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/cli.py:121` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/cli.py:123` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-bridge/src/moodify_bridge/cli.py:203` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-bridge/src/moodify_bridge/cli.py:249` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-bridge/src/moodify_bridge/cli.py:262` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/metrics.py:32` | Line length is 208 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/metrics.py:39` | Line length is 158 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/metrics.py:45` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/metrics.py:47` | Line length is 160 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/metrics.py:48` | Line length is 151 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/metrics.py:50` | Line length is 327 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/metrics.py:54` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/metrics.py:57` | Line length is 155 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/metrics.py:61` | Line length is 155 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/metrics.py:68` | Line length is 206 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/metrics.py:72` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/metrics.py:75` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/metrics.py:76` | Line length is 269 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/metrics.py:81` | Line length is 165 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/metrics.py:82` | Line length is 197 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/metrics.py:89` | Line length is 235 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/metrics.py:96` | Line length is 239 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/services.py:73` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-bridge/src/moodify_bridge/services.py:145` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-bridge/src/moodify_bridge/services.py:168` | Function complexity proxy is 19; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-bridge/src/moodify_bridge/services.py:264` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-bridge/src/moodify_bridge/services.py:279` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-bridge/src/moodify_bridge/services.py:286` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-bridge/src/moodify_bridge/services.py:294` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/services.py:332` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-bridge/src/moodify_bridge/services.py:335` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/services.py:338` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/services.py:339` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/services.py:341` | Line length is 205 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/services.py:347` | Line length is 137 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/services.py:348` | Line length is 161 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/services.py:357` | Line length is 309 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-bridge/src/moodify_bridge/services.py:364` | Function spans 74 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-bridge/src/moodify_bridge/services.py:463` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-bridge/src/moodify_bridge/services.py:473` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-bridge/src/moodify_bridge/services.py:500` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-bridge/src/moodify_bridge/services.py:534` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-bridge/src/moodify_bridge/services.py:562` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-bridge/src/moodify_bridge/services.py:578` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-bridge/src/moodify_bridge/services.py:598` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-bridge/src/moodify_bridge/services.py:723` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-NESTING` | `moodify-bridge/src/moodify_bridge/services.py:818` | Maximum nesting depth is 6; failure and decision paths are compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-bridge/src/moodify_bridge/services.py:913` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-COMPLEXITY` | `moodify-bridge/src/moodify_bridge/services.py:970` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-bridge/src/moodify_bridge/services.py:970` | Function spans 100 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/store.py:29` | Line length is 133 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/store.py:40` | Line length is 169 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/store.py:41` | Line length is 133 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/store.py:50` | Line length is 188 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/store.py:70` | Line length is 232 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/store.py:75` | Line length is 146 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/store.py:81` | Line length is 218 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/store.py:86` | Line length is 167 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/src/moodify_bridge/store.py:92` | Line length is 177 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-bridge/tests/test_store_workflow.py:14` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/adapters/audacity/client.py:41` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/adapters/audacity/client.py:73` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/adapters/audacity/runtime.py:100` | Function spans 73 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/adapters/audacity/runtime.py:163` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/adapters/audacity/runtime.py:170` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/adapters/open_source_toolchain.py:24` | Line length is 132 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/adapters/open_source_toolchain.py:83` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/adapters/open_source_toolchain.py:87` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/adapters/open_source_toolchain.py:107` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/adapters/open_source_toolchain.py:110` | Line length is 136 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/app/engines.py:47` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/app/engines.py:47` | Function spans 85 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/app/engines.py:108` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/app/evidence.py:24` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/app/evidence.py:31` | Line length is 305 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/app/orchestrator.py:36` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/app/orchestrator.py:44` | Line length is 142 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/app/orchestrator.py:45` | Line length is 180 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/app/orchestrator.py:46` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/app/orchestrator.py:49` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/app/orchestrator.py:52` | Line length is 175 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/app/orchestrator.py:83` | Line length is 172 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/app/production_control.py:102` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/app/production_control.py:181` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/app/production_control.py:607` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/app/production_control.py:607` | Function spans 72 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/app/production_control.py:635` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/app/production_control.py:682` | Function spans 78 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/app/production_control.py:767` | Function complexity proxy is 17; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/app/production_control.py:842` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/capability_registry/adapters/base.py:77` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/capability_registry/adapters/base.py:177` | Function spans 82 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/capability_registry/adapters/basic_pitch_adapter.py:56` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/capability_registry/adapters/basic_pitch_adapter.py:56` | Function spans 63 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/capability_registry/adapters/basic_pitch_adapter.py:97` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/capability_registry/adapters/cli.py:32` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/capability_registry/bootstrap.py:29` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/capability_registry/bootstrap.py:76` | Function spans 87 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/capability_registry/bootstrap.py:151` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/capability_registry/bootstrap.py:153` | Line length is 125 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/capability_registry/bootstrap.py:154` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/capability_registry/cli.py:91` | Line length is 180 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/capability_registry/knowledge/policy.py:99` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/capability_registry/knowledge/policy.py:141` | Function has 9 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/capability_registry/knowledge/records.py:173` | Function has 9 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli_daw/adapters/matchering.py:33` | Line length is 137 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/cli_daw/adapters/matchering.py:34` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/cli_daw/adapters/rubberband.py:30` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli_daw/adapters/rubberband.py:37` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli_daw/adapters/rubberband.py:46` | Line length is 206 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/cli_daw/adapters/rubberband.py:47` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli_daw/adapters/sox.py:30` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/cli_daw/adapters/sox.py:31` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-NESTING` | `moodify-core-package/src/moodify/cli_daw/adapters/sox.py:36` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli_daw/adapters/sox.py:46` | Line length is 188 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/cli_daw/adapters/sox.py:53` | Line length is 199 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/cli_daw/adapters/sox.py:54` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/cli_daw/engine_ffmpeg.py:73` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/cli_daw/engine_native.py:102` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-NESTING` | `moodify-core-package/src/moodify/cli_daw/engine_native.py:113` | Maximum nesting depth is 6; failure and decision paths are compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/cli_daw/project.py:78` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/craft_slider.py:51` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/craft_slider.py:60` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/craft_slider.py:198` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/craft_slider.py:255` | Line length is 132 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/craft_slider.py:272` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/features/f0.py:153` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/features/f0.py:262` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/features/perceptual.py:241` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:396` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:432` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:457` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:485` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:494` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:559` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:583` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:612` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:676` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:747` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:758` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/orchestration/workflow_engine.py:792` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/perception/masking.py:321` | Function spans 70 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/processing/limiter.py:177` | Function spans 114 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `moodify-core-package/src/moodify/processing/limiter.py:177` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/processing/rbj_eq.py:190` | Function spans 61 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/processing/tight_focus.py:258` | Function spans 61 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/score_engine/cli.py:35` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/score_engine/midi_ingest.py:106` | Function spans 89 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `moodify-core-package/src/moodify/score_engine/midi_ingest.py:197` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/score_engine/midi_ingest.py:333` | Line length is 141 characters; expression may be compressed. |
| WARNING | `TT-NESTING` | `moodify-core-package/src/moodify/score_engine/musescore_backend.py:116` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/score_engine/musescore_backend.py:129` | Function spans 69 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/score_engine/musescore_backend.py:190` | Line length is 134 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/score_engine/musescore_backend.py:192` | Line length is 139 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/score_engine/musescore_backend.py:194` | Line length is 135 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/score_engine/serialization.py:96` | Line length is 136 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/src/moodify/score_engine/serialization.py:230` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/transcription.py:83` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify-core-package/src/moodify/transcription_pipeline/midi_cleanup.py:66` | Function spans 106 lines; review responsibility boundaries. |
| WARNING | `TT-NESTING` | `moodify-core-package/src/moodify/transcription_pipeline/midi_cleanup.py:66` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/v01_delivery.py:36` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/v01_delivery.py:44` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/v01_delivery.py:115` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/v01_delivery.py:128` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/v01_pipeline.py:198` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/v01_pipeline.py:291` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/v01_pipeline.py:300` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/v01_pipeline.py:341` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/src/moodify/v01_pipeline.py:496` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/capability_registry/test_execution.py:55` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/capability_registry/test_knowledge.py:69` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/capability_registry/test_validation.py:39` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/cli_v2/test_cli_v2_closed_loop.py:83` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/cli_v2/test_cli_v2_closed_loop.py:93` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/cli_v2/test_cli_v2_closed_loop.py:107` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/cli_v2/test_cli_v2_closed_loop.py:129` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/cli_v2/test_cli_v2_closed_loop.py:138` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify-core-package/tests/score_engine/test_musescore_backend.py:40` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/score_engine/test_musescore_backend.py:190` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify-core-package/tests/test_production_runtime.py:425` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/backfill_loader.py:59` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/benchmark_builder.py:96` | Function has 9 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/cli.py:121` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/cli.py:301` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/cli.py:307` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/cli.py:435` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/cli.py:467` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/cli.py:487` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/cli.py:536` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/cli.py:536` | Function spans 64 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/cli.py:602` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/cli.py:622` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/cli.py:648` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/cli.py:648` | Function spans 86 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/comparison_report.py:57` | Function spans 67 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_evidence.py:100` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:686` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:701` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:728` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:738` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:752` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:766` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:780` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:794` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:806` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:819` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:831` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:844` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:856` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:873` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/craft_processes.py:883` | Line length is 128 characters; expression may be compressed. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:894` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:912` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:930` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/craft_processes.py:934` | Line length is 123 characters; expression may be compressed. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:944` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:952` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:962` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:971` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/craft_processes.py:990` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/craft_processes.py:1063` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/craft_processes.py:1077` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/data_asset.py:224` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/data_asset.py:224` | Function spans 64 lines; review responsibility boundaries. |
| WARNING | `TT-NESTING` | `moodify_runtime/data_asset.py:396` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/fusion_scorer.py:93` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/fusion_scorer.py:163` | Function spans 66 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/fusion_scorer.py:262` | Line length is 142 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/fusion_scorer.py:263` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/hardening_gates.py:18` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/hardening_gates.py:18` | Function spans 75 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/learning_store.py:84` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/learning_surface.py:23` | Function spans 94 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/mainline_registry.py:42` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/mainline_registry.py:66` | Function has 8 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/mrs_surface.py:118` | Function complexity proxy is 18; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/mrs_surface.py:118` | Function spans 86 lines; review responsibility boundaries. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/mrs_surface.py:118` | Function has 9 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/operator_console.py:939` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/operator_console.py:989` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/operator_console.py:1035` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/operator_console.py:1059` | Line length is 124 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/operator_console.py:1286` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/runner.py:68` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/runner.py:89` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/runner.py:89` | Function spans 78 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/runner.py:115` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/runner.py:169` | Function has 9 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-PARAMETERS` | `moodify_runtime/runner.py:227` | Function has 7 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-COMPLEXITY` | `moodify_runtime/runner.py:266` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/runner.py:266` | Function spans 108 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/runner.py:299` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `moodify_runtime/runner.py:462` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `moodify_runtime/significance_evaluator.py:118` | Function spans 81 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `moodify_runtime/tests/test_runner_rights_gate.py:592` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `scripts/data_asset_backfill.py:25` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-NESTING` | `scripts/data_asset_backfill.py:25` | Maximum nesting depth is 6; failure and decision paths are compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `scripts/data_asset_backfill.py:47` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `scripts/deepseek_worker_client.py:56` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-PARAMETERS` | `scripts/deepseek_worker_client.py:113` | Function has 9 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-BROAD-EXCEPTION` | `scripts/deepseek_worker_client.py:147` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `scripts/download_cloud_data.py:47` | Line length is 189 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/golden_runtime_exercise.py:43` | Function spans 63 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `scripts/golden_runtime_exercise.py:126` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `scripts/moodify_deep_ear.py:31` | Function spans 88 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `scripts/moodify_deep_ear.py:158` | Line length is 126 characters; expression may be compressed. |
| WARNING | `TT-BROAD-EXCEPTION` | `scripts/verify_exported_master.py:55` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `tests/test_deepseek_worker_client.py:64` | Line length is 122 characters; expression may be compressed. |
| WARNING | `TT-NESTING` | `tools/architecture/budget.py:41` | Maximum nesting depth is 5; failure and decision paths are compressed. |
| WARNING | `TT-FUNCTION-LENGTH` | `tools/architecture/budget.py:82` | Function spans 100 lines; review responsibility boundaries. |
| WARNING | `TT-NESTING` | `tools/architecture/budget.py:82` | Maximum nesting depth is 6; failure and decision paths are compressed. |
| WARNING | `TT-LINE-LENGTH` | `tools/architecture/budget.py:191` | Line length is 134 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `tools/architecture/enforcer.py:60` | Line length is 136 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `tools/architecture/enforcer.py:61` | Line length is 139 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `tools/architecture/enforcer.py:62` | Line length is 133 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `tools/architecture/enforcer.py:63` | Line length is 134 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `tools/architecture/enforcer.py:64` | Line length is 132 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `tools/architecture/enforcer.py:65` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `tools/architecture/enforcer.py:66` | Line length is 129 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `tools/architecture/enforcer.py:67` | Line length is 135 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `tools/architecture/enforcer.py:68` | Line length is 133 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `tools/architecture/enforcer.py:79` | Function complexity proxy is 18; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `tools/architecture/enforcer.py:79` | Function spans 69 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `tools/generate_midi_anchored_lrc.py:77` | Function complexity proxy is 16; branch pressure may hide decisions. |
| WARNING | `TT-COMPLEXITY` | `tools/project_governance/gate.py:43` | Function complexity proxy is 18; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `tools/project_governance/gate.py:43` | Function spans 62 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `tools/project_governance/import_tasks.py:55` | Function spans 64 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `tools/project_governance/inventory.py:37` | Function complexity proxy is 19; branch pressure may hide decisions. |
| WARNING | `TT-LINE-LENGTH` | `tools/project_governance/inventory.py:53` | Line length is 143 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `tools/project_governance/inventory.py:76` | Function complexity proxy is 15; branch pressure may hide decisions. |
| WARNING | `TT-PARAMETERS` | `tools/project_governance/ledger.py:99` | Function has 9 declared parameters; implicit context may need a named structure. |
| WARNING | `TT-COMPLEXITY` | `tools/project_governance/ledger.py:124` | Function complexity proxy is 15; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `tools/project_governance/observability.py:42` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `tools/run_audacity_stage.py:39` | Function spans 72 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `tools/score_asset_pipeline.py:49` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `tools/studio_session_prep/candidate_adapter.py:58` | Function spans 79 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `tools/studio_session_prep/candidate_adapter.py:123` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-LINE-LENGTH` | `tools/studio_session_prep/candidate_plan.py:186` | Line length is 121 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `tools/studio_session_prep/candidate_plan.py:203` | Line length is 127 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `tools/studio_session_prep/candidate_plan.py:206` | Line length is 131 characters; expression may be compressed. |
| WARNING | `TT-LINE-LENGTH` | `tools/studio_session_prep/candidate_plan.py:214` | Line length is 130 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `tools/studio_session_prep/reporting.py:28` | Function complexity proxy is 15; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `tools/studio_session_prep/reporting.py:28` | Function spans 74 lines; review responsibility boundaries. |
| WARNING | `TT-COMPLEXITY` | `tools/studio_session_prep/reporting.py:104` | Function complexity proxy is 18; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `tools/studio_session_prep/studio_prep.py:79` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `tools/studio_session_prep/studio_prep.py:116` | Function complexity proxy is 19; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `tools/studio_session_prep/studio_prep.py:141` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `tools/studio_session_prep/studio_prep.py:162` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `tools/studio_session_prep/studio_prep.py:178` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `tools/studio_session_prep/studio_prep.py:187` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `tools/studio_session_prep/studio_prep.py:195` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `tools/studio_session_prep/studio_prep.py:262` | Function spans 69 lines; review responsibility boundaries. |
| WARNING | `TT-LINE-LENGTH` | `tools/studio_session_prep/studio_prep.py:265` | Line length is 134 characters; expression may be compressed. |
| WARNING | `TT-COMPLEXITY` | `tools/studio_session_prep/studio_prep.py:334` | Function complexity proxy is 14; branch pressure may hide decisions. |
| WARNING | `TT-FUNCTION-LENGTH` | `tools/studio_session_prep/studio_prep.py:334` | Function spans 80 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `tools/studio_session_prep/studio_prep.py:349` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `tools/studio_session_prep/studio_prep.py:379` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `tools/studio_session_prep/studio_prep.py:420` | Function spans 74 lines; review responsibility boundaries. |
| WARNING | `TT-FUNCTION-LENGTH` | `tools/studio_session_prep/studio_prep.py:535` | Function spans 70 lines; review responsibility boundaries. |
| WARNING | `TT-BROAD-EXCEPTION` | `tools/studio_session_prep/studio_prep.py:571` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-COMPLEXITY` | `tools/studio_session_prep/studio_prep.py:664` | Function complexity proxy is 13; branch pressure may hide decisions. |
| WARNING | `TT-BROAD-EXCEPTION` | `tools/studio_session_prep/studio_prep.py:685` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `tools/studio_session_prep/wse_profile.py:157` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `tools/studio_session_prep/wse_profile.py:209` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-BROAD-EXCEPTION` | `tools/xhs_compare_video/generate_xhs_compare_video.py:260` | Broad exception handler requires contextual logging, rethrowing, or a documented boundary. |
| WARNING | `TT-FUNCTION-LENGTH` | `tools/xhs_compare_video/generate_xhs_compare_video.py:272` | Function spans 73 lines; review responsibility boundaries. |

## Resolved findings

- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:395` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:408` `TT-COMPLEXITY` — Function complexity proxy is 23; branch pressure may hide decisions.
- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:408` `TT-FUNCTION-LENGTH` — Function spans 69 lines; review responsibility boundaries.
- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:426` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:450` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:473` `TT-LINE-LENGTH` — Line length is 124 characters; expression may be compressed.
- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:475` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:484` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:484` `TT-EMPTY-EXCEPTION` — Empty exception handler hides failure evidence.
- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:547` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:547` `TT-EMPTY-EXCEPTION` — Empty exception handler hides failure evidence.
- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:571` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:600` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:629` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:629` `TT-EMPTY-EXCEPTION` — Empty exception handler hides failure evidence.
- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:639` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:639` `TT-EMPTY-EXCEPTION` — Empty exception handler hides failure evidence.
- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:728` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:739` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:773` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/v01_delivery.py:33` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/v01_delivery.py:41` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/v01_delivery.py:112` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/v01_delivery.py:112` `TT-EMPTY-EXCEPTION` — Empty exception handler hides failure evidence.
- `moodify-core-package/src/moodify/v01_delivery.py:125` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/v01_delivery.py:125` `TT-EMPTY-EXCEPTION` — Empty exception handler hides failure evidence.
- `moodify-core-package/src/moodify/v01_delivery.py:141` `TT-EMPTY-EXCEPTION` — Empty exception handler hides failure evidence.
- `moodify-core-package/src/moodify/v01_pipeline.py:199` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/v01_pipeline.py:278` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/v01_pipeline.py:278` `TT-EMPTY-EXCEPTION` — Empty exception handler hides failure evidence.
- `moodify-core-package/src/moodify/v01_pipeline.py:287` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/v01_pipeline.py:328` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify-core-package/src/moodify/v01_pipeline.py:328` `TT-EMPTY-EXCEPTION` — Empty exception handler hides failure evidence.
- `moodify-core-package/src/moodify/v01_pipeline.py:371` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify-core-package/src/moodify/v01_pipeline.py:412` `TT-PARAMETERS` — Function has 11 declared parameters; implicit context may need a named structure.
- `moodify-core-package/src/moodify/v01_pipeline.py:469` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify_runtime/cli.py:73` `TT-FUNCTION-LENGTH` — Function spans 342 lines; review responsibility boundaries.
- `moodify_runtime/cli.py:115` `TT-LINE-LENGTH` — Line length is 130 characters; expression may be compressed.
- `moodify_runtime/cli.py:335` `TT-LINE-LENGTH` — Line length is 121 characters; expression may be compressed.
- `moodify_runtime/cli.py:341` `TT-LINE-LENGTH` — Line length is 121 characters; expression may be compressed.
- `moodify_runtime/cli.py:417` `TT-COMPLEXITY` — Function complexity proxy is 101; branch pressure may hide decisions.
- `moodify_runtime/cli.py:417` `TT-FUNCTION-LENGTH` — Function spans 472 lines; review responsibility boundaries.
- `moodify_runtime/cli.py:423` `TT-LINE-LENGTH` — Line length is 124 characters; expression may be compressed.
- `moodify_runtime/cli.py:538` `TT-LINE-LENGTH` — Line length is 131 characters; expression may be compressed.
- `moodify_runtime/cli.py:845` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/cli.py:870` `TT-LINE-LENGTH` — Line length is 129 characters; expression may be compressed.
- `moodify_runtime/craft_processes.py:685` `TT-COMPLEXITY` — Function complexity proxy is 47; branch pressure may hide decisions.
- `moodify_runtime/craft_processes.py:685` `TT-FUNCTION-LENGTH` — Function spans 335 lines; review responsibility boundaries.
- `moodify_runtime/craft_processes.py:685` `TT-NESTING` — Maximum nesting depth is 23; failure and decision paths are compressed.
- `moodify_runtime/craft_processes.py:718` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify_runtime/craft_processes.py:777` `TT-LINE-LENGTH` — Line length is 125 characters; expression may be compressed.
- `moodify_runtime/craft_processes.py:779` `TT-LINE-LENGTH` — Line length is 121 characters; expression may be compressed.
- `moodify_runtime/craft_processes.py:864` `TT-LINE-LENGTH` — Line length is 127 characters; expression may be compressed.
- `moodify_runtime/craft_processes.py:905` `TT-LINE-LENGTH` — Line length is 136 characters; expression may be compressed.
- `moodify_runtime/craft_processes.py:929` `TT-LINE-LENGTH` — Line length is 153 characters; expression may be compressed.
- `moodify_runtime/craft_processes.py:945` `TT-LINE-LENGTH` — Line length is 139 characters; expression may be compressed.
- `moodify_runtime/craft_processes.py:952` `TT-LINE-LENGTH` — Line length is 131 characters; expression may be compressed.
- `moodify_runtime/craft_processes.py:957` `TT-LINE-LENGTH` — Line length is 127 characters; expression may be compressed.
- `moodify_runtime/craft_processes.py:958` `TT-LINE-LENGTH` — Line length is 130 characters; expression may be compressed.
- `moodify_runtime/craft_processes.py:972` `TT-LINE-LENGTH` — Line length is 127 characters; expression may be compressed.
- `moodify_runtime/craft_processes.py:978` `TT-LINE-LENGTH` — Line length is 128 characters; expression may be compressed.
- `moodify_runtime/craft_processes.py:1018` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify_runtime/operator_console.py:399` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/operator_console.py:693` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/operator_console.py:702` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/operator_console.py:764` `TT-FUNCTION-LENGTH` — Function spans 179 lines; review responsibility boundaries.
- `moodify_runtime/operator_console.py:860` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify_runtime/operator_console.py:955` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/operator_console.py:975` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/operator_console.py:977` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/operator_console.py:980` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/operator_console.py:983` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify_runtime/operator_console.py:987` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/operator_console.py:1006` `TT-COMPLEXITY` — Function complexity proxy is 14; branch pressure may hide decisions.
- `moodify_runtime/operator_console.py:1006` `TT-FUNCTION-LENGTH` — Function spans 161 lines; review responsibility boundaries.
- `moodify_runtime/operator_console.py:1086` `TT-LINE-LENGTH` — Line length is 124 characters; expression may be compressed.
- `moodify_runtime/operator_console.py:1258` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify_runtime/runner.py:21` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:29` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:67` `TT-COMPLEXITY` — Function complexity proxy is 39; branch pressure may hide decisions.
- `moodify_runtime/runner.py:67` `TT-NESTING` — Maximum nesting depth is 5; failure and decision paths are compressed.
- `moodify_runtime/runner.py:127` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:150` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:162` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:163` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:164` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify_runtime/runner.py:165` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:193` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:205` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:221` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:223` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:225` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:230` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:232` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:233` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.
- `moodify_runtime/runner.py:234` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:239` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:240` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:258` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:273` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:274` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:276` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:320` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:321` `TT-DEBT-MARKER` — Debt marker TEMP requires a reason and exit condition.
- `moodify_runtime/runner.py:366` `TT-BROAD-EXCEPTION` — Broad exception handler requires contextual logging, rethrowing, or a documented boundary.


## Analysis (Claude, 2026-08-04)

The 714 "new" findings are dominated by baseline scope asymmetry, not regressions:

- Before baseline was audited from a git worktree at HEAD (tracked files only, 335 files);
  after covers the full working tree (566 files) including new characterization tests and
  previously untracked modules (moodify-bridge/, transcription_pipeline/, etc.).
- services.py added a module logger at the top; line-number-embedding fingerprints
  (TT-BROAD-EXCEPTION / TT-EMPTY-EXCEPTION) re-attribute pre-existing findings as new.
- New warnings from explicit-failure conversions are accepted (principle 4: failure is
  first-class evidence).

New ERROR-level findings in the 8 wave modules: **0**. The 41 guard-listed errors are all
scope artifacts (untracked files absent from baseline) or line-shift re-attributes.
See VERIFICATION.md and CHANGELOG.md for per-module truth.
