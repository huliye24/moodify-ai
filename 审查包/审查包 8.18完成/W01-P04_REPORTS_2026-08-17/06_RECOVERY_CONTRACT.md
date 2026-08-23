# 06 — Recovery Contract

**W01-P04 · 2026-08-17 · 实现：recover_expired_leases() + 持久化**

## Case A — Worker crash

- lease 最终过期（TTL 3600s，无 heartbeat 则过期）。
- Job 不会永远 RUNNING：`recover_expired_leases()` 将过期 RUNNING/VERIFYING → RETRY_WAIT（预算内）或 FAILED。
- 不完整 attempt 保留（attempts 表 outcome='failed'）。
- 新 attempt 可启动（requeue → claim 新 attempt_number）。
- **验证：TST-02**

## Case B — Control node restart

- 状态全部持久化于 SQLite；无 in-memory-only authority（CP-INV-18）。
- 重开连接即恢复（TST-06）。
- **验证：TST-06**

## Case C — Network partition

- stale worker 的 lease 过期 → `_guard_lease` 拒绝 commit（fencing，CP-INV-17）。
- **验证：TST-02（stale complete 拒绝）**

## Case D — DB temporary unavailable

- worker 侧：DB 错误应归类 DB_TRANSIENT → RETRY_WAIT；不得静默假设成功（CP-INV-12）。
- 控制面：BEGIN IMMEDIATE 失败即 rollback，无半写。

## Case E — OSS upload succeeds but DB commit fails

- object 未注册 → complete 拒绝（CP-INV-13）→ 无 false READY。
- orphan 对象可由 P03 `orphan_objects()` 检测（INV-08）。
- **验证：TST-07**

## Case F — DB says object exists but OSS missing

- P03 `missing_objects()` 检测（INV-09）；不进入 READY 交付（READY 要求 registered artifact；delivery 侧校验 OSS 存在性为 P05/P06 责任）。

## 恢复流程（worker 侧启动时）

1. 打开 DB → JobControlPlane(repo)。
2. 调用 `recover_expired_leases()`（对齐 node/reconstruction_job 的 recover_interrupted 语义）。
3. 领取 QUEUED/RETRY_WAIT 到期任务（P05 worker 循环）。

## 人工动作要求

- 所有恢复路径最终由 recover 自动完成；FAILED 需人工评估后 reset（TR-16，admin 权限）。
