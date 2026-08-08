# AB_AUDIT_BEFORE — Pairwise Auditory Judge 审计基线

任务：DSK-MFY-PAIRWISE-JUDGE-001
日期：2026-08-08
状态：Phase 0（变更前撰写）

## 1. 运行时/栈检测

- **core**：Python 3.11，moodify CLI v2 + FastAPI（/api/v1 15 端点）
- **Android**：Kotlin + Compose，4-tab（首页/听觉检测/案例/我的）+ WorkDetailScreen A/B 播放
- **分析管线**：`auditory/service.py::scan_audio`（46+ 指标）+ `comparison.py::compute_deltas`（响度归一化）+ `judgment.py`（13 风险码）
- **学习**：`learning/models.py::PairwisePreference`（7 字段）+ `CaseLearningStore.append_preference`（09_learning/pairwise_preferences.jsonl）+ `export_learning_records`

## 2. 可复用面（不重复造轮子）

| 规格维度 | 复用指标 | 来源 |
|---|---|---|
| Signal integrity | clipping_sample_ratio / near_clipping / invalid_sample_count / finite_sample_ratio / silence_ratio / true_peak_dbfs | auditory metrics |
| Loudness | integrated_lufs / sample_peak_dbfs | auditory metrics |
| Dynamics | crest_factor_db / loudness_range_lu / plr_db | auditory metrics |
| Spectral balance | 9 频段比例 / spectral_flatness / hf_cutoff / noise_floor | auditory metrics |
| Stereo/phase | stereo_correlation / negative_correlation_ratio / side_to_mid_db / phase_risk_ratio（mono→INSUFFICIENT） | stereo.py |
| 持久化 | 06_pairwise/*.json + CaseLearningStore | — |
| 黄金案例 | run_golden.py 确定性合成模式 | auditory |

## 3. 缺口（本任务实现）

- 无 pairwise 领域模型/比较引擎/决策策略（evaluation/judges.py 是情绪三评委，不适用）
- `PairwisePreference` 缺 label_source/machine_outcome/machine_confidence/eligible_for_training
- 无 CLI 命令、无 API 端点、无 Android 判断 UI
- transient/residual 维度无检测器（→ INSUFFICIENT_EVIDENCE）

## 4. 基线扫描

- `scan_ab_scope.py src/moodify`：380 命中（现有 comparison/judge 词汇，无 pairwise 引擎）
- 既有测试：core 全量 793 绿；Android JVM 41 绿
