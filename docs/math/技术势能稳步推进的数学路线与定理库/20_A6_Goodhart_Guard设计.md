# 题目 A6：Goodhart Guard 设计

**来源**: 母文件 §9 题目 A6
**类型**: 后续 AI 题目规格书
**产出**: 多指标制衡 + 隐藏验证集 + 反例触发 + 指标漂移监控

---

## 0. 题目定义

设计 Moodify Goodhart Guard。定义指标漂移检测、隐藏样本验证、反例触发规则。

---

## 1. 多指标综合方案

### 1.1 指标体系

```
Primary (受保护, 不可单独优化):
  EDSR_true — 人耳偏好 (金标准, 但获取昂贵)
  EDSR_proxy — 代理指标 (快速, 但会漂移)

Supporting (用于制衡):
  WHS — 声学健康度
  LFR — 听力疲劳风险
  ArtifactRisk — 伪影风险
  StylePreservation — 风格保持度

Engineering (约束, 非目标):
  Latency — 处理延迟
  Cost — API 调用成本
```

### 1.2 综合分数

```python
def composite_score(candidate, weights_from_calibration):
    return (
        weights_from_calibration["edsr_proxy"] * candidate.edsr_proxy
        + weights_from_calibration["whs"] * candidate.whs
        + weights_from_calibration["lfr_penalty"] * (100 - candidate.lfr)
        + weights_from_calibration["artifact_penalty"] * (100 - candidate.artifact_risk * 100)
        + weights_from_calibration["style_preservation"] * candidate.style_similarity * 100
    )
# 所有权重来自定理 2 的校准实验, 不手工设定
```

---

## 2. 隐藏验证集管理

```python
HIDDEN_VALIDATION_SIZE = max(10, total_cases * 0.1)  # 至少 10 个, 最多 10%

# 选取: 随机选择, 分层保证情绪和风格覆盖
# 存储: 文件标记 hidden=True, 不参与训练/校准/检索
# 评估: 每 100 次处理后, 在隐藏集上运行
```

---

## 3. 反例触发规则

```python
ANTI_PATTERN_RULES = [
    {
        "condition": lambda c: c.whs_delta > 10 and c.edsr_proxy_delta < -5,
        "message": "WHS 大幅上升但 EDSR_proxy 下降",
        "action": "flag_as_counterexample"
    },
    {
        "condition": lambda c: c.edsr_proxy_delta > 15 and c.whs_delta < -5,
        "message": "EDSR_proxy 大幅上升但 WHS 下降",
        "action": "flag_as_counterexample"
    },
    {
        "condition": lambda history: all(h.edsr_proxy_delta > 0 for h in history[-5:])
            and all(h.user_satisfied == False for h in history[-5:] if h.user_satisfied is not None),
        "message": "连续 5 次 proxy 上升但用户反馈无改善",
        "action": "pause_auto_recommend"
    },
]
```

---

## 4. 指标漂移监控

```python
class DriftMonitor:
    def __init__(self, window_size=100):
        self.window_size = window_size
        self.history = []

    def add(self, proxy_score, human_feedback):
        self.history.append((proxy_score, human_feedback))

    def check(self):
        if len(self.history) < self.window_size:
            return "insufficient_data"

        recent = self.history[-self.window_size:]
        proxy_trend = linregress(range(len(recent)), [r[0] for r in recent]).slope
        human_trend = linregress(range(len(recent)), [r[1] for r in recent if r[1] is not None]).slope

        if proxy_trend > 0.01 and human_trend < -0.01:
            return "⚠️ Proxy diverging from human preference"
        return "stable"
```

---

## 5. 产物清单

1. `goodhart/composite_score.py`
2. `goodhart/hidden_validation.py`
3. `goodhart/anti_pattern_detector.py`
4. `goodhart/drift_monitor.py`
5. `goodhart/dashboard.html` (可视化)

---

## 6. 理论参考

- Goodhart (1975), Campbell (1976)
- Manheim & Garrabrant (2018)
- 母文件定理 6

---

*Moodify 题目规格书 · A6 · v1.0*
