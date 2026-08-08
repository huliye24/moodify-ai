# Human vs Moodify Evaluation Framework

状态：Protocol draft v0.1。目的不是证明预设结论，而是在限定任务上检验 Moodify 相对人工工作流的优势与失败边界。

## 三组对照

- A：原始 AI 生成音乐；
- B：专业人工工作流处理；
- C：Moodify 处理。

固定同一源文件哈希、交付目标和允许资产。保存 B/C 的工具版本、处理条件、人时、机器时和成本。B 的工程师背景与 C 的 pipeline/rules 必须登记。

## 评价维度

| 类别 | 指标 |
|---|---|
| Perceptual Quality | vocal naturalness、clarity、transient definition、tonal balance、spatial stability、fatigue、emotional coherence |
| Technical Quality | loudness、true peak、dynamics、clipping、phase、stereo correlation、masking、spectral anomalies |
| Structural Integrity | section consistency、vocal identity continuity、rhythmic stability、melody preservation、lyric alignment、arrangement coherence |
| Production Performance | runtime、human time、candidate count、reproducibility、failure rate、cost/song、batch consistency |

## 实验设计

1. 先预注册任务、样本纳入/排除、主要/次要终点、阈值、停止条件和统计方法。
2. 感知评价采用响度匹配、盲听、每听众随机顺序；A/B/C 身份不可由文件名泄露。
3. 专业人员与普通听众分层报告，不合并掩盖差异。
4. 技术测量独立于感知选择；标准 backend、版本、单位和置信度必须保存。
5. 结构评价以人工校正参考为准，报告自动估计误差而非只报成功率。
6. 保存所有失败、平局和 Moodify 输给人工的样本；不得事后删异常样本。
7. 不按单案例宣布结论，不用“音质提升百分比”作为唯一结论。

## 分析与报告

报告样本量、均值/中位数、分布、置信区间、个体偏好、失败率和分层结果。主要比较为 C vs B；A 用于显示两种处理相对原始的变化。多重维度须标明主要终点或进行校正。生产性能同时报告质量与资源，不用更快自动推导更好。

## 优势主张门禁

只有当预注册主要终点、失败率、复现率与成本共同达到阈值，且跨多个授权案例重复，才允许表达“在限定任务 X 上显示优势”。允许的结论必须包含样本、任务、版本、时间、局限和 Moodify 失败案例。否则结论为 HOLD/REWORK。

