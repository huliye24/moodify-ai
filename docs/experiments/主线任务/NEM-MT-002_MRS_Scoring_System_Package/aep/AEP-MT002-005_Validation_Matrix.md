# AEP-MT002-005_Validation_Matrix｜验证矩阵建立

## 目标

建立 MRS 每次升级必须通过的验证矩阵。

## 输入

- `nem/NEM-MT-002_MRS_Scoring_System.md`
- `rules/MRS_Benchmark_Rules.md`
- `00_NODE_STATUS.md`
- Runtime 产生的音频处理结果或测试样本

## 交付物

- monotonicity
- scale validation
- no ceiling
- v0.2/v0.3.1 correlation
- bad-sample suppression
- improvement reward
- loudness-cheat resistance
- stability
- HQ damage sensitivity

## 验收标准

- 至少 8 项验证可运行
- 每项有 PASS/HOLD/FAIL
- 结果保存为报告
- 失败项进入 backlog

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
