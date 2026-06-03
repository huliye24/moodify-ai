# AEP-MT002-002_Acoustic_Feature_Dimensions｜声学特征维度整理

## 目标

整理 MRS 所依赖的数学、物理、声学和信号处理特征族。

## 输入

- `nem/NEM-MT-002_MRS_Scoring_System.md`
- `rules/MRS_Benchmark_Rules.md`
- `00_NODE_STATUS.md`
- Runtime 产生的音频处理结果或测试样本

## 交付物

- 频谱真实度特征
- 动态真实度特征
- 瞬态真实度特征
- 空间真实度特征
- 质感与破坏性惩罚特征

## 验收标准

- 每个维度至少有 2 个候选特征
- 特征可以被 Python 提取
- 特征解释符合声学逻辑
- 特征被写入模板或配置

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
