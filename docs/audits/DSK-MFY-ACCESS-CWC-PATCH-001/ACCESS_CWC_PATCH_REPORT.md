# ACCESS_CWC_PATCH_REPORT — 开放访问 + CWC 计算额度实现清单

任务：DSK-MFY-ACCESS-CWC-PATCH-001
日期：2026-08-09

## 1. 新增包 `moodify/access/`

| 文件 | 职责 |
|---|---|
| `models.py` | 6 个 frozen dataclass：UserAccessProfile / CWCBalance / CWCTransaction / ComputeJobAdmission / QuotaState / ReferralRewardRecord |
| `policy.py` | AccessPolicy（from_yaml 权威路径 `configs/access_policy_v1.yaml`）：开放注册、操作成本表、tier 并发/每日配额/限流、推荐奖励、队列深度 |
| `ledger.py` | CWC 账本：append-only JSONL 事务日志 + 重放推导余额；GRANT/RESERVE/CONSUME/RELEASE/REFUND/REFERRAL_REWARD/ADMIN_ADJUST；不变量 available ≥ 0 |
| `admission.py` | 计算准入：estimate → 余额检查 → reserve → 并发限制 → QUEUED 排队（含 backpressure 消息）→ settle（消费 + 差额退回）/ fail（释放）；rate limit + 每日配额 + 队列深度 |
| `service.py` | 开放注册（邀请码必填移除）+ 推荐奖励（双方、一次性、邀请者上限、自荐拒绝）+ 统一门面 |
| `golden.py` | 7 个黄金场景（确定性） |
| `__init__.py` | 公共导出 |

## 2. 配置

- `configs/access_policy_v1.yaml`：唯一阈值来源（starter 100 CWC、操作成本 quick_scan 1 / full_analysis 3 / AB Judge 5 / ranking_10 20、free 并发 1、限流 3/min、推荐 10+5）

## 3. API（routes/access.py，已注册 /api/v1）

- `POST /api/v1/auth/register`（referral_code 可选；extra=forbid 拒绝旧邀请码硬字段）
- `POST /api/v1/referral/redeem`
- `GET /api/v1/cwc/balance`、`GET /api/v1/cwc/history`
- `POST /api/v1/compute/estimate`、`POST /api/v1/compute/admit`、`POST /api/v1/compute/settle`
- `GET /api/v1/compute/quota`

## 4. CLI（cli_v2/main.py）

- `access register <user> [--referral-code]`、`access balance <user>`、`access estimate <op>`、`access admit <user> <op>`、`access referral <inviter> <invitee>`（--store 可指定账本根）

## 5. 战略一致性

- CWC = 计算额度：全库扫描无 平台币/钱包资产/交易中心/购买藏品 文案（黄金场景 LEGACY_CWC_COPY_REMOVED 自动断言）
- 入口开放 vs 计算受限分离：注册永不要求邀请码；重计算走配额/队列
- 未 reintroduce：交易中心 / 钱包投机 / 藏品 / 平台币叙事

## 6. 已知限制 / DEFER

- A/B Judge 与 N 轨排名引擎**未接入** admit（提供 estimate/admit 端点与成本表，引擎准入集成后续任务）
- Android 端新文案（07_UI_COPY_PATCH：推荐码可选等）因补丁 08 已清空 CWC 区域，无活跃代码可改；注册 UI 未来在 Android 侧做
- 限流为分钟窗口（非滑动窗口）；账本为单机文件存储（非多进程安全事务）
