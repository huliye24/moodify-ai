# 00 — P04 Executive Summary

**Package:** W01-P04 — Control Plane & Authoritative Job State Machine
**执行时间:** 2026-08-17 22:30–23:10 CST
**性质:** 控制平面建设（代码 + 契约 + 测试）；生产部署 BLOCKED

## 三个原子任务

- **T04-1 唯一 Job State Machine**：Existing Authority Discovery（7 个候选系统）→ 收敛 8 态生命周期（State≠Stage），16 条迁移矩阵（脚本校验通过）。
- **T04-2 Queue/Lease/Retry/Recovery/Idempotency**：`JobControlPlane` 实现原子 claim（单 owner）、lease TTL+heartbeat+fencing、retry 预算、恢复、幂等注册。
- **T04-3 Failure/Event/Evidence/Observability**：14 类 failure taxonomy、append-only 事件、attempt 模型、queue_summary/job_view。

## 关键决策

1. **不新造第二套状态机**：以 P03 已提交的 data_plane repository 为基准实现；node/（4 态，生产实跑）与 reconstruction_job/（11 态，未提交）映射到 8 态，运行时切换待授权。
2. **State≠Stage**：stage 是进度描述（P05 定义 vocabulary）；reconstruction_job 的 VALIDATING/ANALYZING 等 stage 不再升级为状态。
3. **Lease 释放即删除**：leases 表 1:1 每 job，claim 原子领取；stale worker 因 lease 失效无法 commit（fencing）。
4. **READY 双 guard**：ready_object_id 必须注册（CP-INV-13）+ verification 标志（CP-INV-14）。

## 验证

- 12/12 测试（TST-01..12）PASS；连同 P03/guard 共 **24 passed**；ruff 干净。
- 迁移矩阵脚本校验：16 transitions OK。

## Gate

- CONTROL_PLANE_DEPLOY_BLOCKED：生产部署未授权（代码/migration/测试/计划已完成）。

**完成后停止，等待人类审核，不进入 P05。**
