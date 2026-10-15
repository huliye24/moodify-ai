# 情绪波工程学 → Moodify Hear/Judge 技术吸收记录

**Date:** 2026-10-06  
**Source root:** `E:\文川院\01 学科母体\015 情绪波工程学`  
**Status:** RESEARCH ABSORPTION / EXPERIMENTAL  
**CANON_CHANGE:** NO — 本记录不改变产品身份、Judge authority、Sound Protocol 或生产 state machine。

## 结论

该学科母体中最有价值的部分不是把“情绪”直接写成一个自动分数，而是已经形成了一套与 Moodify Judge 高度一致的研究纪律：声音状态必须是多尺度的；测量、推断与价值判断必须分层；处理收益必须在响度匹配后分解；最小干预必须同时检查身份损伤和新缺陷；证据不完整或冲突时必须停止自动结论。

这些内容可立即成为 Hear/Judge 的实验契约。情绪—声学因果关系、公式权重和阈值仍处于 M0/M1，不得写入生产规则。

## 可直接采用

| 来源 | 可用技术 | Moodify 落点 | 状态 |
|---|---|---|---|
| 研究宪章 | M0–M6 证据成熟度；失败与反例保留 | Provider/Judge 实验发布门禁 | 立即采用为研究治理 |
| MATH-001 §2–3 | 时间序列、多尺度听觉状态 | 既有 `AuditoryRepresentation` + `HearingState` | 已有主体；补理论来源 |
| MATH-001 §5 | 置信度、不确定性、越界升级 | 既有 uncertainty / authority escalation | 已有实现；继续校准 |
| MATH-001 §6–7、PRINCIPLE-001 | 最小干预、身份保持、新缺陷、净增益分解 | `NetGainEvidence` | 本次新增实验契约 |
| MATH-001 §8–9 | 多源证据、最弱项与冲突不能被平均掩盖 | 既有 evidence graph / conflicts | 已有实现；禁止未经校准加权总分 |
| MATH-001 §10 | 生产案例 = 原始→表示→判断→处理→验证→人工反馈 | Treatment Record / Judge 数据飞轮 | 与现行 Canon 一致 |
| EXP-G01 | 增益与结构变化分离、响度匹配、逐算子消融 | Judge After benchmark | 可转成预注册实验 |
| SIM-003 | 采样峰值不能代表编码后发布安全 | technical verification sensor | 保留为局部技术门禁 |

## 本次代码吸收

1. `HearingObservation.theory_refs`：每项新观察可追溯到理论/实验来源，不把理论出处混入模型 provenance。
2. `NetGainEvidence`：分别记录目标收益、身份保持、新缺陷风险、响度偏差、成本、复现性与人工偏好。
3. `NetGainEvidence` 明确不输出 aggregate score；未响度匹配或关键维度缺失时返回 `INCONCLUSIVE`。
4. 即使全部技术证据方向正向，当前仍返回 `HUMAN_REQUIRED`，因为情绪增益和作品完成度尚无获授权的机器裁决范围。
5. 无目标收益或出现新缺陷时建议 `KEEP_ORIGINAL`；身份漂移进入人工升级。

## 暂不采用为生产能力

| 内容 | 原因 | 正确处理 |
|---|---|---|
| “情绪波场”作为物理实体 | 原文明确未被实验证实 | 只作为研究隐喻/假设 |
| `AI_aud` 六能力乘法总分 | 权重未定义，维度不可直接比较 | 用作架构完整性检查，不计算产品分数 |
| 声学状态与目标情绪的直接距离 | `z*`、感知权重与条件变量均未拟合 | 建立人类标注任务后再训练/校准 |
| 熵阈值自动执行 | 概率可能失校准，阈值待拟合 | 先做 reliability/ECE 与盲测 |
| 加权验证总分 | 平均会掩盖关键失败 | 维度分报 + blocking guardrails |
| 能力成长、难度、壁垒公式 | 属战略/商业模型而非音频事实 | 不进入 Core runtime |
| 旧 `clean_master` 观察 | 该预设已被当前 Canon 退场 | 仅作为历史案例，不恢复产品入口 |

## 下一实验包

建议把 EXP-001 与 EXP-002 改写为 Judge-1 首批预注册任务：

1. 至少 10 首有权利的作品，按作品/创作者隔离；
2. ORIGINAL、A、B 全部响度匹配并盲化；
3. 评分维度分离：目标表达、完成度、疲劳、异常、身份保持；
4. 保存逐算子和完整链，估计边际贡献与交互损伤；
5. 结果写入 Treatment Record 候选区，不自动进入训练集；
6. 先验证“系统知道何时 INCONCLUSIVE / KEEP_ORIGINAL”，再追求命中率。

## 回滚

本次仅增加实验性数据契约和研究文档。回滚时删除 `moodify.auditory.net_gain`、相应测试，并移除 `HearingObservation.theory_refs`；不影响既有报告、Sound Protocol 或生产处理流程。
