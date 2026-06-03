# AEP-MT002-009_MRS_Report_System｜MRS 报告系统

## 目标

生成适合人和 AI 继续分析的 MRS 运行报告。

## 输入

- `nem/NEM-MT-002_MRS_Scoring_System.md`
- `rules/MRS_Benchmark_Rules.md`
- `00_NODE_STATUS.md`
- Runtime 产生的音频处理结果或测试样本

## 交付物

- 单样本报告
- 批量排名报告
- 验证矩阵报告
- 异常样本报告

## 验收标准

- 报告可读
- 包含核心表格
- 包含下一步建议
- 能直接交给 AI 继续分析

## 失败处理

如果本 AEP 未通过验收，不得进入下一 Gate。失败原因应写入：

- `reports/`
- `logs/`
- `decisions/Decision_Log.md`
- `backlog/MT-002_Backlog.md`

## AI 执行要求

- 只推进本 AEP 范围内的内容。
- 不要改动无关节点。
- 如果需要修改评分标准，必须写入 Decision Log。
- 如果验证失败，标记为 HOLD，不要强行 ADOPT。
