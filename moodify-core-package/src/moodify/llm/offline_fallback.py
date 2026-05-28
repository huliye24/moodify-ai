"""离线降级: API 不可用时加权平均聚合相似案例参数"""
from moodify.knowledge.craft_chains import get_recommended_params

PARAM_KEYS_15 = [
    "P01_vocal_presence_freq", "P02_vocal_presence_gain", "P03_vocal_presence_q",
    "P04_proximity_low_freq", "P05_proximity_low_gain",
    "P06_compression_ratio", "P07_compression_attack", "P08_compression_release", "P09_compression_threshold",
    "P10_reverb_t60", "P11_reverb_dry_wet", "P12_reverb_width",
    "P13_harmonic_drive",
    "P14_high_shelf_freq", "P15_high_shelf_gain",
]

STRENGTH_KEYS = ["spectrum", "dynamic", "space", "layer", "master"]


def aggregate_params_offline(
    similar_cases: list[tuple],
    emotion_code: str,
) -> tuple[dict[str, float], dict[str, float]]:
    """加权平均聚合。排除用户不满意的案例。

    Returns:
        (params_dict, strength_vector) — 15 参数 + 5D 强度
    """
    if not similar_cases:
        rec = get_recommended_params(emotion_code)
        return rec, {k: 0.5 for k in STRENGTH_KEYS}

    valid = [(rec, sim) for rec, sim in similar_cases if rec.satisfied is None or rec.satisfied]
    if not valid:
        rec = get_recommended_params(emotion_code)
        return rec, {k: 0.5 for k in STRENGTH_KEYS}

    total_weight = sum(sim for _, sim in valid)

    params = {}
    for key in PARAM_KEYS_15:
        wsum = sum(rec.params.get(key, 0.0) * sim for rec, sim in valid)
        params[key] = wsum / total_weight

    strength = {}
    for key in STRENGTH_KEYS:
        wsum = sum(rec.strength_vector.get(key, 0.5) * sim for rec, sim in valid)
        strength[key] = wsum / total_weight

    return params, strength
