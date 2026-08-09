# NTRACK_AUDIT_BEFORE — N 轨排名实施前审计

任务：DSK-MFY-NTRACK-RANKER-001
日期：2026-08-09

## 运行时 / 栈

- Python 3.11 + moodify-core-package（v2.0.0，canonical 身份 "The Ear of AI"）
- 决策/比较引擎：`moodify/evaluation/pairwise/`（DSK-MFY-PAIRWISE-JUDGE-001，26 测试绿）
- 分析管线：`moodify/auditory/service.py` 的 `scan_audio` + `load_scan_evidence`（53 指标，profile MFY-WSE-SCAN-PROFILE-001）
- 学习存储：`moodify/learning/store.py` 的 `CaseLearningStore`（PairwisePreference）
- CLI：`cli_v2/main.py`（case 子命令），API：FastAPI `/api/v1`（mobile v1 契约）

## 复用面确认

| 面 | 现状 | 复用决策 |
|---|---|---|
| Pairwise Judge | `run_pairwise_judge` / `compare_dimensions` / `decide` / `DecisionPolicy` | 复用比较与决策（不重复实现维度逻辑） |
| 规范分析 | `scan_audio` + `load_scan_evidence`（每次/每版本一次） | 复用 + 按 source hash 缓存 |
| 学习记录 | `PairwisePreference`（label_source/eligible_for_training） | 复用派生 preference 落盘 |
| 错误契约 | mobile v1（400 + error.code） | 沿用 |

## 关键事实（预检）

- `load_scan_evidence` 要求 `metrics.json` + `analysis_data.npz`（**非 evidence.json**——实现时初版误用 evidence.json 导致缓存失效，已修正）
- `scan_audio` 不写 evidence.json；缓存判定以 metrics.json 为准
- 比较预算：小批全对 / 中批每候选 4 对 / 大批每候选 3 对（补丁包 estimate_pair_budget.py 口径）
- ffmpeg 经 winget 路径可用；无 ffmpeg 时端到端测试跳过（skipif 约定与 pairwise 一致）
