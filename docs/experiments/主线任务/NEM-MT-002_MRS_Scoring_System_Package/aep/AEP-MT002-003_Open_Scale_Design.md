# AEP-MT002-003_Open_Scale_Design｜开放跑分尺度设计

## 目标

建立 MRS 的开放分数尺度，使其像跑分一样可持续突破，而不是封闭满分。

## 输入

- `nem/NEM-MT-002_MRS_Scoring_System.md`
- `rules/MRS_Benchmark_Rules.md`
- `00_NODE_STATUS.md`
- Runtime 产生的音频处理结果或测试样本

## 交付物

- 基线样本集合定义
- D_ref 或等价参考距离方案
- 分数分布预期
- 低分/高分解释区间

## 验收标准

- 基线中位数可校准到约 1000
- 高质量样本允许超过 1000
- 低质量样本可明显低于 1000
- 尺度不会产生人为满分

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
