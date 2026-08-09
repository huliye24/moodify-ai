# ACCESS_CWC_TEST_REPORT — 测试结果

任务：DSK-MFY-ACCESS-CWC-PATCH-001
日期：2026-08-09

## 1. 命令与结果

| 命令 | 结果 |
|---|---|
| `pytest tests/access/test_ledger.py` | ✅ 9 passed |
| `pytest tests/access/test_admission.py` | ✅ 10 passed |
| `pytest tests/access/test_service.py` | ✅ 9 passed |
| `pytest tests/access/test_api.py` | ✅ 8 passed |
| `python -m moodify.access.golden` | ✅ 7/7（见下） |
| `ruff check`（access + 测试 + 触及文件） | ✅ All checks passed |
| CLI 冒烟（register/estimate/admit） | ✅ 三条命令 JSON 输出正常 |

新增测试合计 **34 个**。

## 2. 黄金场景（7/7）

| 场景 | 断言 | 结果 |
|---|---|---|
| OPEN_SIGNUP_NO_CODE | 无邀请码注册成功，starter 100 CWC | ✅ |
| OPEN_SIGNUP_WITH_REFERRAL | 推荐码可选注册，双方 GRANTED | ✅ |
| AB_JUDGE_ESTIMATED_COST | estimate(pairwise_ab_judge) = 5 | ✅ |
| INSUFFICIENT_CWC | 余额耗尽后 REJECTED_INSUFFICIENT（可控拒绝非崩溃） | ✅ |
| QUEUE_UNDER_LOAD | 并发满 → QUEUED + backpressure 文案 | ✅ |
| REFERRAL_REWARD_GRANTED | 邀请者 +10、被邀请者 +5 | ✅ |
| LEGACY_CWC_COPY_REMOVED | access 包零 平台币/钱包/交易中心 命中 | ✅ |

## 3. 验收标准对照（09_ACCEPTANCE_TESTS.md）

| AT | 覆盖 |
|---|---|
| AT-01 开放注册 | ✅ 无码注册测试 + API |
| AT-02 可选推荐码 | ✅ 带码注册 + 无码不阻断 |
| AT-03 CWC 语义 | ✅ 全库文案扫描 + 黄金 LEGACY 场景 |
| AT-04 无硬门 | ✅ invite_required=False 默认 + API 422 拒绝旧硬字段 |
| AT-05 成本估算 | ✅ estimate 端点（AB Judge 5 CWC） |
| AT-06 余额检查 | ✅ admit 前可用余额校验 |
| AT-07 队列 | ✅ QUEUED 状态 + backpressure |
| AT-08 并发限制 | ✅ free 并发 1，超额 QUEUED |
| AT-09 推荐奖励 | ✅ 双方得 CWC + 一次性/上限/自荐拒绝 |
| AT-10 文案清理 | ✅ 无平台币/钱包文案 |
| AT-11 背压 | ✅ 队列满 → QUEUE_FULL 可控拒绝 |
| AT-12 特性开关 | ✅ open_registration 可关（策略字段） |

## 4. 全量回归

- `pytest -q`（moodify-core-package，本实现后复跑）：见验收记录（基线 898 + 新增 34）
