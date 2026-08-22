# 02 — Authoritative State Machine

**W01-P04 · 2026-08-17 · 唯一 Job 生命周期权威（8 态）**

## 设计原则

1. **State ≠ Stage**（CP-INV-16）：State 是控制生命周期权威；Stage 是进度描述（P05 定义 vocabulary）。
2. **Lease ≠ State**：lease 是 ownership metadata。
3. **Event ≠ State Authority**（CP-INV-04）：event 是审计日志。
4. **Attempt ≠ State**：attempt 是执行实例。
5. 优先复用 P03 data_plane jobs 表（字段承载）——本包补齐迁移语义。

## 状态集（8 态）

```text
CREATED
  → QUEUED
      → RUNNING
          → VERIFYING
              → READY
          → RETRY_WAIT (transient failure, budget remains)
              → QUEUED
      → CANCELED
RUNNING / VERIFYING → FAILED (terminal, after budget or permanent)
CREATED / QUEUED / RETRY_WAIT → CANCELED
```

| State | 含义 | Terminal |
|---|---|---|
| CREATED | Job 记录建立，尚未入队 | — |
| QUEUED | 可被 worker 领取 | — |
| RUNNING | 有有效 lease 的 worker 正在执行 | — |
| VERIFYING | 产物验证阶段（Canon 要求时） | — |
| RETRY_WAIT | transient 失败等待退避重试 | — |
| READY | 完成；必须有 ready_object_id（CP-INV-13）+ 要求的 verification evidence（CP-INV-14） | ✓ |
| FAILED | 终态（预算耗尽或永久失败） | ✓ |
| CANCELED | 终态（用户/管理取消） | ✓ |

## 与现有系统映射

| P04 8 态 | node/（4 态） | reconstruction_job/（11 态） | contracts/production_case |
|---|---|---|---|
| CREATED | — | — | CREATED |
| QUEUED | QUEUED | QUEUED | ACTIVE |
| RUNNING | RUNNING | VALIDATING/ANALYZING/PLANNING/RECONSTRUCTING（stage 投影） | ACTIVE |
| VERIFYING | — | VERIFYING | ACTIVE |
| RETRY_WAIT | — | —（retry_or_fail 内退避） | — |
| READY | SUCCEEDED | SUCCEEDED / SOURCE_WINS | COMPLETED |
| FAILED | FAILED | FAILED | FAILED |
| CANCELED | — | CANCELLED | CANCELLED |
| — | — | HUMAN_REQUIRED | AWAITING_HUMAN |

HUMAN_REQUIRED/AWAITING_HUMAN：评审域状态（authority/escalation），非 lifecycle——READY 前可悬挂于 VERIFYING 或显式 HUMAN 门（P05 细化）。

## 迁移矩阵（完整定义见 02_STATE_TRANSITION_MATRIX.csv）

| from | command | to | actor | 关键前置 |
|---|---|---|---|---|
| CREATED | enqueue | QUEUED | control | track 存在 |
| QUEUED | claim | RUNNING | worker | 无有效 lease；原子领取（CP-INV-05/06） |
| RUNNING | heartbeat | RUNNING | lease owner | lease 有效；仅续租（CP-INV-07） |
| RUNNING | progress | RUNNING | lease owner | 更新 stage（非 state） |
| RUNNING | verify | VERIFYING | lease owner | 产物已注册 |
| VERIFYING | complete | READY | control/owner | ready_object_id 存在 + verification（CP-INV-13/14） |
| RUNNING | fail | RETRY_WAIT | control | retryable 且预算未耗尽（CP-INV-09） |
| RUNNING | fail | FAILED | control | permanent 或预算耗尽 |
| VERIFYING | fail | FAILED | control | 同上 |
| RETRY_WAIT | requeue | QUEUED | control/recovery | backoff 到期 |
| QUEUED/RUNNING/... | cancel | CANCELED | control/user | 非终态 |
| 任意终态 | （回退） | — | 禁止 | CP-INV-08：仅显式 reset 策略 |

## 事务性（CP-INV-02）

每次迁移在一个一致性边界内完成：
1. 校验当前 state（WHERE state = expected）
2. 校验前置（lease/attempt/artifact/verification）
3. 写 jobs 新 state + attempt/lease 变更 + append event
4. 全部在同一事务（SQLite BEGIN IMMEDIATE）

## 并发语义（CP-INV-05/17）

- claim：`UPDATE jobs SET ... WHERE job_id=? AND current_state='QUEUED' AND NOT EXISTS 有效 lease`（原子）。
- 并发双 claim：只有一个成功（TST-01）。
- stale worker commit：lease 过期或 attempt_number 不符 → 拒绝（fencing，TST-02/CP-INV-17）。

## 实现

- `moodify.data_plane.control`：JobStateMachine（迁移表 + 事务执行）+ LeaseManager + RetryPolicy + EventLog + AttemptStore + IdempotencyRegistry + QueueSummary。
- jobs 表扩展字段已具备（P03）：current_state/current_attempt/failure_code/failure_summary/started_at/finished_at/ready_object_id。
- 新增表：job_events / attempts / leases / idempotency_keys（见 control.py SCHEMA 扩展）。
