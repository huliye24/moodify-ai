# 10 — Observability Contract

**W01-P04 · 2026-08-17 · 最小观测面（§14，不建大型监控平台）**

## Job 视图（job_view(job_id)）

current_state / current_attempt / lease（owner/expiry）/ retry 计数（attempts）/ last failure（failure_code）/ ready_object_id / events（时间线）

## Queue 视图（queue_summary()）

| 指标 | 来源 |
|---|---|
| queued / retry_wait / running / verifying / ready / failed / canceled | jobs.current_state 计数 |
| stale_leases | leases.expires_at <= now |

## Worker 视图

- worker_id / last heartbeat / current job / version / capacity / health：**P05 worker 侧实现**（本包提供 lease/attempt 数据源）。

## Control 视图

- DB reachable：repo 查询成功即活。
- object store reachable：P03 adapter head（轻量）。
- queue authority healthy：queue_summary() 可调用。
- build/commit/version：仓库 git commit（部署时记录）。

## 日志要求（§15）

所有日志至少携带：track_id / job_id / attempt_id / correlation_id / stage / worker_id。

禁止：
- log 中输出 Secret；
- log 中输出签名 URL 完整 query；
- 只留无结构 traceback 而没有 failure record（须走 FailureRecord）。

## 实现现状

- `queue_summary()` / `job_view()` / `events()` 已实现（control.py）。
- worker 级观测与日志接入 → P05。
