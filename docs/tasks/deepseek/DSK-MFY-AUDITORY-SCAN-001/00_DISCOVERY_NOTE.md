# DSK-MFY-AUDITORY-SCAN-001｜Repository Discovery Note

## 可复用资产（已确认存在）

1. **CLI v2**：`moodify/cli_v2/main.py`，argparse + `handlers` dict（"case.verify"→cmd），`_result()` JSON 输出，`CLIError(code,message,exit_code,payload)`。
2. **Case 生命周期**：`moodify/app/production_control.py` — `CaseState` 状态机（CREATED→SOURCE_REGISTERED→SPECIFIED→ANALYZED→PLANNED→TECHNICALLY_VALIDATED→AWAITING_ARTISTIC_APPROVAL→APPROVED→EXECUTING→EXECUTED→VERIFYING→VERIFIED→PACKAGED→COMPLETED），`ProductionCase`（register_source/specify/analyze/set_plan/run_technical_gate/approve），`ProductionCaseStore`（case 目录原子写），`ProductionControlService`。
3. **Evidence**：`moodify/app/evidence.py`（EvidenceBundle/aggregate_evidence/write_evidence_bundle）+ `ProductionControlService.package()` 的 evidence_manifest.json 全链路 sha256 模式。
4. **ApprovedExecutionEnvelope**：frozen dataclass + `_build_envelope()` + `ExecutionEngine` Protocol（引擎不改 case 状态）。
5. **Verification**：`ProductionControlService.verify()` → VerificationResult（PASS/FAIL，源 hash/引擎身份/plan 身份/基础音频检查）。
6. **FFmpeg 包装**：`capability_registry/adapters/ffmpeg_adapter.py`（ControlledProcessAdapter：纯 argv 无 shell、WinGet 探测、AdapterResult 错误模式）。
7. **音频分析**：`v01_analyzer.analyze`（AudioMetrics 7 段）、`bands.py`、`reality_metrics`、`mrs_adapter.score_for_quality_gate`。
8. **错误分类**：`ErrorClass` taxonomy（invalid_input/provider_defect/environment_failure/timeout/partial_output/policy_rejection）+ KNOWN_FAILURE_MODES；控制面 ControlError/CLIError。
9. **测试约定**：conftest `mock_audio`（440/554Hz 立体声正弦）+ `mock_wav`；tests/cli_v2/ 全流程参考。
10. **数据布局**：`project_dir/cases/<case_id>/`（case.json + output/ + evidence/）。

## 集成决策

- 新包 `moodify/auditory/`（models/profiles/decode/spectrogram/metrics/timeline/stereo/comparison/judgment/reports/manifests/errors）。
- CLI 命令 `case scan / case candidate register / case compare` 接入 cli_v2 handlers。
- before scan → `ProductionCase.analyze`（ANALYZED）；plan → set_plan（PLANNED）；candidate 经 ExecutionEngine 路径（EXECUTING/EXECUTED）；after scan + compare → verify 流程（VERIFYING→VERIFIED）。
- 证据写入复用 evidence_manifest.json 哈希模式；不建并行 case 系统、不加新生命周期状态。
- 响度：自研 BS.1770 K-weighting（pedalboard LoudnessMeter 本版本不可用）。
- 频谱主证据：ffmpeg showspectrumpic（线性/对数双视图）；数值 STFT 自研（numpy/hann，确定性）。
