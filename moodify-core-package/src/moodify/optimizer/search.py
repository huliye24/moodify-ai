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


# ── 2.1.4 proxy_evaluate ─────────────────────────────────

def proxy_evaluate(
    strength_vector: dict[str, float],
    diagnosis,
    emotion_code: str,
    craft_card=None,
    vector_bias: dict | None = None,
) -> float:
    """不跑真实 DSP，预估强度向量对应的 EDS 改善."""
    from moodify.orchestration.state_transfer import StateTransferEngine
    from moodify.knowledge.emotion_targets import get_ideal_process_vector

    engine = StateTransferEngine()
    ws_raw = StateTransferEngine.diagnostic_to_process(diagnosis)

    chain_strengths = [strength_vector.get(t, 0.5) for t in CHAIN_ORDER]
    ws_proxy, meta = engine.apply_chain_transfer(
        ws_raw, CHAIN_ORDER, chain_strengths, emotion_code,
    )

    target = get_ideal_process_vector(emotion_code).copy()
    if vector_bias:
        for i, dim in enumerate(["E", "D", "S", "T", "H"]):
            target[i] += vector_bias.get(dim, 0.0)
        target = np.clip(target, 0.0, 1.0)
    dist_before = float(np.linalg.norm(ws_raw.to_array() - target))
    dist_after = float(np.linalg.norm(ws_proxy.to_array() - target))

    if dist_before > 1e-8:
        eds = 100.0 * (1.0 - dist_after / dist_before)
    else:
        eds = 100.0

    warnings = meta.get("warnings", [])
    eds -= 5.0 * len(warnings)

    # craft 正则项
    if craft_card is not None:
        try:
            from moodify.knowledge.craft_chain_match import CraftChainMatch
            matcher = CraftChainMatch()
            ws_compat = matcher._wave_state_compatibility(
                craft_card, ws_proxy.to_dict(), emotion_code
            )
            craft_penalty = (1.0 - ws_compat) * 15.0
            eds -= craft_penalty
        except Exception:
            pass

    return float(np.clip(eds, -100.0, 100.0))


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
) -> list[tuple[dict[str, float], dict[str, float], float]]:
    """5D 强度空间搜索主入口."""
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

    # 获取 craft_card 用于正则化
    craft_card = None
    try:
        from moodify.knowledge.craft_chain_match import generate_craft_cards_from_data, CraftChainMatch
        cards = generate_craft_cards_from_data()
        matcher = CraftChainMatch()
        matches = matcher.match(defects, emotion_code, diagnosis, cards, top_k=1)
        craft_card = matches[0].craft_card if matches else None
    except Exception:
        pass

    # 代理评估
    scored: list[tuple[dict[str, float], float]] = []
    for vec in vectors:
        score = proxy_evaluate(vec, diagnosis, emotion_code, craft_card, vector_bias=vector_bias)
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
