# AEP-MT002-004_Synthetic_Control_Set｜合成控制样本集

## 目标

建立可重复生成的合成控制样本，用来测试 MRS 的方向性和抗作弊能力。

## 输入

- `nem/NEM-MT-002_MRS_Scoring_System.md`
- `rules/MRS_Benchmark_Rules.md`
- `00_NODE_STATUS.md`
- Runtime 产生的音频处理结果或测试样本

## 交付物

- over_bright 样本
- over_dark 样本
- loudness_only 样本
- transient_damage 样本
- hq_damage 样本

## 验收标准

- 样本生成过程可复现
- 每类样本有预期评分方向
- 能用于回归测试
- 输出写入验证报告

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
