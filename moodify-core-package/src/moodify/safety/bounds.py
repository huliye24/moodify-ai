"""参数安全边界定义 — 数据文件, 不包含算法 (SPEC-008 §2).

Provenance (SPEC-011 T9.1 / MATH-008 四层规格体系):
  P01-P05 (人声/低频 EQ):  AES 推荐均衡器操作范围 + pedalboard 默认值
  P06-P09 (压缩器):         ITU-R BS.1770 / EBU 3342 动态处理器典型值
  P10-P12 (混响):           混响感知阈值 (Zwicker & Fastl 1999)
  P13 (谐波驱动):           安全上限 (经验值, 待实验验证)
  P14-P15 (高频 EQ):        ITU-R BS.1770 听力保护建议范围
"""

# ── 硬边界 (每个参数的物理/声学安全范围) ──
HARD_BOUNDS = {
    "P01_vocal_presence_freq":  (1500, 6000),
    "P02_vocal_presence_gain":  (-6, 10),
    "P03_vocal_presence_q":     (0.3, 2.0),
    "P04_proximity_low_freq":   (80, 600),
    "P05_proximity_low_gain":   (-8, 8),
    "P06_compression_ratio":    (1.0, 20.0),
    "P07_compression_attack":   (2, 80),
    "P08_compression_release":  (20, 800),
    "P09_compression_threshold": (-40, -5),
    "P10_reverb_t60":           (0.1, 5.0),
    "P11_reverb_dry_wet":       (0.0, 0.8),
    "P12_reverb_width":         (0.0, 2.5),
    "P13_harmonic_drive":       (0.0, 0.8),
    "P14_high_shelf_freq":      (4000, 18000),
    "P15_high_shelf_gain":      (-6, 10),
}

# ── 组合禁区 ──
# 每条: (condition_lambda, violation_message, correction_fn)
# condition 仅在相关参数均存在于 params 时触发
# correction_fn 接收 params dict, 在其上原位修改
COMBO_RULES = [
    (
        lambda p: ("P02_vocal_presence_gain" in p and "P15_high_shelf_gain" in p
                   and p["P02_vocal_presence_gain"] + p["P15_high_shelf_gain"] > 8),
        "中频+高频增益和 > 8dB, 可能导致刺耳",
        lambda p: _distribute_excess(p, "P02_vocal_presence_gain",
                                     "P15_high_shelf_gain", 8),
    ),
    (
        lambda p: ("P05_proximity_low_gain" in p and "P11_reverb_dry_wet" in p
                   and p["P05_proximity_low_gain"] > 5
                   and p["P11_reverb_dry_wet"] > 0.4),
        "低频增益 > 5dB 时混响干湿比不应 > 0.4, 避免浑浊",
        lambda p: _clamp_param(p, "P11_reverb_dry_wet", hi=0.4),
    ),
    (
        lambda p: ("P06_compression_ratio" in p and "P13_harmonic_drive" in p
                   and p["P06_compression_ratio"] > 6
                   and p["P13_harmonic_drive"] > 0.3),
        "压缩比 > 6:1 时谐波驱动不应 > 0.3, 避免听觉疲劳",
        lambda p: _clamp_param(p, "P13_harmonic_drive", hi=0.3),
    ),
    (
        lambda p: ("P02_vocal_presence_gain" in p and "P15_high_shelf_gain" in p
                   and p["P02_vocal_presence_gain"] < -3
                   and p["P15_high_shelf_gain"] < -3),
        "中频和高频不应同时大幅衰减, 会导致声音闷暗",
        lambda p: (
            _clamp_param(p, "P02_vocal_presence_gain", lo=-3),
            _clamp_param(p, "P15_high_shelf_gain", lo=-3),
        ),
    ),
    (
        lambda p: ("P09_compression_threshold" in p and "P06_compression_ratio" in p
                   and p["P09_compression_threshold"] < -30
                   and p["P06_compression_ratio"] > 4),
        "阈值 < -30dB 时压缩比不应 > 4:1, 避免泵浦效应",
        lambda p: _clamp_param(p, "P06_compression_ratio", hi=4),
    ),
]


def _distribute_excess(p: dict, key_a: str, key_b: str, cap: float) -> None:
    """按比例削减两个参数的超出部分."""
    a = p.get(key_a, 0)
    b = p.get(key_b, 0)
    excess = a + b - cap
    if excess <= 0:
        return
    p[key_a] = a - excess / 2
    p[key_b] = b - excess / 2


def _clamp_param(p: dict, key: str, lo: float | None = None,
                 hi: float | None = None) -> None:
    """Clamp 单个参数, 只修改如果超界."""
    if key not in p:
        return
    if lo is not None and p[key] < lo:
        p[key] = lo
    if hi is not None and p[key] > hi:
        p[key] = hi


# ── 情绪特例 (放宽边界, 替代 HARD_BOUNDS 中对应维度) ──
EMOTION_EXCEPTIONS = {
    "WL": {"P13_harmonic_drive": (0.0, 1.0), "P06_compression_ratio": (1.0, 30.0)},
    "UD": {"P06_compression_ratio": (1.0, 30.0)},
    "SE": {"P11_reverb_dry_wet": (0.0, 1.0)},
}
