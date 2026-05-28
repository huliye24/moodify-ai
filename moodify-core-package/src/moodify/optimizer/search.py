"""5D 强度空间搜索 — LHS 采样 + 代理评估 + 强度↔参数映射"""

from __future__ import annotations

import time
import numpy as np
from scipy.stats import qmc

# ── 常量 ─────────────────────────────────────────────────

STRENGTH_TO_PARAMS: dict[str, list[str]] = {
    "spectrum": [
        "P01_vocal_presence_freq", "P02_vocal_presence_gain", "P03_vocal_presence_q",
        "P04_proximity_low_freq", "P05_proximity_low_gain",
        "P14_high_shelf_freq", "P15_high_shelf_gain",
    ],
    "dynamic": [
        "P06_compression_ratio", "P07_compression_attack",
        "P08_compression_release", "P09_compression_threshold",
    ],
    "space": [
        "P10_reverb_t60", "P11_reverb_dry_wet", "P12_reverb_width",
    ],
    "layer": [
        "P13_harmonic_drive",
    ],
    "master": [],
}

CHAIN_ORDER = ["spectrum", "dynamic", "space", "layer", "master"]

DEFAULT_RANGE = (0.3, 0.7)

PARAM_INT_KEYS = {"P01_vocal_presence_freq", "P04_proximity_low_freq", "P14_high_shelf_freq"}


# ── 2.1.2 define_strength_space ──────────────────────────

def define_strength_space(
    defects: list,
    emotion_code: str,
) -> dict[str, tuple[float, float]]:
    """基于缺陷类型确定 5 个维度的搜索范围."""
    from moodify.knowledge.craft_chains import get_chain_params

    chain = get_chain_params(emotion_code)
    risk_text = " ".join(chain.get("risk_warnings", []))

    defect_params = set()
    for d in defects:
        defect_params.add(getattr(d, "parameter", ""))

    space: dict[str, tuple[float, float]] = {}
    for dim in CHAIN_ORDER:
        params_in_dim = set(STRENGTH_TO_PARAMS.get(dim, []))
        if defect_params & params_in_dim:
            space[dim] = (0.15, 0.85)
        else:
            lo, hi = DEFAULT_RANGE
            lo = max(0.1, lo)
            hi = min(0.9, hi)
            space[dim] = (lo, hi)

    # 特殊约束
    if "混响" in risk_text and "space" in space:
        lo, hi = space["space"]
        space["space"] = (lo, min(hi, 0.7))
    if "压缩" in risk_text and "dynamic" in space:
        lo, hi = space["dynamic"]
        space["dynamic"] = (lo, min(hi, 0.7))
    if "高频" in risk_text and "spectrum" in space:
        lo, hi = space["spectrum"]
        space["spectrum"] = (lo, min(hi, 0.7))

    # master 固定
    space["master"] = (0.45, 0.55)

    return space


# ── 2.1.3 sample_strength_vectors ────────────────────────

def sample_strength_vectors(
    space: dict[str, tuple[float, float]],
    n: int = 2000,
    seed: int = 42,
) -> list[dict[str, float]]:
    """Latin Hypercube Sampling 在 5D 空间产生 n 个均匀分布的强度向量."""
    sampler = qmc.LatinHypercube(d=5, seed=seed)
    samples = sampler.random(n=n)

    vectors: list[dict[str, float]] = []
    for i in range(n):
        vec: dict[str, float] = {}
        for j, dim in enumerate(CHAIN_ORDER):
            lo, hi = space[dim]
            vec[dim] = float(lo + samples[i, j] * (hi - lo))
        vectors.append(vec)
    return vectors


# ── 马氏距离 (SPEC-006-REV: 静态 Σ, 从 T_EFFECTS 推导) ──

def _mahalanobis_distance(
    x: np.ndarray,        # (5,) 或 (n, 5)
    y: np.ndarray,        # (5,)
    sigma_inv: np.ndarray,  # (5, 5)
) -> float | np.ndarray:
    """d = sqrt((x-y)^T @ sigma_inv @ (x-y)).
    负值回退到欧氏距离。"""
    diff = x - y
    if diff.ndim == 1:
        val = diff @ sigma_inv @ diff
        if val < 0:
            return float(np.linalg.norm(diff))
        return float(np.sqrt(val))
    else:
        val = np.sum(diff @ sigma_inv * diff, axis=1)
        neg = val < 0
        if np.any(neg):
            result = np.sqrt(np.maximum(0, val))
            result[neg] = np.linalg.norm(diff[neg], axis=1)
            return result
        return np.sqrt(val)


def derive_static_sigma_inv() -> np.ndarray:
    """从 T_EFFECTS 一次性推导 5D 波场协方差的精度矩阵。
    不涉及任何音频处理 — 纯数学推导。"""
    from moodify.orchestration.state_transfer import StateTransferEngine

    T_EFFECTS = StateTransferEngine.T_EFFECTS
    chain_order = ["spectrum", "dynamic", "space", "layer", "master"]
    dims = ["E", "D", "S", "T", "H"]

    rng = np.random.RandomState(42)
    n_samples = 10000
    strengths = rng.dirichlet(np.ones(5), size=n_samples)

    deltas = np.zeros((n_samples, 5))
    for i in range(n_samples):
        delta = np.zeros(5)
        for j, (t_type, strength) in enumerate(zip(chain_order, strengths[i])):
            effects = T_EFFECTS[t_type]
            for k, dim in enumerate(dims):
                p = effects[dim]
                if strength <= 0.5:
                    t = strength / 0.5
                    delta[k] += p[0] + t * (p[2] - p[0])
                else:
                    t = (strength - 0.5) / 0.5
                    delta[k] += p[2] + t * (p[4] - p[2])
        deltas[i] = delta

    sigma = np.cov(deltas.T)
    sigma += 1e-4 * np.eye(5)
    return np.linalg.inv(sigma)


_STATIC_SIGMA_INV: np.ndarray | None = None


def get_static_sigma_inv() -> np.ndarray:
    """模块级缓存 — 首次调用时计算, 后续直接返回。"""
    global _STATIC_SIGMA_INV
    if _STATIC_SIGMA_INV is None:
        _STATIC_SIGMA_INV = derive_static_sigma_inv()
    return _STATIC_SIGMA_INV


# ── 2.1.4 proxy_evaluate ─────────────────────────────────

def proxy_evaluate(
    strength_vector: dict[str, float],
    ws_raw: np.ndarray,              # (5,) — 原始波场 5D 向量
    target: np.ndarray,              # (5,) — 目标情绪理想 5D 向量
    dist_before: float,              # ||ws_raw - target||
    emotion_code: str = "GA",
    J: np.ndarray | None = None,     # (5,5) — 岭回归雅可比
    condition_number: float | None = None,
) -> float:
    """T_EFFECTS 为基础, 岭回归 J 为校正。

    公式: Δws = Δws_TE + α × J @ (s - 0.5)
    α 由 condition_number 决定。

    信任门控:
      cond < 20  → α = 0.8 (大幅校正)
      cond < 50  → α = 0.5 (适度校正)
      cond < 100 → α = 0.2 (保守校正)
      cond ≥ 100 → α = 0.0 (纯 T_EFFECTS)
    """
    # 始终计算 T_EFFECTS 基准
    eds_te = _proxy_te_base(strength_vector, ws_raw, target, dist_before, emotion_code)

    if J is None or condition_number is None:
        return eds_te

    if condition_number < 20:
        alpha = 0.8
    elif condition_number < 50:
        alpha = 0.5
    elif condition_number < 100:
        alpha = 0.2
    else:
        return eds_te

    # 岭回归校正 (马氏距离)
    ws_te = _get_te_wave_state(strength_vector, ws_raw, emotion_code)
    sv_arr = np.array([strength_vector.get(d, 0.5) for d in CHAIN_ORDER])
    delta_correction = alpha * (J @ (sv_arr - 0.5))
    ws_corrected = ws_te + delta_correction
    sigma_inv = get_static_sigma_inv()
    dist_corrected = float(_mahalanobis_distance(ws_corrected, target, sigma_inv))
    eds_corrected = 100.0 * (1.0 - dist_corrected / max(dist_before, 1e-8))

    return float(np.clip(eds_corrected, -100.0, 100.0))


def _get_te_wave_state(
    strength_vector: dict[str, float],
    ws_raw: np.ndarray,
    emotion_code: str,
) -> np.ndarray:
    """T_EFFECTS 状态转移后的 5D 向量 (不计算评分, 只返回向量)。"""
    from moodify.orchestration.state_transfer import StateTransferEngine, WaveStateProcess

    ws_proc = WaveStateProcess(
        E=float(ws_raw[0]), D=float(ws_raw[1]),
        S=float(ws_raw[2]), T=float(ws_raw[3]), H=float(ws_raw[4]),
    )
    engine = StateTransferEngine()
    chain_strengths = [strength_vector.get(t, 0.5) for t in CHAIN_ORDER]
    ws_out, _ = engine.apply_chain_transfer(ws_proc, CHAIN_ORDER, chain_strengths, emotion_code)
    return ws_out.to_array()


def _proxy_te_base(
    strength_vector: dict[str, float],
    ws_raw: np.ndarray,
    target: np.ndarray,
    dist_before: float,
    emotion_code: str,
) -> float:
    """纯 T_EFFECTS 评分 (马氏距离, 无 J 校正, 无惩罚项)。"""
    ws_te = _get_te_wave_state(strength_vector, ws_raw, emotion_code)
    sigma_inv = get_static_sigma_inv()
    dist_after = float(_mahalanobis_distance(ws_te, target, sigma_inv))
    eds = 100.0 * (1.0 - dist_after / max(dist_before, 1e-8))
    eds = float(np.clip(eds, -100.0, 100.0))
    # 在线校准修正
    try:
        from moodify.calibration.online import correct_proxy_score
        eds = correct_proxy_score(eds, emotion_code)
    except Exception:
        pass
    return eds


# ── 2.1.5 strength_to_params ─────────────────────────────

def strength_to_params(
    strength_vector: dict[str, float],
    emotion_code: str,
) -> dict[str, float]:
    """5D 强度向量 → 15 DSP 参数."""
    from moodify.knowledge.craft_chains import CRAFT_CHAINS_15PARAMS

    chain = CRAFT_CHAINS_15PARAMS.get(emotion_code)
    if chain is None:
        raise KeyError(f"Unknown emotion code: {emotion_code}")

    params: dict[str, float] = {}
    for dim in CHAIN_ORDER:
        strength = strength_vector.get(dim, 0.5)
        for pname in STRENGTH_TO_PARAMS.get(dim, []):
            spec = chain.get(pname)
            if spec is None:
                continue
            mn = float(spec["min"])
            rec = float(spec["rec"])
            mx = float(spec["max"])

            if strength <= 0.5:
                t = 1.0 - strength / 0.5
                value = rec + t * (mn - rec)
            else:
                t = (strength - 0.5) / 0.5
                value = rec + t * (mx - rec)

            value = max(mn, min(mx, value))
            if pname in PARAM_INT_KEYS:
                value = round(value)
            params[pname] = value

    return params


# ── 2.1.6 search_optimal_strengths ───────────────────────

def search_optimal_strengths(
    diagnosis,
    emotion_target: str,
    top_k: int = 3,
    n_samples: int = 2000,
    defects: list | None = None,
    vector_bias: dict | None = None,
    audio: np.ndarray | None = None,
    sr: int = 44100,
    n_probes_cal: int = 0,  # 0=不校准, 3=快速验证, 5=完整岭回归
) -> list[tuple[dict[str, float], dict[str, float], float]]:
    """5D 强度空间搜索主入口. 可选探针校准增强代理评估."""
    t0 = time.perf_counter()

    from moodify.knowledge.emotion_targets import resolve_emotion, KEY_TO_CODE
    from moodify.diagnosis.defect_classifier import DefectClassifier

    # 解析情绪代码
    try:
        emotion_key = resolve_emotion(emotion_target)
        emotion_code = KEY_TO_CODE.get(emotion_key, "GA")
    except Exception:
        emotion_code = "GA"

    # 缺陷分类（调用方已提供则跳过）
    if defects is None:
        classifier = DefectClassifier()
        defects = classifier.classify(diagnosis, emotion_code)

    # 搜索空间
    space = define_strength_space(defects, emotion_code)

    # LHS 采样
    vectors = sample_strength_vectors(space, n=n_samples)

    # ── 校准 (SPEC-004-REV / SPEC-005-REV) ──
    J = None
    cond_num = None
    ws_raw_arr = None
    target_arr = None
    dist_before = None

    if audio is not None and n_probes_cal > 0:
        try:
            from moodify.optimizer.calibrate import calibrate
            cal = calibrate(diagnosis, audio, sr, emotion_code, n_probes=n_probes_cal, ridge_lambda=1.0)
            J = cal["J"]
            cond_num = cal["condition_number"]
            ws_raw_arr = cal["ws_raw"]
            target_arr = cal["target"]
            dist_before = float(_mahalanobis_distance(ws_raw_arr, target_arr, get_static_sigma_inv()))
        except Exception:
            pass

    # T_EFFECTS 回退路径
    if ws_raw_arr is None:
        from moodify.orchestration.state_transfer import StateTransferEngine
        from moodify.knowledge.emotion_targets import get_ideal_process_vector
        ws_proc = StateTransferEngine.diagnostic_to_process(diagnosis)
        ws_raw_arr = ws_proc.to_array()
        if vector_bias:
            target_arr = get_ideal_process_vector(emotion_code).copy()
            for i, dim in enumerate(["E", "D", "S", "T", "H"]):
                target_arr[i] += vector_bias.get(dim, 0.0)
            target_arr = np.clip(target_arr, 0.0, 1.0)
        else:
            target_arr = get_ideal_process_vector(emotion_code)
        dist_before = float(_mahalanobis_distance(ws_raw_arr, target_arr, get_static_sigma_inv()))

    # 代理评估 — 使用新的 proxy_evaluate (T_EFFECTS + J校正)
    scored: list[tuple[dict[str, float], float]] = []
    for vec in vectors:
        score = proxy_evaluate(
            vec, ws_raw_arr, target_arr, dist_before,
            emotion_code=emotion_code,
            J=J, condition_number=cond_num,
        )
        scored.append((vec, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    # 构建结果
    result: list[tuple[dict[str, float], dict[str, float], float]] = []
    for vec, score in scored[:top_k]:
        params = strength_to_params(vec, emotion_code)
        result.append((vec, params, score))

    elapsed = (time.perf_counter() - t0) * 1000
    if elapsed > 3000:
        import warnings
        warnings.warn(f"search_optimal_strengths took {elapsed:.0f}ms (target < 3000ms)")

    return result
