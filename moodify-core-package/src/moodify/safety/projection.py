"""四级投影: 硬边界 → 组合禁区 → 情绪特例 → 风险降级 (SPEC-008 §3).

用法:
    from moodify.safety import project
    safe_params, log = project(raw_params, emotion_code)
"""

from moodify.safety.bounds import HARD_BOUNDS, COMBO_RULES, EMOTION_EXCEPTIONS


def project(params: dict[str, float], emotion_code: str) -> tuple[dict, list[str]]:
    """四级安全投影。返回 (safe_params, projection_log).

    顺序:
      Level 1: 硬边界 clip — 每个参数 clamp 到 HARD_BOUNDS
               (情绪特例维度跳过, 由 Level 3 处理)
      Level 2: 组合禁区修正 — 违反规则时执行 correction_fn
      Level 3: 情绪特例释放 — 对放宽维度, 用原始值 + 放宽边界覆盖 L1/L2
      Level 4: 风险降级 — 如果前三层后仍有问题, 整体缩放强度
    """
    log: list[str] = []
    p = dict(params)
    original = dict(params)
    exceptions = EMOTION_EXCEPTIONS.get(emotion_code, {})

    # ── Level 1: 硬边界 clip ──
    for key, (lo, hi) in HARD_BOUNDS.items():
        if key not in p:
            continue
        if key in exceptions:
            continue  # 由 L3 用更宽的边界处理
        old = p[key]
        p[key] = max(lo, min(hi, old))
        if p[key] != old:
            log.append(f"L1: {key} {old:.1f} → {p[key]:.1f} (clamped to [{lo}, {hi}])")

    # ── Level 2: 组合禁区修正 ──
    for condition, msg, correction in COMBO_RULES:
        if condition(p):
            correction(p)
            log.append(f"L2: combo rule triggered — {msg}")

    # ── Level 3: 情绪特例释放 ──
    # 用原始值 + 放宽边界, 覆盖 L1 的跳过和 L2 的可能修正
    for key, (lo, hi) in exceptions.items():
        if key not in original:
            continue
        old = p[key]
        p[key] = max(lo, min(hi, original[key]))
        if p[key] != old:
            log.append(f"L3: {key} {old:.2f} → {p[key]:.2f} (emotion exception [{lo}, {hi}])")

    # ── Level 4: 风险降级 ──
    l1_l2_count = sum(1 for entry in log if entry.startswith("L1") or entry.startswith("L2"))
    if l1_l2_count > 3:
        scale = 0.8
        rec = _get_rec_params(emotion_code)
        for key in list(p.keys()):
            if isinstance(p[key], (int, float)) and key in rec:
                diff = p[key] - rec[key]
                p[key] = rec[key] + diff * scale
        log.append(f"L4: >3 params modified ({l1_l2_count}), scaled corrections by 0.8")

    return p, log


def _get_rec_params(emotion_code: str) -> dict[str, float]:
    """获取参数的工艺卡推荐值."""
    try:
        from moodify.knowledge.craft_chains import get_recommended_params
        return get_recommended_params(emotion_code)
    except Exception:
        return {}
