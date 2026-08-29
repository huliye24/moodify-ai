# 07 — Idempotency Contract

**W01-P04 · 2026-08-17 · 实现：idempotency_keys 表 + 指纹校验**

## 四类幂等（§10）

| 类型 | 语义 | 实现 | 验证 |
|---|---|---|---|
| Create Job | 同请求重复提交 → 同一逻辑 job | enqueue(idempotency_key, request_fingerprint) → 已存在同 key 同指纹 → 返回原 job | TST-10 |
| Transition | 同 command 重复发送 → 幂等/拒绝 | 状态前置校验：已迁移则拒绝或 no-op | TST-03（complete） |
| Artifact Registration | P03 已定义 | register_object 按 object_id 幂等 | P03 Test E |
| Completion | worker 网络超时重复 complete | 已 READY 后 lease 已删 → 二次 complete 拒绝（无重复事件） | TST-03 |

## Idempotency Key 记录

| 字段 | 说明 |
|---|---|
| idempotency_key | 主键（调用方提供） |
| scope | "create_job" 等 |
| request_fingerprint | 请求指纹（内容 hash） |
| result_ref | 结果 job_id |
| created_at | 创建时间 |

## 规则

1. **同 key + 同指纹** → 返回已有结果（幂等）。
2. **同 key + 不同指纹** → `IdempotencyConflict`（不可静默复用；TST-11）。
3. 指纹冲突是硬错误，不猜测调用方意图。

## 边界

- 当前阶段 idempotency_key 由控制面调用方生成（API 层 P06）；本模块提供 registry。
- 过期/保留策略：当前保留全部（阶段小）；P06 API 化时加 retention。
