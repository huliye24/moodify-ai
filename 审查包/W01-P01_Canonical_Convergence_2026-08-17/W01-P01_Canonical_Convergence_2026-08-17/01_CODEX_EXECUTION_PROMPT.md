# Codex Execution Prompt — W01-P01

你正在执行：

**Moodify Cognitive Wave 01 / W01-P01 — Canonical Convergence**

## 第一步：必须读取 P00

如果以下输入不存在，停止：

- P00 Executive Reality Summary
- P00 GitHub Reality
- P00 Task Reality
- P00 Cloud Reality
- P00 Data/External Reality
- P00 Truth Table
- P00 Conflict List
- P00 Current System Map
- P00 Evidence Index

状态：

`STOP — P00_INCOMPLETE`

## 第二步：区分事实与决策

- P00 负责“事实”
- P01 负责“权威决策”
- 不允许用理想状态重写 P00 的事实

## 当前最高产品方向

- 唯一对外产品面：Moodify Music / Player
- 第一阶段核心用户动作：PLAY
- Moodify Ear / Auditory Intelligence：内部听觉、判断、验证与研究系统
- 内部可以复杂，用户表面保持极简
- 不创建第二个公开产品身份

## 你可以修改

- README
- AGENTS
- canonical docs
- repository status / authority policy
- 极小的 Canon drift guard

## 你不能修改

- runtime behavior
- audio pipeline
- servers
- database
- OSS
- production config
- state machine
- worker orchestration
- PR merge state

## 所有冲突必须进入 Decision Register

允许状态：

- CANONICAL
- INTERNAL
- EXPERIMENTAL
- LEGACY
- MIGRATION_PENDING
- HUMAN_DECISION_REQUIRED
- REMOVE_LATER

无法确认就写 `HUMAN_DECISION_REQUIRED`。

完成后停止，不进入 P02。
