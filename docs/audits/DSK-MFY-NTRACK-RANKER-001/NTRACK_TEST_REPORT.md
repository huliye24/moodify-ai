# NTRACK_TEST_REPORT — 测试结果

任务：DSK-MFY-NTRACK-RANKER-001
日期：2026-08-09

## 1. 命令与结果

| 命令 | 结果 |
|---|---|
| `pytest tests/evaluation/test_ntrack_models_policy.py` | ✅ 9 passed |
| `pytest tests/evaluation/test_ntrack_estimator.py` | ✅ 10 passed |
| `pytest tests/evaluation/test_ntrack_album.py` | ✅ 4 passed |
| `pytest tests/evaluation/test_ntrack_api_cli.py` | ✅ 4 passed |
| `pytest tests/evaluation/test_ntrack_service.py`（端到端，真实扫描） | ✅ 7 passed（46.5s） |
| `python -m moodify.evaluation.ntrack.golden` | ✅ 7/7（见 RANKING_DATA_REPORT） |
| `ruff check`（ntrack + 测试 + 触及文件） | ✅ All checks passed |
| 全量回归 | 见下方第 3 节 |

新增测试合计 **34 个**。

## 2. 验收标准对照（11_ACCEPTANCE_TESTS.md）

| AT | 覆盖 |
|---|---|
| AT-01 批量导入 N≥3 | ✅ service 端到端 5 轨 |
| AT-02 分析一次 + 缓存 | ✅ monkeypatch 计数验证：首次 3 次扫描，二次 0 次 |
| AT-03 N=2 委托 | ✅ N_EQUALS_2 黄金案例 + service 测试 |
| AT-04 全局排名 | ✅ 链式边排序测试 + 端到端 |
| AT-05 不确定性/tie bands | ✅ 接近分数成带测试 + ALBUM_12_TIED_MIDDLE 黄金 |
| AT-06 选择性比较 | ✅ 中批预算测试（30 轨 → 120 对 < 435） |
| AT-07 Top-K | ✅ top_k_membership 断言 + API 测试 |
| AT-08 边界精修 | ✅ plan_pairs 边界覆盖测试 + TOP5_BOUNDARY_UNCERTAIN 黄金 |
| AT-09 部分失败隔离 | ✅ PARTIAL_ANALYSIS_FAILURE 黄金 + 端到端 corrupt 隔离 |
| AT-10 证据理由 | ✅ 每 ranked candidate reasons/evidence_refs |
| AT-11 专辑模式 | ✅ ALBUM_REDUNDANT_TOP_TRACKS 黄金 + 4 个 album 单测 |
| AT-12 人工重排持久化 | ✅ HUMAN_REORDER 黄金 + human_ranking.json 断言 |
| AT-13 学习卫生 | ✅ 派生仅相邻反转；label_source=HUMAN_EDITED |
| AT-14 可复现 | ✅ 版本字段（model/policy/analysis）持久化 + 确定性测试 |

## 3. 全量回归

- `pytest -q`（moodify-core-package，本实现后复跑）：**898 passed, 1 skipped**（基线 867 + 新增 31；无退化，8 分钟）
- `ruff check src/moodify tests`：无新增违规（基线 23 条既有 test 文件违规不归本补丁）
- `git diff --check`：通过
