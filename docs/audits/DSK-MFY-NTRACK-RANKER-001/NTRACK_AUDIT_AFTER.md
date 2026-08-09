# NTRACK_AUDIT_AFTER — 实施后状态

任务：DSK-MFY-NTRACK-RANKER-001
日期：2026-08-09

## 新增能力

- `moodify/evaluation/ntrack/`：7 模块（models/policy/estimator/album/service/golden/__init__）
- `configs/ntrack_policy_v1.yaml`：唯一排名策略来源
- CLI：`case ntrack-rank` / `case ntrack-human-ranking`
- API：`POST /api/v1/rankings` / `POST /api/v1/rankings/{id}/human-ranking` / `GET /api/v1/rankings/{id}`
- 测试 34 个（9 模型策略 + 10 估计器 + 5 专辑 + 4 API/CLI + 7 端到端，另有服务测试覆盖缓存/隔离/派生）——测试计数以 TEST_REPORT 为准（逻辑 24 + 端到端 7 = 31；golden 脚本 7 案例）
- 黄金案例 7/7 + `outputs/ntrack_golden/golden_summary.json`

## 未改变

- Pairwise Judge 引擎原样保留（复用而非改动）：26 测试继续绿
- v0.1 管线、Android、runtime、cloud 无改动
- 无新增第三方依赖（numpy/scipy/yaml 均为既有）

## 残余与 DEFER

| 项 | 状态 |
|---|---|
| API 异步 job（大批 N） | 未实现（小批同步可跑；策略预算约束） |
| Android UI（Phase 7） | DEFER |
| 跨 case 全局分析缓存 | 未做（case 内按 hash 缓存已实现） |
| AlbumSequencePlanner（曲序优化） | 按规格保留扩展点，未实现 |
| REVIEW_REQUIRED 触发 | 已实现（削波/静音阈值），人工复核流未接 UI |

## 事实边界

- 实现期修正了两个会误导后续开发的事实：
  1. `load_scan_evidence` 依赖 `metrics.json` + `analysis_data.npz`（非 evidence.json）——初版缓存判定误用 evidence.json 导致缓存永不命中，已修
  2. scan metrics 值为嵌套 dict（`{'value': ...}`）——特征提取初版未解包导致全部特征为 0（专辑冗余全惩罚），已修并与 pairwise `_value` 约定一致
- 合成纯音 tone 的特征区分度有限（band 集中单频带）；专辑冗余测试已用不同频段/噪声组合验证
