# 09 — Event & Attempt Model

**W01-P04 · 2026-08-17 · 实现：job_events + attempts 表（control.py）**

## Event Log（append-only，审计非权威，CP-INV-03/04）

| 字段 | 说明 |
|---|---|
| event_id | 全局唯一 |
| job_id / track_id / attempt_id | 追溯键 |
| event_type | JOB_ENQUEUED / JOB_CLAIMED / LEASE_HEARTBEAT / STAGE_CHANGED / JOB_VERIFYING / JOB_READY / JOB_FAILED_TRANSIENT / JOB_FAILED / JOB_REQUEUED / JOB_CANCELED / JOB_RESET |
| actor_type / actor_id | control / worker / user / admin |
| from_state / to_state | 迁移记录 |
| stage | 进度描述（可选） |
| occurred_at | 时间戳 |
| correlation_id | 关联 ID（重试链） |
| failure_code | 失败码（如适用） |

- 规则：**只 append，不 update/delete**；`jobs.current_state` 仍是当前状态权威。
- 查询：按 job_id / attempt_id / correlation_id（P04 §14 logs 可查询性）。

## Attempt 模型（§13）

```text
job
  ├── attempt 1 (attempt_id, number=1, worker, lease, started, outcome)
  ├── attempt 2 (number=2, ...)
  └── attempt 3 (number=3, ...)
```

| 字段 | 说明 |
|---|---|
| attempt_id / job_id / attempt_number | UNIQUE(job_id, attempt_number) |
| worker_id / lease_id | 执行身份 |
| started_at / ended_at | 时间 |
| outcome | started / succeeded / failed |
| failure_code | 失败码 |
| output_object_id | 产出对象 |

- 每个 attempt 独立记录 → retry 不覆盖历史失败（§13）。
- attempt_number 是 fencing 的一部分（stale attempt 不能 commit，CP-INV-17）。

## 事件完整性与查询

- 每次迁移必 append（TST-12 验证全事件类型出现）。
- queue/job observability：`queue_summary()` / `job_view()` / `events()`。
