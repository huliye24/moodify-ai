# AEP-MT002-010_MRS_Versioning_Rules｜MRS 版本升级规则

## 目标

建立 MRS 公式与配置升级规则，防止评分标准频繁漂移。

## 输入

- `nem/NEM-MT-002_MRS_Scoring_System.md`
- `rules/MRS_Benchmark_Rules.md`
- `00_NODE_STATUS.md`
- Runtime 产生的音频处理结果或测试样本

## 交付物

- 版本号规则
- 升级条件
- 回归测试要求
- Decision Log 记录要求

## 验收标准

- 每次升级有版本号
- 升级前后结果可比较
- 必须通过验证矩阵
- 失败项不得直接 ADOPT

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
