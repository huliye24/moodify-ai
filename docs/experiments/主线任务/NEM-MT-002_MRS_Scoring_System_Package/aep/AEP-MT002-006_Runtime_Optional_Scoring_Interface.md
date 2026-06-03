# AEP-MT002-006_Runtime_Optional_Scoring_Interface｜Runtime 可选评分接口

## 目标

让 MRS 接入 Runtime，但作为可选评分列，不阻塞主音频处理流程。

## 输入

- `nem/NEM-MT-002_MRS_Scoring_System.md`
- `rules/MRS_Benchmark_Rules.md`
- `00_NODE_STATUS.md`
- Runtime 产生的音频处理结果或测试样本

## 交付物

- off 模式
- quick_mrs 模式
- full_mrs 模式
- mrs_open_v031 模式

## 验收标准

- 不开启 MRS 时主流程正常
- 开启 MRS 时报告增加评分列
- MRS 失败不导致音频处理失败
- 耗时单独记录

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
