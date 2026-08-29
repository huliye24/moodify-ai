# 11 — Control API Command Contract

**W01-P04 · 2026-08-17 · 内部命令面（§16）；P06 决定是否公网 REST 化**

## 命令清单（实现于 JobControlPlane）

| 命令 | 方法 | 状态迁移 | 幂等 | 内部 auth 要求 |
|---|---|---|---|---|
| create+enqueue job | enqueue() | CREATED→QUEUED | idempotency_key | 控制面 |
| claim job | claim() | QUEUED→RUNNING | 单 owner 原子 | worker 身份 |
| heartbeat lease | heartbeat() | RUNNING 保持 | 幂等 | lease owner |
| report progress/stage | （P05 扩展） | stage 描述 | 幂等 | lease owner |
| verify | verify() | RUNNING→VERIFYING | 幂等 | lease owner |
| complete job | complete() | →READY | 终态幂等 | lease owner + artifact |
| fail attempt | fail() | →RETRY_WAIT/FAILED | 幂等 | control |
| cancel job | cancel(admin=) | →CANCELED | 终态幂等 | user/admin（RUNNING 需 admin） |
| requeue | requeue() | RETRY_WAIT→QUEUED | 幂等 | control/recovery |
| get job | job_view() | — | — | 控制面 |
| list queue summary | queue_summary() | — | — | 控制面 |
| get worker health | （P05 worker 侧） | — | — | 内部 |

## 边界

- 当前为 Python API（模块级命令面），非 REST。
- 公网 REST 化与鉴权（service-key 复用 P02 S-02）→ P06。
- 内部 worker 命令使用内部 auth / private boundary（P02 NW 目标：杭州 :8000 收紧为 LA 白名单）。
