# 13 — Control Plane Test Report

**W01-P04 · 2026-08-17 · 12/12 PASS（tests/test_control_plane.py）**

| 测试 | 验证 | 结果 |
|---|---|---|
| TST-01 Concurrent Claim | 双 worker 并发 claim 只有一个 owner（CP-INV-05） | PASS |
| TST-02 Lease Expiry Recovery | lease 过期 → 恢复；stale worker 不能覆盖（CP-INV-17） | PASS |
| TST-03 Duplicate Complete | 重复 complete 幂等，无重复 READY 事件 | PASS |
| TST-04 Retry Budget | transient 重试预算耗尽 → FAILED（CP-INV-09） | PASS |
| TST-05 Permanent Failure | INPUT_INVALID 不盲目重试 | PASS |
| TST-06 Control Restart | 重开连接状态从 DB 恢复（CP-INV-11/18） | PASS |
| TST-07 OSS/DB Split Brain | object 未注册 → 无 false READY | PASS |
| TST-08 READY Guard | 无 artifact → 拒绝（CP-INV-13） | PASS |
| TST-09 Terminal Protection | READY 不可回退（CP-INV-08） | PASS |
| TST-10 Idempotent Create | 同 key 同指纹 → 同一 job | PASS |
| TST-11 Idempotency Conflict | 同 key 不同指纹 → 冲突 | PASS |
| TST-12 Event Completeness | 每次迁移 append 事件（CP-INV-03） | PASS |

## 执行

```text
python -m pytest moodify-core-package/tests/test_control_plane.py
12 passed in 3.53s

连同 P03（9）+ guard（3）：24 passed in 8.62s
ruff：All checks passed
```

## 迁移矩阵校验

```text
validate_transition_matrix.py 02_STATE_TRANSITION_MATRIX.csv
OK: 16 transitions passed basic W01-P04 checks
```

## 覆盖说明

- 测试基于 SQLite（与 P03 同一实现）；PolarDB/生产 worker 未接（CONTROL_PLANE_DEPLOY_BLOCKED）。
- 全量回归未跑（新增模块与既有代码无交集；data_plane 包已隔离）。
