# 题目 A10：Lyapunov-like Energy Function

**来源**: 母文件 §9 题目 A10
**产出**: V 函数实现 + 权重校准 + 闭环控制 + 停止条件

---

## 0. 题目定义

设计 Moodify Lyapunov-like Energy。用 WHS、EDS、LFR、ArtifactRisk、Uncertainty 定义一个可计算能量函数。

---

## 1. V 函数的实现

```python
def compute_energy(wavestate, diagnosis, emotion_code, gp_model=None) -> float:
    """
    V(x, g) = α*EmotionDistance + β*DefectPenalty + γ*OverprocessingRisk + δ*Uncertainty
    """
    # α, β, γ, δ = calibrated_weights(emotion_code)  # 来自校准实验

    ed = emotion_distance(wavestate, emotion_code)        # ∈ [0, 1]
    dp = defect_penalty(diagnosis)                        # ∈ [0, 3]
    op = overprocessing_risk(diagnosis)                   # ∈ [0, 1]
    un = estimate_uncertainty(wavestate, gp_model)        # ∈ [0, 1]

    # 默认权重 (校准前)
    alpha, beta, gamma, delta = 0.50, 0.25, 0.15, 0.10

    return alpha * ed + beta * (dp / 3.0) + gamma * op + delta * un


def emotion_distance(ws, emotion_code):
    target = get_ideal_process_vector(emotion_code)
    ws_array = ws.to_array() if hasattr(ws, 'to_array') else np.array([ws.E, ws.D, ws.S, ws.T, ws.H])
    return np.linalg.norm(ws_array - target) / np.sqrt(5)


def defect_penalty(diagnosis):
    defects = DefectClassifier().classify(diagnosis)
    return sum(d.severity for d in defects) / max(1, len(defects))


def overprocessing_risk(diagnosis):
    lfr = diagnosis.Emotion.E3_FatigueRisk / 120.0
    artifact = estimate_artifact_risk(diagnosis)
    return max(lfr, artifact)
```

---

## 2. 闭环控制

```python
def closed_loop_process(audio, emotion_code, max_iterations=3):
    x_current = diagnose(audio)
    trajectory = [{"step": 0, "ws": x_current, "V": compute_energy(x_current, x_current, emotion_code)}]

    for t in range(1, max_iterations + 1):
        params = recommend_params(x_current, emotion_code)
        params = project_to_safe(params, emotion_code)
        audio_out = dsp_process(audio, params)
        x_new = diagnose(audio_out)
        V_new = compute_energy(x_new, x_new, emotion_code)

        if V_new >= trajectory[-1]["V"] - 0.01:
            break  # 不再改善
        if V_new < V_threshold(emotion_code):
            trajectory.append({"step": t, "ws": x_new, "V": V_new, "converged": True})
            return audio_out, trajectory

        trajectory.append({"step": t, "ws": x_new, "V": V_new})
        x_current = x_new
        audio = audio_out

    return audio_out, trajectory
```

---

## 3. 风险限制

```python
RISK_LIMITS = {
    "GA": 0.4, "HL": 0.4, "SE": 0.5, "CN": 0.5,
    "LW": 0.3, "DR": 0.6, "UD": 0.8, "WL": 0.9,
}

def check_risk_limit(ws, emotion_code):
    risk = overprocessing_risk(ws)
    limit = RISK_LIMITS.get(emotion_code, 0.5)
    return risk <= limit, risk, limit
```

---

## 4. 产物清单

1. `energy/energy_function.py` — V 实现
2. `energy/closed_loop.py` — 闭环控制
3. `energy/weight_calibration.py` — 权重校准
4. `energy/trajectory_viz.py` — V 下降曲线可视化

---

*Moodify 题目规格书 · A10 · v1.0*
