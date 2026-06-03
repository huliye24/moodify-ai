# AEP-MT002-008_Real_AI_Music_Benchmark_Run｜真实 AI 音乐样本基准运行

## 目标

用真实 Suno / Udio / AI 音乐样本跑第一轮 MRS 基准测试。

## 输入

- `nem/NEM-MT-002_MRS_Scoring_System.md`
- `rules/MRS_Benchmark_Rules.md`
- `00_NODE_STATUS.md`
- Runtime 产生的音频处理结果或测试样本

## 交付物

- 10-30 首真实 AI 音乐样本
- 原始样本评分
- 处理后样本评分
- ΔMRS 统计

## 验收标准

- 样本来源记录清楚
- 每个样本有 MRS 记录
- 报告中有分布、排名、异常样本
- 结果进入 reports/

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
