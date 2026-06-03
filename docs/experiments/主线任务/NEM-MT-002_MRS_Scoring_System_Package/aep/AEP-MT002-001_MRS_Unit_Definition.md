# AEP-MT002-001_MRS_Unit_Definition｜MRS 单位定义

## 目标

定义 MRS 作为 AI 音乐真实度开放跑分单位，明确数值含义、方向、基准锚点和无满分原则。

## 输入

- `nem/NEM-MT-002_MRS_Scoring_System.md`
- `rules/MRS_Benchmark_Rules.md`
- `00_NODE_STATUS.md`
- Runtime 产生的音频处理结果或测试样本

## 交付物

- MRS 单位说明
- 开放尺度定义
- 基线中位数约 1000 的原则
- 不得使用 0-100 满分制

## 验收标准

- MRS 数值方向明确
- 基线与突破含义明确
- 人类听感只作为 sanity check
- 写入 rules/MRS_Benchmark_Rules.md

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
