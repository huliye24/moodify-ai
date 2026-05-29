# 题目 A7：Pareto 前沿策略

**来源**: 母文件 §9 题目 A7
**类型**: 后续 AI 题目规格书
**产出**: Pareto 计算 + 三种选择策略

---

## 0. 题目定义

把 top-3 从「单一分数排序」改为「Pareto 前沿 + 模式选择」。给出 creator / release / conservative 三种选择策略。

---

## 1. Pareto 前沿计算

```python
def pareto_frontier(candidates, objectives):
    """
    objectives: list of (key, direction)
      例: [("edsr_proxy", "max"), ("whs", "max"), ("lfr", "min"), ("artifact_risk", "min")]
    """
    n = len(candidates)
    dominated = [False] * n
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if dominates(candidates[j], candidates[i], objectives):
                dominated[i] = True
                break
    return [c for i, c in enumerate(candidates) if not dominated[i]]


def dominates(a, b, objectives):
    all_at_least_as_good = True
    any_strictly_better = False
    for key, direction in objectives:
        if direction == "max":
            if a[key] < b[key]: all_at_least_as_good = False
            if a[key] > b[key]: any_strictly_better = True
        else:
            if a[key] > b[key]: all_at_least_as_good = False
            if a[key] < b[key]: any_strictly_better = True
    return all_at_least_as_good and any_strictly_better
```

---

## 2. 三种选择策略

```python
def select_creator(frontier):
    """创作者模式: 优先 EDSR 和风格保留"""
    return max(frontier, key=lambda c:
        0.4 * c["edsr_proxy"] + 0.3 * c["style_preservation"] + 0.2 * c["whs"] + 0.1 * (100 - c["lfr"])
    )

def select_release(frontier):
    """发布者模式: 优先 WHS 和低伪影"""
    return max(frontier, key=lambda c:
        0.35 * c["whs"] + 0.30 * (100 - c["artifact_risk"] * 100) + 0.20 * c["edsr_proxy"] + 0.15 * (100 - c["lfr"])
    )

def select_conservative(frontier):
    """保守模式: 优先低风险和高保真"""
    return max(frontier, key=lambda c:
        0.35 * (100 - c["lfr"]) + 0.30 * c["style_preservation"] + 0.20 * c["whs"] + 0.15 * c["edsr_proxy"]
    )
```

---

## 3. 多版本展示格式

```json
{
  "pareto_frontier": [
    {
      "version_id": "v1",
      "label": "更清晰",
      "strengths": {"whs": 85, "edsr_proxy": 70},
      "tradeoffs": {"lfr": 15},
      "description": "声音干净通透, 轻微疲劳风险"
    },
    {
      "version_id": "v2",
      "label": "更温暖",
      "strengths": {"edsr_proxy": 74, "style_preservation": 0.92},
      "tradeoffs": {"whs": 78},
      "description": "保留更多原始质感, 温暖舒适"
    }
  ],
  "recommended_mode": {
    "creator": "v2",
    "release": "v1",
    "conservative": "v2"
  }
}
```

---

## 4. 产物清单

1. `pareto/frontier.py` — Pareto 计算
2. `pareto/selectors.py` — 三种选择策略
3. `pareto/display_format.json` — 多版本展示格式
4. `pareto/tests.py` — 已知案例的 Pareto 测试

---

## 5. 理论参考

- Pareto (1906), Deb et al. (2002): NSGA-II
- Miettinen (1999): Multiobjective Optimization
- 母文件定理 7

---

*Moodify 题目规格书 · A7 · v1.0*
