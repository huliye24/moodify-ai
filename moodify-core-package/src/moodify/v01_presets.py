"""v01_presets.py -- Three v0.1.0 processing presets.

Each preset maps to a pedalboard DSP parameter dict consumed by MoodifyDSPChain.
"""

# ── Warm Vocal ──────────────────────────────────────────
# Gentle vocal enhancement: warmth + presence + light compression

WARM_VOCAL_PARAMS: dict[str, float] = {
    "P01_vocal_presence_freq":     3000.0,
    "P02_vocal_presence_gain":     2.5,
    "P03_vocal_presence_q":        0.7,
    "P04_proximity_low_freq":      200.0,
    "P05_proximity_low_gain":      2.5,
    "P06_compression_ratio":       1.45,
    "P07_compression_attack":      25.0,
    "P08_compression_release":     220.0,
    "P09_compression_threshold":   -16.0,
    "P10_reverb_t60":              1.2,
    "P11_reverb_dry_wet":          0.20,
    "P12_reverb_width":            0.8,
    "P13_harmonic_drive":          0.08,
    "P14_high_shelf_freq":         10000.0,
    "P15_high_shelf_gain":         1.5,
}

# ── Clean Master ────────────────────────────────────────
# Transparent mastering: gentle compression + subtle air

CLEAN_MASTER_PARAMS: dict[str, float] = {
    "P01_vocal_presence_freq":     3000.0,
    "P02_vocal_presence_gain":     0.0,
    "P03_vocal_presence_q":        0.5,
    "P04_proximity_low_freq":      200.0,
    "P05_proximity_low_gain":      0.0,
    "P06_compression_ratio":       1.20,
    "P07_compression_attack":      35.0,
    "P08_compression_release":     250.0,
    "P09_compression_threshold":   -12.0,
    "P10_reverb_t60":              0.0,
    "P11_reverb_dry_wet":          0.0,
    "P12_reverb_width":            1.0,
    "P13_harmonic_drive":          0.0,
    "P14_high_shelf_freq":         12000.0,
    "P15_high_shelf_gain":         1.0,
}

# ── Wide Space ──────────────────────────────────────────
# Spatial enhancement: wide reverb + stereo width

WIDE_SPACE_PARAMS: dict[str, float] = {
    "P01_vocal_presence_freq":     3000.0,
    "P02_vocal_presence_gain":     1.0,
    "P03_vocal_presence_q":        0.5,
    "P04_proximity_low_freq":      150.0,
    "P05_proximity_low_gain":      0.0,
    "P06_compression_ratio":       1.25,
    "P07_compression_attack":      35.0,
    "P08_compression_release":     320.0,
    "P09_compression_threshold":   -14.0,
    "P10_reverb_t60":              2.5,
    "P11_reverb_dry_wet":          0.28,
    "P12_reverb_width":            1.0,
    "P13_harmonic_drive":          0.05,
    "P14_high_shelf_freq":         12000.0,
    "P15_high_shelf_gain":         1.5,
}

PRESETS = {
    "warm_vocal": {
        "name": "Warm Vocal",
        "name_zh": "温暖人声",
        "description": "增强人声温度、厚度和亲密感",
        "params": WARM_VOCAL_PARAMS,
    },
    "clean_master": {
        "name": "Clean Master",
        "name_zh": "干净母带",
        "description": "透明母带处理，清理频谱，增强稳定性",
        "params": CLEAN_MASTER_PARAMS,
    },
    "wide_space": {
        "name": "Wide Space",
        "name_zh": "宽阔空间",
        "description": "增强空间感和听觉宽度",
        "params": WIDE_SPACE_PARAMS,
    },
}


def get_preset(key: str) -> dict | None:
    """Return preset dict or None if unknown key."""
    return PRESETS.get(key)


def list_presets() -> list[str]:
    """Return available preset keys."""
    return list(PRESETS.keys())
