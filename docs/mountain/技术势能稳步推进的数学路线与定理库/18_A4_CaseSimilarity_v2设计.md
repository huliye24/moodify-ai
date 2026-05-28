# 题目 A4：Case Similarity v2 设计

**来源**: 母文件 §9 题目 A4
**类型**: 后续 AI 题目规格书
**产出**: 四分量相似度公式 + 权重学习 + 负迁移检测

---

## 0. 题目定义

设计 Moodify Case Similarity v2。给出诊断相似、目标相似、风险相似、结果相似四个分量及权重学习方案。

---

## 1. 四分量公式（精确到代码）

```python
import numpy as np

def case_similarity_v2(case_new: dict, case_hist: dict, weights: tuple = (0.35, 0.25, 0.25, 0.15)) -> float:
    """
    Args:
        case_new: {diagnosis_vector, emotion_code, defect_vector, edsr_real=None}
        case_hist: {diagnosis_vector, emotion_code, defect_vector, edsr_real, satisfied}
        weights: (w_diag, w_target, w_risk, w_outcome)
    Returns:
        similarity ∈ [0, 1]
    """
    w_diag, w_target, w_risk, w_outcome = weights

    # 1. 诊断相似
    sim_diag = cos_sim(case_new["diagnosis_vector"], case_hist["diagnosis_vector"])

    # 2. 目标相似
    sim_target = target_match(case_new["emotion_code"], case_hist["emotion_code"])

    # 3. 风险相似
    sim_risk = 1.0 - l1_dist(case_new["defect_vector"], case_hist["defect_vector"]) / (3 * 17)

    # 4. 结果相似 (仅当历史有反馈)
    sim_outcome = 0.5  # default
    if case_hist.get("satisfied") is True:
        sim_outcome = 1.0
    elif case_hist.get("satisfied") is False:
        sim_outcome = 0.0
    # 权重: 若无反馈, w_outcome = 0, 重新分配

    has_feedback = case_hist.get("satisfied") is not None
    if not has_feedback:
        total = w_diag + w_target + w_risk
        w_diag /= total; w_target /= total; w_risk /= total; w_outcome = 0

    return w_diag * sim_diag + w_target * sim_target + w_risk * sim_risk + w_outcome * sim_outcome


def target_match(code_a: str, code_b: str) -> float:
    """情绪目标匹配度"""
    if code_a == code_b:
        return 1.0
    same_cat = {
        "warm":   ["GA", "HL"],
        "dark":   ["DR", "UD"],
        "spatial":["SE", "CN", "LW"],
        "intense":["WL", "UD"],
    }
    for cat, codes in same_cat.items():
        if code_a in codes and code_b in codes:
            return 0.7
    # 非冲突
    conflicting = [("GA", "WL"), ("HL", "UD"), ("SE", "WL"), ("LW", "UD")]
    if (code_a, code_b) in conflicting or (code_b, code_a) in conflicting:
        return 0.0
    return 0.3
```

---

## 2. 权重学习

### 2.1 数据需求

≥50 条带 `satisfied` 标签的历史案例。

### 2.2 学习方法

```python
from scipy.optimize import minimize

def optimize_weights(history: list[dict]) -> tuple:
    """Leave-One-Out 交叉验证优化权重"""
    def objective(w):
        w = np.abs(w); w /= w.sum()
        kendall_taus = []
        for i, case in enumerate(history):
            others = [h for j, h in enumerate(history) if j != i]
            sims = [case_similarity_v2(case, other, w) for other in others]
            # 用相似度排序 vs 真实迁移收益排序
            true_ranks = rank_by_transfer_benefit(case, others)
            pred_ranks = rank_by_similarity(sims)
            tau, _ = kendalltau(true_ranks, pred_ranks)
            kendall_taus.append(tau)
        return -np.mean(kendall_taus)  # minimize negative τ

    result = minimize(objective, [0.35, 0.25, 0.25, 0.15],
                      bounds=[(0.1, 0.5)] * 4, method='L-BFGS-B')
    w = np.abs(result.x); w /= w.sum()
    return tuple(w)
```

---

## 3. 负迁移检测

### 3.1 检测信号

```python
def detect_negative_transfer(case_new, retrieved_cases, actual_eds):
    """
    如果 RAG 推荐的参数导致 EDS < 搜索的 EDS → RAG 负迁移
    """
    eds_search_baseline = get_search_baseline_eds(case_new)  # 搜索-only 的预期 EDS
    if actual_eds < eds_search_baseline - 5:
        return {
            "negative_transfer": True,
            "eds_gap": actual_eds - eds_search_baseline,
            "retrieved_cases": retrieved_cases,
            "suspected_reason": analyze_mismatch(case_new, retrieved_cases),
        }
    return {"negative_transfer": False}
```

---

## 4. 产物清单

1. `similarity/case_similarity_v2.py` — 四分量实现
2. `similarity/weight_optimization.py` — 权重学习
3. `similarity/negative_transfer_detector.py` — 负迁移检测
4. `similarity/calibration_report.md` — 校准报告

---

## 5. 理论参考

- Lewis et al. (2020), Pan & Yang (2010)
- Rendle et al. (2009): BPR
- 母文件 P0-3, 定理 4

---

*Moodify 题目规格书 · A4 · v1.0*
