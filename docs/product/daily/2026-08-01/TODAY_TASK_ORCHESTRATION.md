# 2026-08-01｜今日新增任务编排

## 新增任务

`DSK-MFY-SPECTRAL-EVIDENCE-012｜处理前后频谱证据与研究数据包 v0.1`

任务包：

```text
E:\moodify\docs\tasks\deepseek\DSK-MFY-SPECTRAL-EVIDENCE-012\
```

## 执行位置

本任务是今天稍后执行的新增独立任务，不覆盖今天既有任务、验收事实或用户修改。开始前先确认当前没有另一个 Worker 正在修改相同目录；只能串行执行。

建议时间盒：4 小时。

1. 45 分钟：冻结证据、参数、指标、Excel 和解释边界合同；
2. 75 分钟：实现整曲/stem 的 before、after、difference 频谱与结构化测量；
3. 60 分钟：生成 JSON、CSV/可用时 Parquet 和 XLSX 研究包；
4. 60 分钟：确定性复验、失败注入、源哈希校验和 HANDOFF。

若今天剩余时间不足，必须停在完整阶段边界，更新 PROGRESS/HANDOFF 并顺延，不得并行赶工或降低证据要求。

## 今日完成门槛

只有满足以下条件才可交给 Codex 验收：

- before/after 使用完全一致的分析参数和色标；
- 图像、结构化数据和 Excel 可相互追溯；
- 源音频和历史记录未改变；
- 人工评价没有被自动填写；
- 未把频谱或指标变化写成音质改善结论；
- 有合法真实样本则记录实际运行；没有则明确 `REAL_DATA_NOT_RUN`。

