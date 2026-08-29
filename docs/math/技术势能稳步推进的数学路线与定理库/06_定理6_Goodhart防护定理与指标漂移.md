# 定理 6：Goodhart 防护定理与指标漂移

**来源**: 技术势能稳步推进的数学路线与定理库 §3 定理6
**层级**: 内部工作定理 — 防止优化目标被指标绑架
**状态**: 待实施 — 随着搜索和代理指标的使用日益重要

---

## 0. 定理陈述

### 0.1 自然语言

当代理指标成为唯一优化目标时，它会逐渐失去代表真实目标的能力。任何单一指标被持续优化后，必然被找到漏洞。

### 0.2 形式化

```
Optimize ProxyScore alone
→ DistributionShift(ProxyScore, HumanPreference)
→ ProxyValidity decreases monotonically over optimization steps
```

防护：保留人耳盲测、保留隐藏验证集、保留多风险指标、记录反例。

---

## 1. Goodhart 效应的具体机制

### 1.1 四阶段退化模型

```
Stage 1 (初始):
  ProxyScore 与 HumanPreference 正相关 (ρ ≈ 0.6)
  搜索提升 ProxyScore → 也提升 HumanPreference

Stage 2 (边际):
  ProxyScore 继续上升, HumanPreference 趋于平稳
  搜索找到了"指标上好看但听感无差异"的区域

Stage 3 (过拟合):
  ProxyScore 上升, HumanPreference 下降
  搜索找到了指标的漏洞 (如过度提亮被 WHS 的 AirBand 项奖励)

Stage 4 (崩塌):
  ProxyScore 和 HumanPreference 的相关性变为负
  代理指标已经完全被 hack
```

### 1.2 Moodify 中最可能被 hack 的指标

| 指标 | 如何被 hack | 听感后果 |
|------|-----------|---------|
| WHS | 把所有 EQ 增益调到安全上限 → 所有频段"健康" | 声音扁平、过度处理 |
| EDS_proxy | 选择使 5D 距离最小化的参数, 忽略缺陷消除 | 指标高但情绪失真 |
| LFR | 降低所有高频 → 疲劳风险 = 0 | 声音闷、无空气感 |
| defect_resolution | 过度 EQ → 缺陷"消失"但引入新伪影 | 头痛医头, 整体劣化 |

---

## 2. 防护策略

### 2.1 多指标制衡

不让任何单一指标垄断排序。

```
综合分数 ≠ WHS (不使用单一指标)
综合分数 ≠ EDSR_proxy alone

综合排序 = Pareto 前沿 (WHS, EDSR_proxy, LFR, ArtifactRisk)
或: 综合分数 = w1*WHS + w2*EDSR + w3*(100-LFR) + w4*(100-ArtifactRisk)
            其中权重由人耳校准实验确定, 不手工设定
```

### 2.2 隐藏验证集

保留 10% 的处理案例不进入训练/校准流程。定期用隐藏集评估：

```
每 100 次处理:
  - 从隐藏集中随机选 5 个案例
  - 运行当前模型
  - 人工评估 (或 A/B 比较)
  - 对比 ProxyScore 的预测

若隐藏集上的 ρ 开始下降 → Goodhart 效应正在发生 → 需要指标重构
```

### 2.3 反例触发规则

```
触发条件 (任意一条满足即触发):
  1. WHS 上升 > 10 但 EDSR_proxy 下降 > 5
  2. EDSR_proxy 上升 > 15 但 WHS 下降 > 5
  3. LFR 下降 > 20 但 EDSR_proxy 下降 > 10
  4. 连续 5 次处理的 ProxyScore 都在上升但用户反馈没有改善

触发后:
  - 标记该案例为反例
  - 将反例加入校准数据集
  - 若连续触发 > 3 次, 暂停自动推荐, 进入人工审核模式
```

### 2.4 指标漂移监控面板

```
每个指标维护:
  - 最近 100 次处理的均值
  - 最近 100 次处理的标准差
  - 最近 100 次中 ProxyScore 与 HumanFeedback 的 ρ

可视化:
  - ρ 随时间的变化趋势线
  - 触发警报: ρ 连续 2 周下降 → ⚠️ 指标正在漂移
```

---

## 3. 留给后续 AI 的题目 (A6)

**题目 A6：设计 Moodify Goodhart Guard。**

要求输出:
1. 多指标综合方案 (权重来源: 校准实验, 不手工设定)
2. 隐藏验证集管理规则
3. 反例触发规则和自动响应流程
4. 指标漂移监控方案
5. 指标重构的触发条件

---

## 4. 理论参考

1. Goodhart, C. A. E. (1975). "Problems of Monetary Management: The U.K. Experience." In *Papers in Monetary Economics*. Reserve Bank of Australia. — 原始 Goodhart 定律。

2. Campbell, D. T. (1976). "Assessing the Impact of Planned Social Change." — Campbell 定律: 指标被用于决策后会被扭曲。

3. Manheim, D. & Garrabrant, S. (2018). "Categorizing Variants of Goodhart's Law." *arXiv:1803.04585*. — Goodhart 效应的四种变体分类。

4. Strathern, M. (1997). "Improving Ratings: Audit in the British University System." *European Review*, 5(3), 305-321. — "When a measure becomes a target, it ceases to be a good measure."

5. 母文件 §3 定理6：Goodhart 防护定理。

---

*Moodify 定理库 · 定理 6 · v1.0*
