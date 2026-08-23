# 14 — P05 Handoff

**From:** W01-P04（Control Plane & Job State Authority）→ **To:** W01-P05（Cloud Audio Compute Pipeline）

## 已固定（P05 不再设计状态机）

- 8 态生命周期（CREATED/QUEUED/RUNNING/VERIFYING/RETRY_WAIT/READY/FAILED/CANCELED）+ 16 条迁移矩阵
- Lease 契约（TTL 1h、heartbeat、fencing=attempt_number）
- Retry taxonomy（14 class）与预算
- Idempotency（create/transition/complete）
- Event/Attempt 模型（append-only）
- Control 命令面（Python API）
- 代码：`moodify.data_plane.control.JobControlPlane` + 12 测试

## P05 必须回答的唯一问题

> 一个被控制平面合法 claim 的 RUNNING Job，怎样执行完整音频计算 pipeline，并以可验证方式产出 READY candidate？

## P05 从 P04 接收（§20）

| 项 | 来源 |
|---|---|
| job_id / track_id / attempt_id | claim() 返回 |
| lease/fencing token | lease_id + attempt_number（heartbeat 需 owner 匹配） |
| stage reporting contract | progress 命令（stage 描述性，非 state） |
| input object refs | objects 表（source/stems 按 track/job） |
| pipeline version | enqueue(pipeline_version) |
| output registration contract | P03 register_object |
| failure taxonomy | FailureRecord + FAILURE_CLASSES |
| completion/failure command | complete() / fail() |
| Evidence contract | P03 evidence 表 + claim 必填 |

## P05 必答清单

| # | 问题 | 约束 |
|---|---|---|
| 1 | worker 循环（claim→执行→complete/fail）与 heartbeat 频率 | 复用 JobControlPlane；不新造状态机 |
| 2 | stage vocabulary（intake/stem/analyze/judge/intervene/render/verify/publish） | stage 仅描述（CP-INV-16） |
| 3 | 音频计算链与 audiolla/LALAL 集成 | P02 拓扑（audiolla 在 LA） |
| 4 | 产物注册与 READY guard 联动 | complete 前 register_object + verification evidence |
| 5 | worker 侧资源守卫与失败分类 | WORKER_RESOURCE_EXHAUSTED 等 |
| 6 | 现有 node/ worker 与新 control plane 的切换 | 人类授权 + 迁移（12 报告） |

## 阻塞项

- CONTROL_PLANE_DEPLOY_BLOCKED：生产 worker 切换需人类授权。
- PolarDB write gate 未解除（P04 全部为 SQLite 实现，生产迁移待授权）。
