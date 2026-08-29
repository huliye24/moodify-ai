# 15 — P04 Acceptance Report

**W01-P04 · 2026-08-17 · base: P00 + P01 (ea8256c7) + P02 + P03 (e78f348)**

## 验收标准逐项（任务书 §21）

- [x] P03 Data Identity Gate 通过（Data Identity Contract/模型/Invariants/Handoff 已读）
- [x] Existing Authority Discovery 完成（01 报告，7 个候选系统 + 缺口）
- [x] 只有一个 authoritative state machine（JobControlPlane，8 态）
- [x] State 与 Stage 分离（CP-INV-16）
- [x] transition matrix 完成（16 条，脚本校验 OK）
- [x] 所有 state change 可追溯（append-only events，TST-12）
- [x] event log 不成为第二状态权威（CP-INV-04）
- [x] 一个 Job 同时最多一个有效 lease（TST-01，CP-INV-05）
- [x] lease 有 expiry（TTL 1h + heartbeat，TST-02）
- [x] stale worker 无法覆盖新 attempt（fencing，TST-02）
- [x] retry 有预算（14 class × max_attempts，TST-04）
- [x] permanent failure 不盲目 retry（TST-05）
- [x] restart/recovery 不依赖进程内存（TST-06）
- [x] create/transition/complete 有 idempotency（TST-03/10/11）
- [x] READY 有 artifact guard（TST-08）
- [x] READY 有 verification guard（TST-08）
- [x] terminal state 受保护（TST-09）
- [x] failure taxonomy 结构化（08 报告，14 class）
- [x] queue summary / stale lease 可观测（queue_summary()）
- [x] logs 可按 job/attempt/correlation 查询（events/attempts 表）
- [x] 不引入第二套 queue/state authority
- [x] 未授权时 production deploy 保持 BLOCKED（CONTROL_PLANE_DEPLOY_BLOCKED）
- [x] P05 Handoff 完成（14 报告）
- [x] 完成后停止，不进入 P05

## 代码清单（本包新增/修改）

```
moodify-core-package/src/moodify/data_plane/control.py   (新增: JobControlPlane + CONTROL_SCHEMA + FailureRecord + FAILURE_CLASSES)
moodify-core-package/src/moodify/data_plane/__init__.py  (导出 JobControlPlane)
moodify-core-package/tests/test_control_plane.py         (新增: 12 测试 TST-01..12)
```

## 验证

- pytest：12/12（control）+ 9（data plane）+ 3（guard）= 24 passed
- ruff：All checks passed
- validate_transition_matrix.py：16 transitions OK

## 事实边界

1. 生产 worker（node/ LA/杭州）未切换；全部为 SQLite 实现（PolarDB write gate BLOCKED）。
2. reconstruction_job/（未跟踪并行工作）未触碰；其状态映射已记录（02 报告），合并决策待并行会话完成。
3. 本包未跑全量回归（新增模块与既有代码无交集）。
