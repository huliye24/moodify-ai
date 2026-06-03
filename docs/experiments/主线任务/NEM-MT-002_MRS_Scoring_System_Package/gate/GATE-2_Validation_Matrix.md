# GATE-2_Validation_Matrix｜验证矩阵

## Gate 目标

至少 8 项验证测试可运行，并能输出 PASS / HOLD / FAIL。

## 通过条件

- 有明确输入；
- 有明确输出；
- 有可复查日志；
- 有可下载或可归档报告；
- 失败项被记录；
- 下一步动作明确。

## 状态标记

```text
PENDING / ACTIVE / PASS / HOLD / FAIL
```

## 升级规则

只有当本 Gate 的核心条件完成并被记录后，节点才可以进入下一 Gate。若关键验证失败，应标记为 HOLD，而不是强行通过。


## Cloud Evidence - 2026-06-03

Status: `PASS` for executable matrix; version decision remains `EXPERIMENTAL`.

- Run ID: `mt002_validation_matrix_gate2_20260603`
- Runnable tests: `9`
- PASS / HOLD / FAIL: `7` / `2` / `0`
- Tracked evidence: `docs/cloud/MT002_GATE2_VALIDATION_MATRIX_EVIDENCE.md`
- Runtime report directory: `reports/mt002_mrs_validation/mt002_validation_matrix_gate2_20260603/`

HOLD items:

- `v02_v031_correlation`: v0.2/pseudo scores do not yet validate MRS Open ranking
- `loudness_cheat_resistance`: current batch has no loudness-cheat positive controls
