# W01-P04 — Control Plane & Authoritative Job State Machine

这是 Moodify Cognitive Wave 01 的第五个任务包。

## 3 个原子任务

1. **唯一 Authoritative Job State Machine**
2. **Queue / Lease / Retry / Recovery / Idempotency**
3. **Failure / Event / Evidence / Observability**

## 核心目标

以后任何时刻问：

> “这首歌现在在哪一步？”

系统都只能有一个权威答案。

## 最重要的设计

### State != Stage

Job State 负责控制生命周期。

Pipeline Stage 只描述当前做什么。

避免把 stem / analyze / render 等每一个处理步骤都变成一级状态，造成状态机膨胀。

### Lease != State

Lease 是 worker ownership metadata。

默认不把 `LEASED` 变成业务一级状态。

### Event != Authority

job_events 是审计历史。

`jobs.current_state`（或 P04 最终选择的现有权威）仍然是当前状态权威。

## 生产修改

如果 production deploy 没有明确授权：

`CONTROL_PLANE_DEPLOY_BLOCKED`

可以写代码、migration 和测试，但不得部署。
