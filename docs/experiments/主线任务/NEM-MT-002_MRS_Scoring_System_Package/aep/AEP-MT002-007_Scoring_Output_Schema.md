# AEP-MT002-007_Scoring_Output_Schema｜评分输出 Schema

## 目标

定义每首音频的 MRS 输出记录格式，保证后续可统计、可比较、可追踪。

## 输入

- `nem/NEM-MT-002_MRS_Scoring_System.md`
- `rules/MRS_Benchmark_Rules.md`
- `00_NODE_STATUS.md`
- Runtime 产生的音频处理结果或测试样本

## 交付物

- score_record schema
- validation_result schema
- run_summary schema
- CSV/JSONL 输出字段

## 验收标准

- 每条评分记录包含 sample_id、version、preset、score、subscores、duration、status
- 字段命名稳定
- 支持后续数据库导入
- schema 通过 JSON 校验

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
