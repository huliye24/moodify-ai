# NTRACK_RANKING_DATA_REPORT — 黄金案例与排名数据

任务：DSK-MFY-NTRACK-RANKER-001
日期：2026-08-09
运行：`python -m moodify.evaluation.ntrack.golden`（RNG seed 7，确定性合成）
输出：`moodify-core-package/outputs/ntrack_golden/golden_summary.json`

## 7 黄金案例结果（7/7 通过）

| 案例 | 断言要点 | 结果 |
|---|---|---|
| ALBUM_10_CLEAR_TOP3 | 10 轨全部 eligible；Top3 成员标记生效 | ✅ |
| ALBUM_12_TIED_MIDDLE | 中间近同轨形成 tie bands（多组 2-4 轨并带） | ✅ |
| ALBUM_REDUNDANT_TOP_TRACKS | 双子 hash 不同（不触发重复门）；专辑序 ≠ 单曲序；质量地板保留最强轨第一；冗余解释存在 | ✅ |
| PARTIAL_ANALYSIS_FAILURE | 1 轨 corrupt 隔离（failed=1）；其余 4 轨正常排名 | ✅ |
| N_EQUALS_2 | 2 轨委托 pairwise（1 条边）；无重复逻辑 | ✅ |
| HUMAN_REORDER | 人工反转序 → 派生 10 条 preference（HUMAN_EDITED） | ✅ |
| TOP5_BOUNDARY_UNCERTAIN | 第 5/6 名边界候选置信度 LOW；tie bands 存在 | ✅ |

## 学习数据卫生

- 机器排名本身不产生 preference（edges 只作为排名证据，不入 learning store）
- 人工调整才派生 preference：仅相邻反转/淘汰形成的逻辑支持对（HUMAN_EDITED，eligible_for_training=True）
- HUMAN_REORDER 案例验证派生计数 10（5 轨全反转 → 相邻反转对）

## 版本追踪（AT-14）

- ranking_model_version = `ntrack_elo_v1`（estimator）
- ranking_policy_version = `ntrack_policy_v1`（policy.json）
- pairwise_policy_version = `pairwise_policy_v1`（policy.json）
- analysis 版本：scan_manifest.json 的 profile_hash 按候选落盘
