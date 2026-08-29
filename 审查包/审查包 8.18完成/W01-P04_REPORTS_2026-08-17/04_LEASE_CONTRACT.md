# 04 — Lease Contract

**W01-P04 · 2026-08-17 · 实现：control.py（leases 表）**

## Lease 记录字段

| 字段 | 类型 | 说明 |
|---|---|---|
| lease_id | TEXT PK | 全局唯一 |
| job_id | TEXT UNIQUE | 一 job 一 lease（UNIQUE(job_id)） |
| attempt_id | TEXT | 绑定 attempt |
| owner | TEXT | worker_id |
| acquired_at | TEXT | 领取时间 |
| expires_at | TEXT | TTL 到期（DEFAULT_LEASE_SECONDS=3600s） |
| heartbeat_at | TEXT | 最近心跳 |
| release_reason | TEXT | completed/failed/canceled/expired |

## Lease 原则（§7.1）

1. **TTL 必须有**：DEFAULT_LEASE_SECONDS = 3600（1h）；心跳续租。
2. **heartbeat 只延长当前有效 lease**：`heartbeat()` 校验 lease 存在且未过期、owner 匹配。
3. **过期 lease 不可 commit result**：`_guard_lease` 拒绝过期 lease（fencing）。
4. **旧 worker 恢复后不得覆盖新 worker 结果**：过期 lease → claim 拒绝；complete 要求有效 lease（TST-02）。
5. **lease expiry 后 recovery runner 可重新 queue**：`recover_expired_leases()` → RETRY_WAIT → requeue → QUEUED。
6. **完成/失败时释放 lease**：complete/fail/cancel/recover 后 DELETE lease 行（审计留在 attempts/events）。

## Fencing（§7.2）

- 方案：**attempt_number 递增 + lease 有效性检查**（乐观版本）。
- 实现：claim 产生新 attempt_number（MAX+1）；stale worker 的 lease_id 已被删除/过期 → `_guard_lease` 抛 TransitionRejected。
- 无需单独 lease_version 字段（lease 行删除即失效 + UNIQUE(job_id) 保证一 job 一 lease）。

## 释放语义

| 事件 | 动作 |
|---|---|
| complete | lease DELETE（release_reason=completed 记录后删） |
| fail | lease DELETE（release_reason=failed 记录后删） |
| cancel | lease DELETE（按 job_id） |
| recover_expired | lease DELETE（release_reason=expired 记录后删） |
