# Codex Execution Prompt — W02-P00

执行：

**W02-P00 — Wave 02 Re-entry Gate**

## Hard Gate

必须读取 W01-P09 的真实执行结果。

如果只有任务模板，没有实际 closeout：

`STOP — W01_CLOSEOUT_NOT_AVAILABLE`

## 三个任务

1. Verify Wave 01 Closeout Reality
2. Validate New Cognitive Riverbed
3. Produce ≤3 Wave 02 problem candidates + Human Gate

## 默认只读

不要：

- 开发
- 部署
- 改服务器
- 改 DB/OSS
- 改 Android
- 改 pipeline
- 改 state machine
- 自动选候选

## 最终

输出：

- current reality revalidation
- riverbed capitalization check
- cold start retest
- drift/debt/unknown
- max 3 candidates
- human selection gate

没有人类选择，不进入 W02-P01。
