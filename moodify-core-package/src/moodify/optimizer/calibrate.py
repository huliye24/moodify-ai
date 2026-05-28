"""局部校准 — 真实 DSP 探针 + 雅可比矩阵拟合 + 协方差估计

SPEC-004: 每首歌用 n_probes 次真实 DSP + 重诊断测量强度→Δws 的局部线性映射。
用最小二乘拟合 5×5 雅可比矩阵 J, 从残差估计协方差 Σ 及其精度矩阵。

产出:
  J: 局部线性模型 — Δws ≈ J @ (strength - 0.5)
  sigma_inv: 马氏距离精度矩阵 — 用于 SPEC-006 距离度量升级
  cv_error: 留一交叉验证误差 — 量化局部线性假设的可信度
"""

from __future__ import annotations

import os
import time
import tempfile
import numpy as np
from scipy.stats import qmc

CHAIN_ORDER = ["spectrum", "dynamic", "space", "layer", "master"]


# ── 探针选择 ──────────────────────────────────────────────

def select_probes(
    space: dict[str, tuple[float, float]],
    n_probes: int = 5,
    seed: int = 42,
) -> list[dict[str, float]]:
    """k-means 聚类中心 — 保证探针在 5D 空间中均匀分散。

    聚类中心最大化探针间距离 → 设计矩阵 X 条件数小 → J 估计稳定。
    """
    n_probes = max(n_probes, 5)

    sampler = qmc.LatinHypercube(d=5, seed=seed)
    samples = sampler.random(n=500)

    points = np.zeros((500, 5))
    for j, dim in enumerate(CHAIN_ORDER):
        lo, hi = space[dim]
        points[:, j] = lo + samples[:, j] * (hi - lo)

    from scipy.cluster.vq import kmeans2
    centroids, _ = kmeans2(points, n_probes, minit='points', seed=seed)

    probes: list[dict[str, float]] = []
    for i in range(n_probes):
        vec: dict[str, float] = {}
        for j, dim in enumerate(CHAIN_ORDER):
            vec[dim] = float(centroids[i, j])
        probes.append(vec)

    return probes


# ── 单探针 DSP ────────────────────────────────────────────

def run_probe_dsp(
    audio: np.ndarray,
    sr: int,
    strength_vector: dict[str, float],
    emotion_code: str,
) -> np.ndarray:
    """单个探针: 强度→15参数→DSP→处理后的音频。

    不做诊断（诊断在 calibrate 中统一管理）。
    """
    from moodify.optimizer.search import strength_to_params
    from moodify.processing.spectral_chain import SpectralDSPChain

    params = strength_to_params(strength_vector, emotion_code)
    chain = SpectralDSPChain()
    return chain.process(audio, sr, params)


# ── 便捷预测 ──────────────────────────────────────────────

def predict_delta(
    strength_vector: dict[str, float],
    J: np.ndarray,
) -> np.ndarray:
    """用校准后的雅可比预测 Δws = J @ (strength - 0.5)."""
    delta_s = np.array([strength_vector.get(d, 0.5) - 0.5 for d in CHAIN_ORDER])
    return J @ delta_s


# ── 主校准函数 ────────────────────────────────────────────

def calibrate(
    diagnosis,            # WaveStateDiagnosis
    audio: np.ndarray,    # (samples, channels) float32
    sr: int,
    emotion_code: str,    # "GA", "SE", ...
    n_probes: int = 5,
    cross_validate: bool = True,
) -> dict:
    """真实 DSP 探针测量 → 局部线性模型校准。

    Returns:
      J:            (5,5) 雅可比 — Δws ≈ J @ (strength - 0.5)
      sigma_inv:    (5,5) 马氏距离精度矩阵
      ws_raw:       (5,) 原始波场 5D
      target:       (5,) 目标情绪理想 5D
      cv_error:     float | None — 留一交叉验证 RMSE
      condition_number: float — 设计矩阵条件数 (<10 好, >100 差)
      probes_used:  int — 成功探针数
      elapsed_ms:   float
      warnings:     list[str]
    """
    t0 = time.perf_counter()
    warnings: list[str] = []

    from moodify.orchestration.state_transfer import StateTransferEngine
    from moodify.knowledge.emotion_targets import get_ideal_process_vector
    from moodify.diagnosis.engine import DiagnosisEngine
    from moodify.diagnosis.defect_classifier import DefectClassifier
    from moodify.optimizer.search import define_strength_space

    # 1-2. 原始状态 + 目标
    ws_raw = StateTransferEngine.diagnostic_to_process(diagnosis).to_array()
    target = get_ideal_process_vector(emotion_code)

    # 3. 搜索空间
    classifier = DefectClassifier()
    defects = classifier.classify(diagnosis, emotion_code)
    space = define_strength_space(defects, emotion_code)

    # 4. 探针
    actual_n = min(n_probes, 10)
    probes = select_probes(space, n_probes=actual_n)

    # 5. 运行探针
    engine = DiagnosisEngine()
    X_rows: list[np.ndarray] = []
    Y_rows: list[np.ndarray] = []
    valid = 0

    for probe in probes:
        try:
            processed = run_probe_dsp(audio, sr, probe, emotion_code)
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tf:
                import soundfile
                soundfile.write(tf.name, processed, sr)
                ws_diag = engine.diagnose_quick(tf.name)
                os.unlink(tf.name)

            ws_probe = StateTransferEngine.diagnostic_to_process(ws_diag).to_array()
            delta = ws_probe - ws_raw

            x_row = np.array([probe[d] - 0.5 for d in CHAIN_ORDER], dtype=np.float64)
            X_rows.append(x_row)
            Y_rows.append(delta.astype(np.float64))
            valid += 1
        except Exception as e:
            warnings.append(f"Probe {valid} failed: {e}")

    if valid < 3:
        raise RuntimeError(f"Insufficient valid probes ({valid}/{len(probes)})")

    if valid < 5:
        warnings.append(f"Only {valid}/{len(probes)} probes succeeded. J underdetermined.")

    # 6-8. 最小二乘
    X = np.array(X_rows)  # (valid, 5)
    Y = np.array(Y_rows)  # (valid, 5)

    cond = float(np.linalg.cond(X.T @ X + 1e-8 * np.eye(5)))
    if cond > 50:
        warnings.append(f"Design matrix condition number = {cond:.0f} (>50), J unstable")

    J_T = np.linalg.lstsq(X, Y, rcond=None)[0]  # (5, 5): strength → ws
    J = J_T.T  # (5, 5): J[ws_dim, strength_dim]

    # 9. 协方差 + 精度矩阵
    residuals = Y - X @ J_T
    sigma = (residuals.T @ residuals) / max(1.0, valid - 5)
    sigma += 1e-6 * np.eye(5)
    sigma_inv = np.linalg.inv(sigma)

    # 10. 交叉验证
    cv_error = None
    if cross_validate and valid >= 6:
        errors = []
        for i in range(valid):
            X_loo = np.delete(X, i, axis=0)
            Y_loo = np.delete(Y, i, axis=0)
            J_loo_T = np.linalg.lstsq(X_loo, Y_loo, rcond=None)[0]
            pred = X[i] @ J_loo_T
            errors.append(np.sum((Y[i] - pred) ** 2))
        cv_error = float(np.sqrt(np.mean(errors)))
        if cv_error > 0.08:
            warnings.append(f"CV RMSE = {cv_error:.3f} (>0.08), local linearity may not hold")

    elapsed = (time.perf_counter() - t0) * 1000

    return {
        "J": J,
        "J_labels": ["E", "D", "S", "T", "H"],
        "sigma_inv": sigma_inv,
        "ws_raw": ws_raw,
        "target": target,
        "condition_number": cond,
        "cv_error": cv_error,
        "probes_used": valid,
        "elapsed_ms": elapsed,
        "warnings": warnings,
    }
