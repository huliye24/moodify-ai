# Codex Execution Prompt — W01-P04

你正在执行：

**Moodify Cognitive Wave 01 / W01-P04 — Control Plane & Authoritative Job State Machine**

## 第一步不是写代码

先完成：

`CURRENT_CONTROL_AUTHORITY_MAP.md`

扫描仓库当前所有：

- state machine
- workflow/orchestration
- queue
- worker claim
- lease
- retry
- recovery
- API job handlers

禁止在扫描前创建新状态机。

## 三个任务

### T04-1
收敛一个 authoritative job lifecycle。

原则：

- State != Stage
- Lease != State
- Event != State Authority

### T04-2
实现/收敛：

- atomic claim
- lease
- heartbeat
- expiry
- fencing
- retry budget
- recovery
- idempotency

### T04-3
建立：

- structured failure
- append-only events
- attempts
- logs
- queue/job/worker observability

## 关键安全条件

- 一个 Job 同时最多一个有效 owner
- stale worker 不能覆盖新 worker
- READY 前必须有 ready object
- terminal state 不能被普通 worker 回退
- restart 后依赖 DB 恢复，不依赖内存

## 禁止

- 第二套 state authority
- 第二套 queue authority
- 在 P04 实现音频 processing pipeline
- 在 P04 实现 playback
- 未授权 production deploy

完成 P05 Handoff 后停止。
