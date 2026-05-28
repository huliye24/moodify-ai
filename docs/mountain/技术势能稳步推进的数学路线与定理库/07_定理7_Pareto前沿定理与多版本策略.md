# 定理 7：Pareto 前沿定理与多版本策略

**来源**: 技术势能稳步推进的数学路线与定理库 §3 定理7
**层级**: 内部工作定理 — 从单最优到多目标权衡
**状态**: 待实施 — 当前 top-3 仍然用单一分数排序

---

## 0. 定理陈述

### 0.1 自然语言

Moodify 的真实目标是多目标约束优化，不应过早压成单一分数。当两个候选在所有目标上各有优劣时，不应强行选一个——应该展示 Pareto 前沿。

### 0.2 形式化

Moodify 的目标至少包括：

```
maximize EDSR_true
maximize WHS
minimize LFR
minimize ArtifactRisk
minimize Latency
minimize Cost
preserve StyleIdentity
```

候选 A 支配候选 B：

```
A dominates B ⇔
  ∀ objective o: A_o ≥ B_o  (对最大化目标)
  ∧ ∃ objective o: A_o > B_o
```

Pareto 前沿 = {c | ¬∃ c' that dominates c}

---

## 1. 当前 top-3 的问题

SPEC-002-REV 的 top-3 选择基于单一 proxy score。这意味着：

1. 如果最佳 proxy 版本过度压缩了动态（WHS 高但 LFR 也高），系统不会注意到
2. 用户无法看到「更清晰」和「更温暖」两个不同方向的版本
3. 排名第 2 的版本可能在第 1 无法覆盖的维度上更好

### 1.1 例子

```
三个候选:
  A: WHS=85, EDS=70, LFR=15, ArtifactRisk=0.05  → proxy=82
  B: WHS=78, EDS=74, LFR=8,  ArtifactRisk=0.02  → proxy=76
  C: WHS=80, EDS=72, LFR=10, ArtifactRisk=0.08  → proxy=78

按 proxy 排序: A > C > B
按 Pareto: A 和 B 互不支配 (A 在 WHS 更好, B 在 EDS/LFR 更好)
           C 被 B 支配 (B 在 EDS 更好, LFR 更低, ArtifactRisk 更低)
           → Pareto 前沿 = {A, B}
```

系统应该展示 A 和 B 给用户，而不是只展示 A。

---

## 2. Moodify 的多目标

### 2.1 目标定义

| 目标 | 方向 | 测量方式 | 权重来源 |
|------|------|---------|---------|
| EDSR_true | maximize | A/B 偏好或 Bradley-Terry θ | 人耳校准 |
| WHS | maximize | health_scorer.compute_whs() | 人耳校准 |
| LFR | minimize | risk_model 或听力疲劳检测 | 人耳校准 |
| ArtifactRisk | minimize | 伪影检测 (泵浦/相位/失真) | 人耳校准 |
| StyleIdentity | preserve | 原始 5D 向量的关键维度偏移 < 阈值 | 人耳校准 |
| Latency | minimize | time.perf_counter() | 工程约束 |
| Cost | minimize | API 调用次数 × 单价 | 工程约束 |

### 2.2 非 Pareto 的实用选择策略

当 Pareto 前沿上有多于 3 个候选时，用选择策略进一步筛选：

```
creator_mode (创作者):
  偏好: 高 EDSR, 风格保留
  不偏好: 不关心延迟和成本

release_mode (发布者):
  偏好: 高 WHS, 低 ArtifactRisk
  不偏好: 可能牺牲一些 EDSR 换取干净

conservative_mode (保守):
  偏好: 低 LFR, 最小风格偏移
  不偏好: 拒绝高风险的参数改动
```

每个模式的偏好体现为 m 个目标上的权重向量。在 Pareto 前沿上选加权最优。

---

## 3. 从单分数到 Pareto 的代码迁移

### 3.1 当前代码

```python
scored.sort(key=lambda x: x[1], reverse=True)  # 单分数
return scored[:top_k]
```

### 3.2 目标代码

```python
def pareto_frontier(candidates, objectives):
    """objectives: list of (key, direction) pairs
       direction: 'max' or 'min'
    """
    frontier = []
    for c in candidates:
        dominated = False
        for other in candidates:
            if dominates(other, c, objectives):
                dominated = True
                break
        if not dominated:
            frontier.append(c)
    return frontier

def dominates(a, b, objectives):
    at_least_as_good = all(
        a[key] >= b[key] if direction == 'max' else a[key] <= b[key]
        for key, direction in objectives
    )
    strictly_better = any(
        a[key] > b[key] if direction == 'max' else a[key] < b[key]
        for key, direction in objectives
    )
    return at_least_as_good and strictly_better
```

---

## 4. 留给后续 AI 的题目 (A7)

**题目 A7：把 top-3 从「单一分数排序」改为「Pareto 前沿 + 模式选择」。**

要求输出:
1. Pareto 前沿计算 (O(n²) 足够, n ≤ 2000)
2. 三种选择策略: creator / release / conservative
3. 多版本展示的 UI 描述 (每个版本标注在哪些维度上更强)
4. 默认版本选择逻辑 (当用户不选时)

---

## 5. 理论参考

1. Pareto, V. (1906). *Manual of Political Economy*. — Pareto 最优的原始概念。

2. Deb, K., Pratap, A., Agarwal, S., & Meyarivan, T. (2002). "A Fast and Elitist Multiobjective Genetic Algorithm: NSGA-II." *IEEE Transactions on Evolutionary Computation*, 6(2), 182-197. — 多目标优化的经典算法。

3. Miettinen, K. (1999). *Nonlinear Multiobjective Optimization*. Springer. — 多目标优化的数学基础。

4. 母文件 §3 定理7：Pareto 前沿定理。

---

*Moodify 定理库 · 定理 7 · v1.0*
