# DSK-MFY-AUDITORY-SCAN-001｜Final Codex Response

## 1. Implementation Verdict

**COMPLETED** — 完整 golden before/after 证据循环实际跑通，全部产出生成并通过证据校验。

## 2. Repository Discovery

- CLI v2：`moodify/cli_v2/main.py`（argparse + handlers dict + `_result` JSON）
- Case 生命周期：`moodify/app/production_control.py`（CaseState 状态机 + ProductionCase + ProductionControlService）
- Evidence：`moodify/app/evidence.py` + package() 的 evidence_manifest.json 全链路 sha256 模式
- ApprovedExecutionEnvelope / ExecutionEngine Protocol / verify() 均存在
- FFmpeg 包装：capability_registry/adapters（纯 argv 无 shell）
- 音频分析：v01_analyzer / bands / reality_metrics / mrs_adapter
- 测试约定：conftest mock_audio + tests/cli_v2 全流程参考
- 发现笔记：`docs/tasks/deepseek/DSK-MFY-AUDITORY-SCAN-001/00_DISCOVERY_NOTE.md`

## 3. Architecture Added

`moodify/auditory/`（13 模块）：models / profiles / decode / spectrogram / metrics /
timeline / stereo / comparison / judgment / reports / manifests / errors / service
（+ run_golden.py）。复用现有 case 目录（`project_dir/cases/<case_id>/`），未建并行
case 系统、未加新生命周期状态。

## 4. CLI Commands

```bash
python -m moodify case scan <proj> <case> --stage before|after --input <wav>
python -m moodify case candidate register <proj> <case> --candidate-id K --input <wav>
python -m moodify case compare <proj> <case> --candidate-id K --plan <plan.json>
```

输出：AUDITORY_BEFORE_SCAN_COMPLETED / CANDIDATE_REGISTERED /
AUDITORY_AFTER_SCAN_COMPLETED / AUDITORY_COMPARISON_COMPLETED。

## 5. Scan Profile

`MFY-WSE-SCAN-PROFILE-001`：48kHz、float32、1600x760 showspectrumpic（viridis/log/120dB
范围）、线性+对数双视图、STFT 8192/2048/hann、1s 时间窗。canonical JSON + SHA-256。

## 6. Metrics Implemented

- 文件元数据（sha256/时长/容器/codec/采样率/位深/声道）
- 响度：integrated_lufs（BS.1770 K-weighting）、loudness_range_lu、true_peak（4x）、
  sample_peak、rms、crest、plr
- 完整性：clipping/near-clipping、dc offset、silence、invalid/finite
- 频谱：centroid、rolloff 85/95、flatness、flux、HF cutoff、noise floor
- 9 段归一化频带比例 + 绝对能量（用于归一化比较）
- 立体声：correlation、mid/side、width、negative-corr、phase-risk（mono 置 null）
- timeline_metrics.jsonl（窗口级）

## 7. Comparison Method

- 验证：case/profile hash/时长（0.05s 容差）/声道，不匹配失败关闭
- 原始 delta + **响度归一化 delta**（能量域 gain² 重算比例）
- delta 频谱图从 STFT 数值生成（非 PNG 减法），线性/对数双视图
- 四图对比表（before/after × linear/log）

## 8. Judgment Rules

- technical_assessment：IMPROVED/NEUTRAL/DEGRADED/UNCERTAIN/INVALID_COMPARISON
- workflow_decision：PASS_TO_LISTENING/NEEDS_REWORK/REJECT_TECHNICAL/INCONCLUSIVE/INVALID
- 16 个风险标志（BLOCKING→REJECT_TECHNICAL；阈值版本化记录）
- 每个报告：human_listening_required: true、artistic_approval_granted: false
- 无 plan → 只描述变化，UNCERTAIN/INCONCLUSIVE

## 9. Golden Case Result

`outputs/auditory_golden/`：合成源+候选 → before scan → 候选注册 → after scan →
plan（presence 目标+无削波护栏）→ compare → **IMPROVED / PASS_TO_LISTENING** →
证据复核通过（全部 manifest 哈希一致）。

## 10. Tests Executed

23 passed（tests/auditory/，warnings-as-errors 模式）；既有 cli_v2 19 passed 无回归。
14 个合成 fixture（silence/sine mono+stereo/clipped/DC/LF/HF/band-limited/antiphase/
compressed/loudness-gain/EQ-change/duration-mismatch/corrupt）。

## 11. Evidence Bundle Paths

- `outputs/auditory_golden/cases/MFY-CASE-GOLDEN-001/01_before_scan/`
- `.../03_processing/candidates/GOLDEN-001.json`
- `.../04_after_scan/`
- `.../05_comparison/`（metrics_delta、双 delta 图、contact sheet、report、judgment_rules、manifest）
- `outputs/auditory_golden/golden_summary.json`

## 12. Files Changed

22 files, +3375 行（commit 5452ff4）：moodify/auditory 13 模块、cli_v2/main.py、
tests/auditory 3 文件、docs/auditory/README.md、discovery note、GOLDEN_CASE_SCRIPT.md。

## 13. Known Limitations

- LUFS/true-peak 为自研近似（48k 系数、4x 过采样），与商业仪表差 0.1-0.3
- delta 频谱图为 256-bin 降采样视图（人工复核用途）
- 仅 Windows + ffmpeg 8.x；cli_v2/main.py 既有分号风格保留（E702 为存量）
- 无 plan 时保守（UNCERTAIN）为设计决策

## 14. Remaining Risks

- BS.1770 与商业仪表未做交叉校准（建议后续用参考素材对标）
- 立体声 phase-risk 阈值为初版（0.7 相关 / 3x side 能量），需真实曲目校准
- 大文件（>10min）流式已按帧处理，但 metrics 的 frame 列表有内存上限风险

## 15. Final Status

**COMPLETED** — 20 项 Definition of Done 全部满足：CLI 可扫、双频谱图、
完整指标、候选注册（无 Audacity 集成）、同 profile 双扫、原始+归一化区分、
数值 delta 图、四图对比、目标/护栏评估、保守判断、艺术审批恒 false、
全证据哈希、既有生命周期未破坏、源文件未覆盖、测试全绿、文档完整、
golden bundle 生成且证据验证通过。
