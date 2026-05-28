# 题目 A8：Bayesian 实验规划器

**来源**: 母文件 §9 题目 A8
**类型**: 后续 AI 题目规格书
**产出**: GP 代理模型 + EI/UCB/PI 采集函数 + 实验排序

---

## 0. 题目定义

设计 Moodify Bayesian Experiment Planner。输入历史案例，输出下一批最值得测试的歌曲、情绪目标和参数候选。

---

## 1. GP 代理模型

```python
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel

kernel = ConstantKernel(1.0) * RBF(length_scale=[1.0] * 5) + WhiteKernel(noise_level=0.01)
gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10, alpha=0.01)

# 输入: 5D strength vectors
# 输出: EDSR_proxy (或 composite score)
X_train = np.array([list(h.strength_vector.values()) for h in history])
y_train = np.array([h.composite_score for h in history])
gp.fit(X_train, y_train)
```

---

## 2. 采集函数

```python
from scipy.stats import norm

def expected_improvement(X_candidate, gp_model, y_best):
    mu, sigma = gp_model.predict(X_candidate, return_std=True)
    with np.errstate(divide='ignore'):
        Z = (mu - y_best) / sigma
        ei = (mu - y_best) * norm.cdf(Z) + sigma * norm.pdf(Z)
        ei[sigma == 0.0] = 0.0
    return ei

def upper_confidence_bound(X_candidate, gp_model, kappa=2.0):
    mu, sigma = gp_model.predict(X_candidate, return_std=True)
    return mu + kappa * sigma

def probability_of_improvement(X_candidate, gp_model, y_best, xi=0.01):
    mu, sigma = gp_model.predict(X_candidate, return_std=True)
    with np.errstate(divide='ignore'):
        Z = (mu - y_best - xi) / sigma
        pi = norm.cdf(Z)
        pi[sigma == 0.0] = 0.0
    return pi
```

---

## 3. 规划器主循环

```python
def plan_experiments(history, budget=10):
    X_train = prepare_training_data(history)
    y_train = prepare_labels(history)
    gp.fit(X_train, y_train)

    # 在 5D 空间中生成候选 (LHS 或网格)
    sampler = qmc.LatinHypercube(d=5)
    candidates = sampler.random(n=5000)
    candidates = unscale_to_strength_space(candidates)

    y_best = max(y_train)
    ei_scores = expected_improvement(candidates, gp, y_best)
    top_indices = np.argsort(ei_scores)[-budget:][::-1]

    return [{"strength_vector": candidates[i], "ei": ei_scores[i]} for i in top_indices]
```

---

## 4. 约束嵌入

将安全多面体 (A5) 的约束嵌入规划器:

```python
candidates_filtered = [u for u in candidates if is_in_safe_polytope(u, emotion_code)]
```

---

## 5. 产物清单

1. `experiment_planner/gp_model.py`
2. `experiment_planner/acquisition.py` — EI/UCB/PI
3. `experiment_planner/planner.py` — 主循环
4. `experiment_planner/compare_lhs.py` — LHS vs Bayesian 对比

---

## 6. 理论参考

- Jones, Schonlau, Welch (1998): EGO
- Rasmussen & Williams (2006): GP
- Snoek et al. (2012): Practical BO
- 母文件定理 8

---

*Moodify 题目规格书 · A8 · v1.0*
