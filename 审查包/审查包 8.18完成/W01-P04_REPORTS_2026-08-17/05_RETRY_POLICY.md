# 05 — Retry Policy

**W01-P04 · 2026-08-17 · 实现：control.py FAILURE_CLASSES**

## Failure Class → Retry 策略

| failure_class | retryable | max_attempts | 说明 |
|---|---|---|---|
| INPUT_INVALID | 否 | 1 | 输入不可修复（TST-05） |
| STORAGE_TRANSIENT | 是 | 3 | OSS 瞬时错误 |
| STORAGE_PERMANENT | 否 | 1 | 对象不可恢复 |
| DB_TRANSIENT | 是 | 3 | 数据库瞬时错误 |
| EXTERNAL_API_RATE_LIMIT | 是 | 3 | 限流退避 |
| EXTERNAL_API_TRANSIENT | 是 | 3 | 外部 API 超时等（TST-04） |
| EXTERNAL_API_PERMANENT | 否 | 1 | 外部拒绝/无效 |
| WORKER_RESOURCE_EXHAUSTED | 是 | 2 | 内存/磁盘不足 |
| PROCESS_TIMEOUT | 是 | 2 | 超时 |
| PROCESS_CRASH | 是 | 3 | worker 崩溃（recover 默认） |
| VERIFICATION_FAILED | 否 | 1 | 验证不通过不重跑 |
| INTERNAL_BUG | 否 | 1 | 需要修复 |
| CANCELED_BY_USER | 否 | 1 | 用户取消 |
| UNKNOWN_FAILURE | 是 | 2 | 兜底 |

## Backoff

- DEFAULT_BACKOFF_SECONDS = 5（当前阶段固定值；指数退避留 P05 worker 侧）。
- jitter：未启用（单 worker 无争用需求）。

## 语义

- 每次 fail：`attempts < max_attempts` 且 retryable → RETRY_WAIT；否则 FAILED（终态）。
- permanent failure 不盲目重试（TST-05）。
- retry 需要新 attempt：requeue 后 claim 产生新 attempt_number（TST-02）。
- 重试前清理：worker 侧负责（P05）；控制面只移动状态。

## 与现有系统对照

- node/（旧）：retry_or_fail 限 3 次 → 对齐 STORAGE_TRANSIENT/DB_TRANSIENT/PROCESS_CRASH 类。
- reconstruction_job/：RETRY_POLICIES（TRANSIENT/PERMANENT/HUMAN_REQUIRED/EXTERNAL_BILLABLE）→ 映射到本 taxonomy。
