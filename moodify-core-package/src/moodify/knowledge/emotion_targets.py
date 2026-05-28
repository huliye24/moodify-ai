"""
emotion_targets.py — 完整 8 情绪目标向量与约束矩阵
=====================================================
Spec references: §3.2-§3.4, §13.2-§13.9, §14.3

每个情绪包含:
  - 目标向量 (T_e for quality.py Q function)
  - 频谱约束矩阵 (§3.2)
  - 动态约束矩阵 (§3.3)
  - 空间约束矩阵 (§3.4)
  - 情绪安全区间 (§14.3)
  - 预期状态转移 (§13)
  - 混响风格推荐
  - 适用音源

情绪代码: GA/SE/UD/LW/HL/DR/WL/CN
"""

import numpy as np

# ============================================================
#  完整 8 情绪目标向量
# ============================================================

EMOTION_TARGETS_V2 = {
    # ================================================================
    #  GA · 温柔觉醒 (Gentle Awakening) — §3.2-3.4, §13.2
    # ================================================================
    "gentle_awakening": {
        "code": "GA",
        "name_cn": "温柔觉醒",
        "name_en": "Gentle Awakening",
        "primary": "温柔",
        "primary_class": "gentle",
        "secondary": ["觉醒", "温暖"],

        # — Q 目标向量 (T_e) —
        "spectrum": {
            "centroid_hz":       (1500, 3000),
            "crowding_LowMid":   (0.10, 0.25),
            "crowding_Presence": (0.02, 0.10),
            "crowding_Bass":     (0.15, 0.30),
            "crowding_Air":      (0.02, 0.12),
        },
        "dynamics": {
            "DR_dB":             (8.0, 12.0),
            "Crest_mean_dB":     (12.0, 18.0),
            "SectionContrast_dB":(4.0, 8.0),
        },
        "space": {
            "SideRatio":         (0.10, 0.35),
            "Corr_LR_mean":      (0.50, 0.85),
            "MonoCompatibility": (0.70, 1.00),
        },
        "layers": {
            "vocal_ratio":       (0.20, 0.45),
        },

        # — 频谱约束矩阵 (§3.2) —
        "spectrum_constraints": {
            "SubPresence_dB":    (-2, 3),
            "MidClarity_min":    0.6,
            "AirBand_dB":        (-2, 4),
        },
        # — 动态约束矩阵 (§3.3) —
        "dynamics_constraints": {
            "LRA_LU":            (6, 10),
            "ratio_range":       (1.5, 2.5),
            "ChorusImpact_LU":   (2, 4),
            "PLR_min_dB":        8,
        },
        # — 空间约束矩阵 (§3.4) —
        "space_constraints": {
            "RT60_s":            (0.8, 1.5),
            "dry_wet_range":     (0.15, 0.30),
            "width_target":      (1.0, 1.3),
        },
        # — 情绪安全区间 (§14.3) —
        "safety_bounds": {
            "E": (0.55, 0.80), "D": (0.50, 0.75), "S": (0.35, 0.60),
            "T": (0.45, 0.70), "H": (0.40, 0.65),
        },
        # — 预期状态转移 (§13.2) —
        "expected_delta": {"dE": 0.18, "dD": 0.15, "dS": 0.12, "dT": 0.08, "dH": 0.10},
        "reverb_style": "plate",
        "risk_tolerance": 0.3,
        "applicable_sources": {
            "ai_models": ["suno", "udio"],
            "genres": ["piano_ballad", "acoustic_pop", "indie_folk"],
            "vocal_types": ["male_tenor", "female_alto", "soft_vocal"],
        },
        "embryo_direction": "原始波场常有温暖柔软的胚胎情绪方向",
        "common_defects": [
            "人声存在感不足", "高频偏暗", "动态起伏不够", "空间感偏干",
        ],
        "contraindications": [
            "原始波场高频已过度突出", "动态已被严重压缩", "低频已浑浊",
        ],
    },

    # ================================================================
    #  SE · 神圣空灵 (Sacred Ethereal) — §13.3
    # ================================================================
    "sacred_ethereal": {
        "code": "SE",
        "name_cn": "神圣空灵",
        "name_en": "Sacred Ethereal",
        "primary": "神圣",
        "primary_class": "sacred",
        "secondary": ["空灵", "超然"],
        "spectrum": {
            "centroid_hz":       (2500, 5000),
            "crowding_LowMid":   (0.05, 0.18),
            "crowding_Presence": (0.02, 0.08),
            "crowding_Bass":     (0.05, 0.20),
            "crowding_Air":      (0.05, 0.20),
        },
        "dynamics": {
            "DR_dB":             (10.0, 16.0),
            "Crest_mean_dB":     (14.0, 22.0),
            "SectionContrast_dB":(6.0, 12.0),
        },
        "space": {
            "SideRatio":         (0.20, 0.60),
            "Corr_LR_mean":      (0.30, 0.65),
            "MonoCompatibility": (0.60, 0.90),
        },
        "layers": {"vocal_ratio": (0.10, 0.30)},
        "spectrum_constraints": {
            "SubPresence_dB":    (-4, -1),
            "MidClarity_min":    0.5,
            "AirBand_dB":        (2, 6),
        },
        "dynamics_constraints": {
            "LRA_LU":            (10, 16),
            "ratio_range":       (1.2, 2.0),
            "ChorusImpact_LU":   (3, 6),
            "PLR_min_dB":        10,
        },
        "space_constraints": {
            "RT60_s":            (2.5, 4.0),
            "dry_wet_range":     (0.40, 0.65),
            "width_target":      (1.2, 1.5),
        },
        "safety_bounds": {
            "E": (0.50, 0.75), "D": (0.55, 0.85), "S": (0.55, 0.85),
            "T": (0.40, 0.60), "H": (0.30, 0.55),
        },
        "expected_delta": {"dE": 0.10, "dD": 0.20, "dS": 0.28, "dT": 0.02, "dH": 0.05},
        "reverb_style": "hall",
        "risk_tolerance": 0.4,
        "applicable_sources": {
            "ai_models": ["suno", "udio"],
            "genres": ["choral", "ambient", "new_age"],
            "vocal_types": ["choir", "ethereal_vocal"],
        },
        "embryo_direction": "原始波场常有空灵、流动的胚胎情绪方向",
        "common_defects": [
            "空间感不足", "高频不够打开", "混响量不足", "人声过于突出",
        ],
        "contraindications": [
            "原始波场高频已严重刺耳", "混响已过度", "空间感已过宽导致单声道兼容问题",
        ],
    },

    # ================================================================
    #  UD · 都市危险 (Urban Danger) — §13.4
    # ================================================================
    "urban_danger": {
        "code": "UD",
        "name_cn": "都市危险",
        "name_en": "Urban Danger",
        "primary": "危险",
        "primary_class": "urban",
        "secondary": ["压迫", "紧张"],
        "spectrum": {
            "centroid_hz":       (2000, 4000),
            "crowding_LowMid":   (0.15, 0.30),
            "crowding_Presence": (0.05, 0.18),
            "crowding_Bass":     (0.25, 0.50),
            "crowding_Air":      (0.01, 0.08),
        },
        "dynamics": {
            "DR_dB":             (4.0, 8.0),
            "Crest_mean_dB":     (8.0, 14.0),
            "SectionContrast_dB":(2.0, 5.0),
        },
        "space": {
            "SideRatio":         (0.05, 0.20),
            "Corr_LR_mean":      (0.65, 0.95),
            "MonoCompatibility": (0.75, 1.00),
        },
        "layers": {"vocal_ratio": (0.25, 0.50)},
        "spectrum_constraints": {
            "SubPresence_dB":    (2, 6),
            "MidClarity_min":    0.3,
            "AirBand_dB":        (-4, -1),
        },
        "dynamics_constraints": {
            "LRA_LU":            (4, 8),
            "ratio_range":       (3.0, 8.0),
            "ChorusImpact_LU":   (1, 3),
            "PLR_min_dB":        6,
        },
        "space_constraints": {
            "RT60_s":            (0.3, 0.8),
            "dry_wet_range":     (0.10, 0.20),
            "width_target":      (0.8, 1.1),
        },
        "safety_bounds": {
            "E": (0.40, 0.65), "D": (0.30, 0.55), "S": (0.25, 0.45),
            "T": (0.55, 0.85), "H": (0.50, 0.80),
        },
        "expected_delta": {"dE": 0.05, "dD": 0.05, "dS": 0.05, "dT": 0.20, "dH": 0.22},
        "reverb_style": "room",
        "risk_tolerance": 0.65,
        "applicable_sources": {
            "ai_models": ["suno", "udio"],
            "genres": ["trap", "dark_pop", "industrial", "hip_hop"],
            "vocal_types": ["male_baritone", "rap_vocal"],
        },
        "embryo_direction": "原始波场常有暗色调、紧张感的胚胎情绪方向",
        "common_defects": [
            "低频冲击力不足", "中高频不够紧张", "动态不够压迫", "空间太宽",
        ],
        "contraindications": [
            "低频已严重过载", "动态已经完全压平", "中频已过度刺耳",
        ],
    },

    # ================================================================
    #  LW · 孤独留白 (Lonely Whitespace) — §13.5
    # ================================================================
    "lonely_whitespace": {
        "code": "LW",
        "name_cn": "孤独留白",
        "name_en": "Lonely Whitespace",
        "primary": "孤独",
        "primary_class": "lonely",
        "secondary": ["内省", "距离"],
        "spectrum": {
            "centroid_hz":       (1000, 2500),
            "crowding_LowMid":   (0.05, 0.20),
            "crowding_Presence": (0.01, 0.06),
            "crowding_Bass":     (0.05, 0.20),
            "crowding_Air":      (0.01, 0.08),
        },
        "dynamics": {
            "DR_dB":             (10.0, 16.0),
            "Crest_mean_dB":     (14.0, 20.0),
            "SectionContrast_dB":(6.0, 12.0),
        },
        "space": {
            "SideRatio":         (0.05, 0.25),
            "Corr_LR_mean":      (0.50, 0.80),
            "MonoCompatibility": (0.65, 0.95),
        },
        "layers": {"vocal_ratio": (0.10, 0.30)},
        "spectrum_constraints": {
            "SubPresence_dB":    (-3, 0),
            "MidClarity_min":    0.4,
            "AirBand_dB":        (-3, 0),
        },
        "dynamics_constraints": {
            "LRA_LU":            (8, 12),
            "ratio_range":       (1.5, 2.5),
            "ChorusImpact_LU":   (1.5, 3),
            "PLR_min_dB":        9,
        },
        "space_constraints": {
            "RT60_s":            (1.2, 2.5),
            "dry_wet_range":     (0.25, 0.50),
            "width_target":      (1.0, 1.3),
        },
        "safety_bounds": {
            "E": (0.45, 0.65), "D": (0.50, 0.70), "S": (0.35, 0.60),
            "T": (0.40, 0.60), "H": (0.30, 0.50),
        },
        "expected_delta": {"dE": 0.08, "dD": 0.12, "dS": 0.20, "dT": 0.05, "dH": 0.05},
        "reverb_style": "room",
        "risk_tolerance": 0.5,
        "applicable_sources": {
            "ai_models": ["suno", "udio"],
            "genres": ["indie_folk", "ambient_pop", "post_rock"],
            "vocal_types": ["soft_vocal", "male_falsetto"],
        },
        "embryo_direction": "原始波场常有稀疏、空旷的胚胎情绪方向",
        "common_defects": [
            "空间感不够深远", "中频偏薄", "缺乏距离感", "高频偏暗",
        ],
        "contraindications": [
            "原始空间感已过度（混响沼泽）", "中频已过度稀薄",
        ],
    },

    # ================================================================
    #  HL · 治愈温暖 (Healing Warmth) — §13.6
    # ================================================================
    "healing_warmth": {
        "code": "HL",
        "name_cn": "治愈温暖",
        "name_en": "Healing Warmth",
        "primary": "治愈",
        "primary_class": "gentle",
        "secondary": ["温暖", "安慰"],
        "spectrum": {
            "centroid_hz":       (1500, 3000),
            "crowding_LowMid":   (0.15, 0.30),
            "crowding_Presence": (0.02, 0.10),
            "crowding_Bass":     (0.15, 0.35),
            "crowding_Air":      (0.02, 0.10),
        },
        "dynamics": {
            "DR_dB":             (6.0, 10.0),
            "Crest_mean_dB":     (10.0, 16.0),
            "SectionContrast_dB":(3.0, 7.0),
        },
        "space": {
            "SideRatio":         (0.10, 0.30),
            "Corr_LR_mean":      (0.55, 0.85),
            "MonoCompatibility": (0.70, 1.00),
        },
        "layers": {"vocal_ratio": (0.20, 0.45)},
        "spectrum_constraints": {
            "SubPresence_dB":    (0, 4),
            "MidClarity_min":    0.5,
            "AirBand_dB":        (-1, 2),
        },
        "dynamics_constraints": {
            "LRA_LU":            (6, 10),
            "ratio_range":       (1.5, 2.5),
            "ChorusImpact_LU":   (2, 4),
            "PLR_min_dB":        8,
        },
        "space_constraints": {
            "RT60_s":            (0.6, 1.2),
            "dry_wet_range":     (0.12, 0.25),
            "width_target":      (1.0, 1.2),
        },
        "safety_bounds": {
            "E": (0.55, 0.80), "D": (0.50, 0.70), "S": (0.30, 0.50),
            "T": (0.40, 0.60), "H": (0.45, 0.65),
        },
        "expected_delta": {"dE": 0.15, "dD": 0.10, "dS": 0.08, "dT": 0.05, "dH": 0.12},
        "reverb_style": "plate",
        "risk_tolerance": 0.3,
        "applicable_sources": {
            "ai_models": ["suno", "udio"],
            "genres": ["healing_piano", "meditation", "light_jazz", "bossa_nova"],
            "vocal_types": ["soft_vocal", "female_soprano"],
        },
        "embryo_direction": "原始波场常有柔和、温暖、开放的胚胎情绪方向",
        "common_defects": [
            "低频温暖感不足", "中频不够平滑", "高频略暗", "空间感偏干",
        ],
        "contraindications": [
            "低频已过重（温暖→闷热）", "动态已被过度压缩", "高频已过度突出",
        ],
    },

    # ================================================================
    #  DR · 黑暗浪漫 (Dark Romantic) — §13.7
    # ================================================================
    "dark_romantic": {
        "code": "DR",
        "name_cn": "黑暗浪漫",
        "name_en": "Dark Romantic",
        "primary": "黑暗",
        "primary_class": "dark",
        "secondary": ["浪漫", "神秘", "性感"],
        "spectrum": {
            "centroid_hz":       (1200, 2800),
            "crowding_LowMid":   (0.15, 0.30),
            "crowding_Presence": (0.03, 0.12),
            "crowding_Bass":     (0.20, 0.40),
            "crowding_Air":      (0.01, 0.08),
        },
        "dynamics": {
            "DR_dB":             (6.0, 10.0),
            "Crest_mean_dB":     (10.0, 16.0),
            "SectionContrast_dB":(3.0, 7.0),
        },
        "space": {
            "SideRatio":         (0.15, 0.40),
            "Corr_LR_mean":      (0.40, 0.75),
            "MonoCompatibility": (0.65, 0.95),
        },
        "layers": {"vocal_ratio": (0.20, 0.45)},
        "spectrum_constraints": {
            "SubPresence_dB":    (1, 4),
            "MidClarity_min":    0.3,
            "AirBand_dB":        (-2, 1),
        },
        "dynamics_constraints": {
            "LRA_LU":            (5, 9),
            "ratio_range":       (2.0, 4.0),
            "ChorusImpact_LU":   (2, 5),
            "PLR_min_dB":        7,
        },
        "space_constraints": {
            "RT60_s":            (1.0, 2.5),
            "dry_wet_range":     (0.25, 0.45),
            "width_target":      (1.1, 1.4),
        },
        "safety_bounds": {
            "E": (0.45, 0.70), "D": (0.45, 0.65), "S": (0.40, 0.65),
            "T": (0.50, 0.75), "H": (0.50, 0.75),
        },
        "expected_delta": {"dE": 0.12, "dD": 0.10, "dS": 0.18, "dT": 0.10, "dH": 0.18},
        "reverb_style": "hall",
        "risk_tolerance": 0.65,
        "applicable_sources": {
            "ai_models": ["suno", "udio"],
            "genres": ["darkwave", "gothic_pop", "alt_rnb", "trip_hop"],
            "vocal_types": ["female_alto", "male_baritone"],
        },
        "embryo_direction": "原始波场常有深沉、暗色调的胚胎情绪方向",
        "common_defects": [
            "低频深沉感不够", "中频色调不够暗", "人声性感度不足", "空间感欠缺纵深",
        ],
        "contraindications": [
            "中低频已严重浑浊", "动态已被完全压平", "高频已过度衰减导致失去光泽",
        ],
    },

    # ================================================================
    #  WL · 废土机械 (Wasteland Mechanical) — §13.8
    # ================================================================
    "wasteland_mechanical": {
        "code": "WL",
        "name_cn": "废土机械",
        "name_en": "Wasteland Mechanical",
        "primary": "废土",
        "primary_class": "wasteland",
        "secondary": ["粗粝", "末世", "工业"],
        "spectrum": {
            "centroid_hz":       (2500, 5000),
            "crowding_LowMid":   (0.15, 0.35),
            "crowding_Presence": (0.05, 0.20),
            "crowding_Bass":     (0.30, 0.55),
            "crowding_Air":      (0.03, 0.15),
        },
        "dynamics": {
            "DR_dB":             (2.0, 6.0),
            "Crest_mean_dB":     (6.0, 12.0),
            "SectionContrast_dB":(1.0, 4.0),
        },
        "space": {
            "SideRatio":         (0.03, 0.15),
            "Corr_LR_mean":      (0.70, 0.95),
            "MonoCompatibility": (0.80, 1.00),
        },
        "layers": {"vocal_ratio": (0.20, 0.45)},
        "spectrum_constraints": {
            "SubPresence_dB":    (3, 7),
            "MidClarity_min":    0.2,
            "AirBand_dB":        (0, 3),
        },
        "dynamics_constraints": {
            "LRA_LU":            (3, 6),
            "ratio_range":       (4.0, 10.0),
            "ChorusImpact_LU":   (1, 2),
            "PLR_min_dB":        5,
        },
        "space_constraints": {
            "RT60_s":            (0.2, 0.6),
            "dry_wet_range":     (0.05, 0.15),
            "width_target":      (0.6, 1.0),
        },
        "safety_bounds": {
            "E": (0.35, 0.60), "D": (0.25, 0.50), "S": (0.20, 0.40),
            "T": (0.60, 0.90), "H": (0.60, 0.90),
        },
        "expected_delta": {"dE": 0.05, "dD": 0.02, "dS": 0.02, "dT": 0.25, "dH": 0.30},
        "reverb_style": "chamber",
        "risk_tolerance": 0.8,
        "applicable_sources": {
            "ai_models": ["suno", "udio"],
            "genres": ["industrial", "ebm", "hard_techno", "noise"],
            "vocal_types": ["shouted_vocal", "processed_vocal"],
        },
        "embryo_direction": "原始波场常有粗粝、冲击性强的胚胎情绪方向",
        "common_defects": [
            "失真度不足", "瞬态不够锋利", "低频冲击力不够", "声音过于'干净'",
        ],
        "contraindications": [
            "失真已严重破坏音乐性", "次低频已压倒一切（小音箱不可听）",
        ],
    },

    # ================================================================
    #  CN · 电影感 (Cinematic) — §13.9
    # ================================================================
    "cinematic": {
        "code": "CN",
        "name_cn": "电影感",
        "name_en": "Cinematic",
        "primary": "电影",
        "primary_class": "cinematic",
        "secondary": ["宏大", "深情", "叙事"],
        "spectrum": {
            "centroid_hz":       (1800, 3500),
            "crowding_LowMid":   (0.10, 0.25),
            "crowding_Presence": (0.03, 0.10),
            "crowding_Bass":     (0.10, 0.30),
            "crowding_Air":      (0.03, 0.15),
        },
        "dynamics": {
            "DR_dB":             (10.0, 16.0),
            "Crest_mean_dB":     (14.0, 22.0),
            "SectionContrast_dB":(6.0, 12.0),
        },
        "space": {
            "SideRatio":         (0.20, 0.55),
            "Corr_LR_mean":      (0.35, 0.70),
            "MonoCompatibility": (0.60, 0.90),
        },
        "layers": {"vocal_ratio": (0.15, 0.35)},
        "spectrum_constraints": {
            "SubPresence_dB":    (-1, 3),
            "MidClarity_min":    0.6,
            "AirBand_dB":        (0, 4),
        },
        "dynamics_constraints": {
            "LRA_LU":            (8, 14),
            "ratio_range":       (1.5, 3.0),
            "ChorusImpact_LU":   (3, 6),
            "PLR_min_dB":        10,
        },
        "space_constraints": {
            "RT60_s":            (1.5, 3.0),
            "dry_wet_range":     (0.20, 0.40),
            "width_target":      (1.2, 1.5),
        },
        "safety_bounds": {
            "E": (0.55, 0.80), "D": (0.55, 0.80), "S": (0.50, 0.75),
            "T": (0.45, 0.70), "H": (0.45, 0.70),
        },
        "expected_delta": {"dE": 0.15, "dD": 0.18, "dS": 0.25, "dT": 0.10, "dH": 0.12},
        "reverb_style": "hall",
        "risk_tolerance": 0.5,
        "applicable_sources": {
            "ai_models": ["suno", "udio"],
            "genres": ["orchestral", "epic_ballad", "soundtrack"],
            "vocal_types": ["male_tenor", "female_soprano"],
        },
        "embryo_direction": "原始波场常有宏大、叙事性的胚胎情绪方向",
        "common_defects": [
            "空间感不够宏大", "动态起伏不够", "低频深度不足", "高频空气感不够",
        ],
        "contraindications": [
            "混响已过度（宏大→模糊）", "动态已过度压缩",
        ],
    },
}

# ============================================================
#  Aliases
# ============================================================

EMOTION_ALIASES = {
    "温柔觉醒": "gentle_awakening",
    "神圣空灵": "sacred_ethereal",
    "都市危险": "urban_danger",
    "孤独留白": "lonely_whitespace",
    "治愈温暖": "healing_warmth",
    "黑暗浪漫": "dark_romantic",
    "废土机械": "wasteland_mechanical",
    "电影感":   "cinematic",
    # English aliases
    "gentle": "gentle_awakening",
    "sacred": "sacred_ethereal",
    "urban":  "urban_danger",
    "lonely": "lonely_whitespace",
    "healing":"healing_warmth",
    "dark":   "dark_romantic",
    "wasteland": "wasteland_mechanical",
}

CODE_TO_KEY = {
    "GA": "gentle_awakening",
    "SE": "sacred_ethereal",
    "UD": "urban_danger",
    "LW": "lonely_whitespace",
    "HL": "healing_warmth",
    "DR": "dark_romantic",
    "WL": "wasteland_mechanical",
    "CN": "cinematic",
}

KEY_TO_CODE = {v: k for k, v in CODE_TO_KEY.items()}


def resolve_emotion(name: str) -> str:
    """将中文名/英文名/代码解析为 emotion key"""
    if name in EMOTION_TARGETS_V2:
        return name
    if name in EMOTION_ALIASES:
        return EMOTION_ALIASES[name]
    if name in CODE_TO_KEY:
        return CODE_TO_KEY[name]
    # 模糊匹配
    for key, target in EMOTION_TARGETS_V2.items():
        if name in key or key in name:
            return key
    raise KeyError(f"Unknown emotion: {name}. Available: {list(EMOTION_TARGETS_V2.keys())}")


def get_emotion_target(name: str) -> dict:
    """获取完整情绪目标数据"""
    key = resolve_emotion(name)
    return EMOTION_TARGETS_V2[key]


def get_safety_bounds(name: str) -> dict[str, tuple[float, float]]:
    """获取情绪安全区间 [E, D, S, T, H]"""
    target = get_emotion_target(name)
    return target["safety_bounds"]


def get_ideal_process_vector(name: str) -> np.ndarray:
    """获取情绪的理想到处理五维向量 (区间的中点)"""
    bounds = get_safety_bounds(name)
    return np.array([
        (bounds["E"][0] + bounds["E"][1]) / 2,
        (bounds["D"][0] + bounds["D"][1]) / 2,
        (bounds["S"][0] + bounds["S"][1]) / 2,
        (bounds["T"][0] + bounds["T"][1]) / 2,
        (bounds["H"][0] + bounds["H"][1]) / 2,
    ])


def list_all_emotions() -> list[str]:
    """列出所有已定义情绪"""
    return list(EMOTION_TARGETS_V2.keys())
