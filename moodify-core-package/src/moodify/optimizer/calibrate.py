"""局部校准 — 真实 DSP 探针 + 岭回归雅可比 + 单探针验证

SPEC-004-REV: 三层设计
  Layer 1 (默认, 0s): 纯 T_EFFECTS — 不校准
  Layer 2 (可选, ~1.5s): 单探针验证 — 1次DSP+轻量诊断
  Layer 3 (异步, ~7.5s): 5探针岭回归校准 — 结果缓存

关键修正 vs 原版:
  - 岭回归替代最小二乘 (λ=1.0, 收缩估计防过拟合)
  - 轻量诊断替代 diagnose_quick (~0.5s vs 2-3s)
  - 无临时 WAV 文件 (内存传递)
  - condition_number 替代 cv_error 做信任门控
"""

from __future__ import annotations

import time
import numpy as np
from scipy.stats import qmc

CHAIN_ORDER = ["spectrum", "dynamic", "space", "layer", "master"]


# ── 探针选择 ──────────────────────────────────────────────

def select_probes(
    space: dict[str, tuple[float, float]],
    n_probes: int = 5,
    seed: int = 42,
) -> list[dict[str, float]]:
    """k-means 聚类中心 — 保证探针在 5D 空间中均匀分散。"""
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
    """单个探针: 强度→15参数→DSP→处理后的音频 (内存操作, 无磁盘 I/O)。"""
    from moodify.optimizer.search import strength_to_params
    from moodify.processing.spectral_chain import SpectralDSPChain

    params = strength_to_params(strength_vector, emotion_code)
    chain = SpectralDSPChain()
    return chain.process(audio, sr, params)


# ── 轻量诊断 ──────────────────────────────────────────────

def diagnose_lightweight(audio: np.ndarray, sr: int) -> np.ndarray:
    """自包含的轻量 5D WaveState 计算。不依赖外部模块的特殊方法。

    每维度取 1 个最快指标, 目标 < 0.5s:
      E: STFT 中频能量占比 (250-4000Hz / 全频段)
      D: 分段落 RMS 分位数差 (简化 LRA, 不用 pyloudnorm)
      S: 左右声道平均相关系数
      T: 帧间 RMS 跳跃比 (瞬态密度)
      H: 高频能量比 (简化疲劳风险)
    """
    import librosa

    audio_f32 = audio.astype(np.float32)
    if audio_f32.ndim == 1:
        audio_f32 = np.column_stack([audio_f32, audio_f32])

    n_fft = 2048
    hop = 512

    # E: 中频清晰度 — 中频(250-4000Hz)能量 vs 全频段
    D_left = librosa.stft(audio_f32[:, 0], n_fft=n_fft, hop_length=hop)
    mag = np.abs(D_left)
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    mid_mask = (freqs >= 250) & (freqs <= 4000)
    mid_energy = np.sum(mag[mid_mask]) / max(np.sum(mag), 1e-8)
    E = max(0.0, min(1.0, mid_energy * 2.0))  # scale to [0, 1]

    # D: 简化 LRA — 10 段 RMS 的分位数差
    seg_len = len(audio_f32) // 10
    rms_segs = np.array([
        np.sqrt(np.mean(audio_f32[i*seg_len:(i+1)*seg_len, 0] ** 2))
        for i in range(10) if seg_len > 0
    ])
    rms_db = 20 * np.log10(rms_segs + 1e-8)
    lra_simple = float(np.percentile(rms_db, 95) - np.percentile(rms_db, 5))
    D = max(0.0, min(1.0, lra_simple / 15.0))

    # S: 声道相关性
    ml, mr = audio_f32[:, 0], audio_f32[:, 1]
    corr = float(np.corrcoef(ml, mr)[0, 1]) if len(ml) > 1 else 0.0
    S = max(0.0, min(1.0, 1.0 - abs(corr)))

    # T: 瞬态密度 — 帧间 RMS 跳跃 > 3dB 的比例
    frame_len = int(sr * 0.05)  # 50ms frames
    n_frames = len(audio_f32) // max(frame_len, 1)
    frame_rms = np.array([
        np.sqrt(np.mean(audio_f32[i*frame_len:(i+1)*frame_len, 0] ** 2))
        for i in range(n_frames)
    ])
    frame_db = 20 * np.log10(frame_rms + 1e-8)
    jumps = np.sum(np.abs(np.diff(frame_db)) > 3.0)
    T = max(0.0, min(1.0, jumps / max(n_frames - 1, 1)))

    # H: 高频能量比 — 8kHz+ 能量占比 (疲劳风险代理)
    high_mask = freqs >= 8000
    hf_ratio = np.sum(mag[high_mask]) / max(np.sum(mag), 1e-8)
    H = max(0.0, min(1.0, 1.0 - hf_ratio * 10.0))

    return np.array([E, D, S, T, H], dtype=np.float64)


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
    ridge_lambda: float = 1.0,
) -> dict:
    """真实 DSP 探针测量 + 岭回归 → 局部线性模型校准。

    SPEC-004-REV 修正:
      - 岭回归替代最小二乘 (ridge_lambda 收缩 J 向零)
      - 轻量诊断替代 diagnose_quick (无临时 WAV)
      - condition_number 做信任门控 (不需要 cv_error)

    Returns:
      J:               (5,5) 岭回归雅可比 — 收缩估计, 偏向零
      sigma_inv:       (5,5) 马氏距离精度矩阵
      ws_raw:          (5,)  原始波场 5D
      target:          (5,)  目标情绪理想 5D
      condition_number: float — 设计矩阵条件数
      probes_used:     int
      elapsed_ms:      float
      warnings:        list[str]
    """
    t0 = time.perf_counter()
    warnings: list[str] = []

    from moodify.orchestration.state_transfer import StateTransferEngine
    from moodify.knowledge.emotion_targets import get_ideal_process_vector
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

    # 5. 运行探针 — 轻量诊断, 无临时 WAV
    X_rows: list[np.ndarray] = []
    Y_rows: list[np.ndarray] = []
    valid = 0

    for probe in probes:
        try:
            processed = run_probe_dsp(audio, sr, probe, emotion_code)
            ws_probe_5d = diagnose_lightweight(processed, sr)
            delta = ws_probe_5d - ws_raw

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

    # 6. 岭回归 (替代原版最小二乘)
    X = np.array(X_rows)  # (valid, 5)
    Y = np.array(Y_rows)  # (valid, 5)

    XTX = X.T @ X
    cond = float(np.linalg.cond(XTX + 1e-8 * np.eye(5)))
    if cond > 50:
        warnings.append(f"Design matrix condition number = {cond:.0f} (>50), J unstable")

    # 岭回归: J_T = (X^T X + λI)^(-1) X^T Y
    XTX_ridge = XTX + ridge_lambda * np.eye(5)
    J_T = np.linalg.solve(XTX_ridge, X.T @ Y)  # (5, 5): strength → ws
    J = J_T.T  # (5, 5): J[ws_dim, strength_dim]

    # 7. 协方差 + 精度矩阵
    residuals = Y - X @ J_T
    sigma = (residuals.T @ residuals) / max(1.0, valid - 5)
    sigma += 1e-6 * np.eye(5)
    sigma_inv = np.linalg.inv(sigma)

    elapsed = (time.perf_counter() - t0) * 1000

    return {
        "J": J,
        "J_labels": ["E", "D", "S", "T", "H"],
        "sigma_inv": sigma_inv,
        "ws_raw": ws_raw,
        "target": target,
        "condition_number": cond,
        "ridge_lambda": ridge_lambda,
        "probes_used": valid,
        "elapsed_ms": elapsed,
        "warnings": warnings,
    }


# ── Layer 2: 单探针验证 ───────────────────────────────────

def validate_te(
    diagnosis,
    audio: np.ndarray,
    sr: int,
    emotion_code: str,
    top_strength: dict[str, float],
) -> dict:
    """单探针验证 T_EFFECTS 准确性。

    用搜索 top-1 的强度向量做 1 次真实 DSP + 轻量诊断,
    对比 T_EFFECTS 预测偏差。

    Returns:
      te_reliable:    bool   — T_EFFECTS 是否可信 (偏差 < 0.08)
      deviation:      float  — 预测 vs 实际的 5D 偏差
      actual_delta:   (5,)   — 实际 Δws
      predicted_delta: (5,)  — T_EFFECTS 预测 Δws
      elapsed_ms:     float
    """
    t0 = time.perf_counter()

    from moodify.orchestration.state_transfer import StateTransferEngine

    ws_raw = StateTransferEngine.diagnostic_to_process(diagnosis).to_array()

    # T_EFFECTS 预测
    engine = StateTransferEngine()
    ws_proc = StateTransferEngine.WaveStateProcess(
        E=float(ws_raw[0]), D=float(ws_raw[1]),
        S=float(ws_raw[2]), T=float(ws_raw[3]), H=float(ws_raw[4]),
    )
    chain_strengths = [top_strength.get(d, 0.5) for d in CHAIN_ORDER]
    ws_te, _ = engine.apply_chain_transfer(ws_proc, CHAIN_ORDER, chain_strengths, emotion_code)
    predicted_delta = ws_te.to_array() - ws_raw

    # 真实 DSP + 轻量诊断
    processed = run_probe_dsp(audio, sr, top_strength, emotion_code)
    ws_actual_5d = diagnose_lightweight(processed, sr)
    actual_delta = ws_actual_5d - ws_raw

    deviation = float(np.linalg.norm(actual_delta - predicted_delta))
    te_reliable = deviation < 0.08

    return {
        "te_reliable": te_reliable,
        "deviation": deviation,
        "actual_delta": actual_delta,
        "predicted_delta": predicted_delta,
        "elapsed_ms": (time.perf_counter() - t0) * 1000,
    }
