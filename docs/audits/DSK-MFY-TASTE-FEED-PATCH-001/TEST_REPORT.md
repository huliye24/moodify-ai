# TEST_REPORT — 测试结果

任务：DSK-MFY-TASTE-FEED-PATCH-001
日期：2026-08-09

## 1. 命令与结果

| 命令 | 结果 |
|---|---|
| `pytest tests/recommendation/test_feedback_taste.py` | ✅ 10 passed |
| `pytest tests/recommendation/test_rank.py` | ✅ 7 passed |
| `pytest tests/recommendation/test_service_api.py` | ✅ 9 passed |
| `python -m moodify.recommendation.golden` | ✅ 7/7（见下） |
| `ruff check`（recommendation + 测试 + 触及文件） | ✅ All checks passed |
| CLI 冒烟（request/feedback/taste） | ✅ 三条命令 JSON 输出正常 |

新增测试合计 **23 个**（+ 黄金 7 场景脚本）。

## 2. 黄金场景（7/7）

| 场景 | 断言 | 结果 |
|---|---|---|
| NEW_USER_COLD_START | 新用户无偏好仍服务 5 条 | ✅ |
| TRACK_PROFILE_LINKAGE | 轨道 → 7 维听觉 profile 可链接 | ✅ |
| FEEDBACK_UPDATES_TASTE | COMPLETION 事件 → 口味向量变化 | ✅ |
| SKIP_PENALTY_RANKING | 重复硬跳轨道掉出榜首 | ✅ |
| EXPLORATION_BUDGET | 探索池在预算内 + similarity/exploration 来源并存 | ✅ |
| QUALITY_GATE_FILTER | SEVERE_ISSUES 轨道不进 feed | ✅ |
| REQUEST_TRACEABILITY | request_id + ranking_version + 事件可回链（3 impression + 1 反馈） | ✅ |

## 3. 验收标准对照（09_ACCEPTANCE_TESTS.md）

| AT | 覆盖 |
|---|---|
| AT-01 导航双面 | ⚠️ core 支持；Android feed 入口 DEFER（PARTIAL 项） |
| AT-02 For You 面 | ✅ API/CLI 可进入并播放（轨道注册 + feed） |
| AT-03 反馈捕获 | ✅ 9 事件类型 + 派生标签（impression/play/skip/completion/replay/like/save） |
| AT-04 轨道 profile 链接 | ✅ auditory_profile 端点 + 黄金场景 |
| AT-05 口味 profile | ✅ 事件 → 长短期向量 + novelty tolerance |
| AT-06 排名可追溯 | ✅ request_id/ranking_version/事件回链（黄金场景） |
| AT-07 核心保留 | ✅ 听觉管线未动（全量回归） |
| AT-08 无遗留回潮 | ✅ 无 CWC/token 引入（审计 + 文案） |
| AT-09 轻量纪律 | ✅ 仅 feed/收藏，无社交膨胀 |
| AT-10 解释 token | ✅ 每候选 explanation_tokens（source/pref_match/novelty/diversity/quality） |

## 4. 全量回归

- `pytest -q`（moodify-core-package，本实现后复跑）：见验收记录（基线 932 + 新增 23）
