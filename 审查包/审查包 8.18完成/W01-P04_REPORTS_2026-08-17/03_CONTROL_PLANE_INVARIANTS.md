# 03 — Control Plane Invariants

**W01-P04 · 2026-08-17 · 实现状态：代码（moodify.data_plane.control）已实现并有测试**

| # | Invariant | 实现 | 验证 |
|---|---|---|---|
| CP-INV-01 | One State Authority：一个 Job 一个权威 current state | `jobs.current_state` 唯一；仅 JobControlPlane 可迁移 | TST-09/12 |
| CP-INV-02 | Transactional Transition：迁移+attempt/lease/event 同一事务 | 全部迁移在 BEGIN IMMEDIATE 内 | TST-01 |
| CP-INV-03 | No Silent Transition：每次迁移 append event | `_append_event` 强制 | TST-12 |
| CP-INV-04 | Event Is Audit：event 不替代 current state | `jobs.current_state` 仍是权威 | TST-12 |
| CP-INV-05 | One Valid Lease：同时最多一个有效 lease | claim 原子检查 + leases UNIQUE(job_id) | TST-01 |
| CP-INV-06 | Expiring Ownership：lease 有 TTL | DEFAULT_LEASE_SECONDS=3600；heartbeat 续租 | TST-02 |
| CP-INV-07 | Heartbeat Not Business Progress | heartbeat 只延 expires_at，不改 state | TST-12（state 不变） |
| CP-INV-08 | Terminal Protection：终态不可被普通 worker 回退 | claim/fail 拒绝终态；无 public revert | TST-09 |
| CP-INV-09 | Bounded Retry：retry 有预算 | FAILURE_CLASSES max_attempts | TST-04 |
| CP-INV-10 | Idempotent Commands | idempotency_keys 表 + 指纹校验 | TST-03/10/11 |
| CP-INV-11 | Deterministic Recovery：重启从 DB 恢复 | state 持久化；TST-06 重开连接验证 | TST-06 |
| CP-INV-12 | Structured Failure：class/code/retryable | FailureRecord + FAILURE_CLASSES | TST-05 |
| CP-INV-13 | READY Requires Artifact | complete 校验 ready_object_id 已注册 | TST-08 |
| CP-INV-14 | READY Requires Required Verification | complete 校验 verification_evidence 标志（Canon 要求时） | TST-08 |
| CP-INV-15 | Worker Uses Commands | 仅 JobControlPlane 提供迁移方法；无裸 SQL 写 | 设计 |
| CP-INV-16 | Stage Is Descriptive | jobs 无 stage 状态字段（P05 定义 stage vocabulary） | 设计 |
| CP-INV-17 | Stale Attempt Cannot Commit | _guard_lease：lease 过期/不属调用者 → 拒绝 | TST-02 |
| CP-INV-18 | No In-memory-only Queue Truth | SQLite 持久化；恢复从 DB 事实 | TST-06 |
