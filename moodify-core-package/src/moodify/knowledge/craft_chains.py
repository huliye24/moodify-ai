"""
craft_chains_data.py — 完整 8 情绪 × 15 参数工艺链数据
=========================================================
数据来源: SPEC §13.2-§13.9
每条链: 15 DSP parameters × (min, rec, max) + risk_warnings + contraindications

参数 ID 对照 (SPEC §8.1):
  P01 vocal_presence_freq [Hz]
  P02 vocal_presence_gain [dB]
  P03 vocal_presence_q    [-]
  P04 proximity_low_freq  [Hz]
  P05 proximity_low_gain  [dB]
  P06 compression_ratio   [:1]
  P07 compression_attack  [ms]
  P08 compression_release [ms]
  P09 compression_threshold [dB]
  P10 reverb_t60          [s]
  P11 reverb_dry_wet      [-]
  P12 reverb_width        [-]
  P13 harmonic_drive      [-]
  P14 high_shelf_freq     [Hz]
  P15 high_shelf_gain     [dB]
"""

PARAM_KEYS = [
    "P01_vocal_presence_freq",
    "P02_vocal_presence_gain",
    "P03_vocal_presence_q",
    "P04_proximity_low_freq",
    "P05_proximity_low_gain",
    "P06_compression_ratio",
    "P07_compression_attack",
    "P08_compression_release",
    "P09_compression_threshold",
    "P10_reverb_t60",
    "P11_reverb_dry_wet",
    "P12_reverb_width",
    "P13_harmonic_drive",
    "P14_high_shelf_freq",
    "P15_high_shelf_gain",
]

# ============================================================
#  8 情绪 × 15 参数 = 120 数据点
# ============================================================

CRAFT_CHAINS_15PARAMS = {

    # ==========================================================
    #  GA · 温柔觉醒 (§13.2)
    # ==========================================================
    "GA": {
        "P01_vocal_presence_freq":    {"min": 2500, "rec": 3000, "max": 3500, "unit": "Hz"},
        "P02_vocal_presence_gain":    {"min": 1.5,  "rec": 2.5,  "max": 3.5,  "unit": "dB"},
        "P03_vocal_presence_q":       {"min": 0.5,  "rec": 0.7,  "max": 0.9,  "unit": ""},
        "P04_proximity_low_freq":     {"min": 150,  "rec": 200,  "max": 250,  "unit": "Hz"},
        "P05_proximity_low_gain":     {"min": 1.5,  "rec": 2.5,  "max": 3.5,  "unit": "dB"},
        "P06_compression_ratio":      {"min": 1.5,  "rec": 2.0,  "max": 2.5,  "unit": ":1"},
        "P07_compression_attack":     {"min": 10,   "rec": 15,   "max": 25,   "unit": "ms"},
        "P08_compression_release":    {"min": 100,  "rec": 150,  "max": 400,  "unit": "ms"},
        "P09_compression_threshold":  {"min": -28,  "rec": -24,  "max": -20,  "unit": "dB"},
        "P10_reverb_t60":             {"min": 0.8,  "rec": 1.2,  "max": 1.5,  "unit": "s"},
        "P11_reverb_dry_wet":         {"min": 0.15, "rec": 0.20, "max": 0.30, "unit": ""},
        "P12_reverb_width":           {"min": 0.7,  "rec": 0.8,  "max": 0.9,  "unit": ""},
        "P13_harmonic_drive":         {"min": 0.05, "rec": 0.15, "max": 0.20, "unit": ""},
        "P14_high_shelf_freq":        {"min": 8000, "rec": 10000,"max": 12000,"unit": "Hz"},
        "P15_high_shelf_gain":        {"min": 1.0,  "rec": 2.0,  "max": 3.0,  "unit": "dB"},
        "risk_warnings": [
            "高频增益 > +3dB 会从'温柔'滑向'明亮/刺耳'",
            "压缩比 > 2.5:1 会压碎原曲的动态呼吸感",
            "混响湿比 > 0.30 会淹没前景人声，失去亲密感",
            "谐波驱动 > 0.20 会产生可闻失真，破坏'温柔'质感",
        ],
        "contraindications": [
            "原始波场高频已过度突出",
            "动态已被严重压缩",
            "低频已浑浊",
        ],
        "processing_steps": [
            {"step": 1, "name": "人声存在感增强", "actions": [{"type": "peak_eq", "params": {"freq": 3000, "gain": 2.5, "q": 0.7}}]},
            {"step": 2, "name": "近讲低频温暖", "actions": [{"type": "low_shelf", "params": {"freq": 200, "gain": 2.5}}]},
            {"step": 3, "name": "温和动态塑形", "actions": [{"type": "compressor", "params": {"ratio": 2.0, "attack": 15, "release": 150, "threshold": -24}}]},
            {"step": 4, "name": "温暖谐波补充", "actions": [{"type": "harmonic_exciter", "params": {"drive": 0.15}}]},
            {"step": 5, "name": "短暖混响", "actions": [{"type": "reverb", "params": {"t60": 1.2, "dry_wet": 0.20, "width": 0.8}}]},
            {"step": 6, "name": "柔和空气感", "actions": [{"type": "high_shelf", "params": {"freq": 10000, "gain": 2.0}}]},
        ],
    },

    # ==========================================================
    #  SE · 神圣空灵 (§13.3)
    # ==========================================================
    "SE": {
        "P01_vocal_presence_freq":    {"min": 2500, "rec": 3000, "max": 4000, "unit": "Hz"},
        "P02_vocal_presence_gain":    {"min": 1.0,  "rec": 2.0,  "max": 3.0,  "unit": "dB"},
        "P03_vocal_presence_q":       {"min": 0.4,  "rec": 0.5,  "max": 0.7,  "unit": ""},
        "P04_proximity_low_freq":     {"min": 100,  "rec": 150,  "max": 200,  "unit": "Hz"},
        "P05_proximity_low_gain":     {"min": -2.0, "rec": -1.0, "max": 1.0,  "unit": "dB"},
        "P06_compression_ratio":      {"min": 1.2,  "rec": 1.5,  "max": 2.0,  "unit": ":1"},
        "P07_compression_attack":     {"min": 15,   "rec": 25,   "max": 40,   "unit": "ms"},
        "P08_compression_release":    {"min": 200,  "rec": 300,  "max": 500,  "unit": "ms"},
        "P09_compression_threshold":  {"min": -30,  "rec": -26,  "max": -20,  "unit": "dB"},
        "P10_reverb_t60":             {"min": 2.5,  "rec": 3.5,  "max": 4.0,  "unit": "s"},
        "P11_reverb_dry_wet":         {"min": 0.40, "rec": 0.55, "max": 0.65, "unit": ""},
        "P12_reverb_width":           {"min": 0.9,  "rec": 1.0,  "max": 1.0,  "unit": ""},
        "P13_harmonic_drive":         {"min": 0,    "rec": 0,    "max": 0.05, "unit": ""},
        "P14_high_shelf_freq":        {"min": 10000,"rec": 12000,"max": 14000,"unit": "Hz"},
        "P15_high_shelf_gain":        {"min": 2.0,  "rec": 4.0,  "max": 6.0,  "unit": "dB"},
        "risk_warnings": [
            "混响湿比 > 0.65 = 完全淹没清晰度，失去音乐可辨性",
            "高频增益 > +6dB = 听觉疲劳急剧上升",
            "混响 T60 > 4s = 前后音符重叠产生频率堆积",
            "低频过度衰减 (< -3dB) = 失去身体感支撑",
        ],
        "contraindications": [
            "原始空间感已过度", "高频已严重刺耳",
        ],
        "processing_steps": [
            {"step": 1, "name": "轻盈人声", "actions": [{"type": "peak_eq", "params": {"freq": 3000, "gain": 2.0, "q": 0.5}}]},
            {"step": 2, "name": "克制低频", "actions": [{"type": "low_shelf", "params": {"freq": 150, "gain": -1.0}}]},
            {"step": 3, "name": "保留动态", "actions": [{"type": "compressor", "params": {"ratio": 1.5, "attack": 25, "release": 300, "threshold": -26}}]},
            {"step": 4, "name": "宏大混响", "actions": [{"type": "reverb", "params": {"t60": 3.5, "dry_wet": 0.55, "width": 1.0}}]},
            {"step": 5, "name": "空气感打开", "actions": [{"type": "high_shelf", "params": {"freq": 12000, "gain": 4.0}}]},
        ],
    },

    # ==========================================================
    #  UD · 都市危险 (§13.4)
    # ==========================================================
    "UD": {
        "P01_vocal_presence_freq":    {"min": 3000, "rec": 3500, "max": 4500, "unit": "Hz"},
        "P02_vocal_presence_gain":    {"min": 1.0,  "rec": 2.0,  "max": 3.0,  "unit": "dB"},
        "P03_vocal_presence_q":       {"min": 0.6,  "rec": 0.8,  "max": 1.2,  "unit": ""},
        "P04_proximity_low_freq":     {"min": 60,   "rec": 100,  "max": 150,  "unit": "Hz"},
        "P05_proximity_low_gain":     {"min": 3.0,  "rec": 4.5,  "max": 6.0,  "unit": "dB"},
        "P06_compression_ratio":      {"min": 3.0,  "rec": 5.0,  "max": 8.0,  "unit": ":1"},
        "P07_compression_attack":     {"min": 2,    "rec": 5,    "max": 10,   "unit": "ms"},
        "P08_compression_release":    {"min": 50,   "rec": 80,   "max": 120,  "unit": "ms"},
        "P09_compression_threshold":  {"min": -32,  "rec": -28,  "max": -22,  "unit": "dB"},
        "P10_reverb_t60":             {"min": 0.2,  "rec": 0.5,  "max": 0.8,  "unit": "s"},
        "P11_reverb_dry_wet":         {"min": 0.10, "rec": 0.18, "max": 0.25, "unit": ""},
        "P12_reverb_width":           {"min": 0.6,  "rec": 0.8,  "max": 1.0,  "unit": ""},
        "P13_harmonic_drive":         {"min": 0.20, "rec": 0.35, "max": 0.50, "unit": ""},
        "P14_high_shelf_freq":        {"min": 6000, "rec": 8000, "max": 10000,"unit": "Hz"},
        "P15_high_shelf_gain":        {"min": -3.0, "rec": -1.5, "max": 0,    "unit": "dB"},
        "risk_warnings": [
            "压缩比 > 8:1 = 动态完全压平",
            "低频增益 > +6dB = 浑浊掩盖中频",
            "谐波驱动 > 0.50 = 失真变成噪音",
            "高频衰减 > -3dB = 过于压抑",
        ],
        "contraindications": [
            "动态已完全压平", "低频已严重过载",
        ],
        "processing_steps": [
            {"step": 1, "name": "紧张人声", "actions": [{"type": "peak_eq", "params": {"freq": 3500, "gain": 2.0, "q": 0.8}}]},
            {"step": 2, "name": "压迫低频", "actions": [{"type": "low_shelf", "params": {"freq": 100, "gain": 4.5}}]},
            {"step": 3, "name": "重度压缩", "actions": [{"type": "compressor", "params": {"ratio": 5.0, "attack": 5, "release": 80, "threshold": -28}}]},
            {"step": 4, "name": "工业谐波", "actions": [{"type": "harmonic_exciter", "params": {"drive": 0.35}}]},
            {"step": 5, "name": "紧致空间", "actions": [{"type": "reverb", "params": {"t60": 0.5, "dry_wet": 0.18, "width": 0.8}}]},
            {"step": 6, "name": "压抑高频", "actions": [{"type": "high_shelf", "params": {"freq": 8000, "gain": -1.5}}]},
        ],
    },

    # ==========================================================
    #  LW · 孤独留白 (§13.5)
    # ==========================================================
    "LW": {
        "P01_vocal_presence_freq":    {"min": 2000, "rec": 2500, "max": 3000, "unit": "Hz"},
        "P02_vocal_presence_gain":    {"min": 1.0,  "rec": 1.5,  "max": 2.5,  "unit": "dB"},
        "P03_vocal_presence_q":       {"min": 0.4,  "rec": 0.5,  "max": 0.7,  "unit": ""},
        "P04_proximity_low_freq":     {"min": 150,  "rec": 250,  "max": 350,  "unit": "Hz"},
        "P05_proximity_low_gain":     {"min": -2.0, "rec": 0,    "max": 1.5,  "unit": "dB"},
        "P06_compression_ratio":      {"min": 1.5,  "rec": 2.0,  "max": 2.5,  "unit": ":1"},
        "P07_compression_attack":     {"min": 10,   "rec": 20,   "max": 30,   "unit": "ms"},
        "P08_compression_release":    {"min": 150,  "rec": 250,  "max": 400,  "unit": "ms"},
        "P09_compression_threshold":  {"min": -26,  "rec": -22,  "max": -18,  "unit": "dB"},
        "P10_reverb_t60":             {"min": 1.2,  "rec": 2.0,  "max": 2.5,  "unit": "s"},
        "P11_reverb_dry_wet":         {"min": 0.25, "rec": 0.40, "max": 0.50, "unit": ""},
        "P12_reverb_width":           {"min": 0.8,  "rec": 1.0,  "max": 1.2,  "unit": ""},
        "P13_harmonic_drive":         {"min": 0,    "rec": 0.05, "max": 0.10, "unit": ""},
        "P14_high_shelf_freq":        {"min": 8000, "rec": 10000,"max": 12000,"unit": "Hz"},
        "P15_high_shelf_gain":        {"min": -2.0, "rec": -1.0, "max": 1.0,  "unit": "dB"},
        "risk_warnings": [
            "混响湿比 > 0.50 = 孤独变成空洞",
            "中频过度衰减 = 人声失去存在感",
            "压缩过重 = 动态起伏被打平",
        ],
        "contraindications": [
            "混响已过度", "动态已被严重压缩",
        ],
        "processing_steps": [
            {"step": 1, "name": "内省人声", "actions": [{"type": "peak_eq", "params": {"freq": 2500, "gain": 1.5, "q": 0.5}}]},
            {"step": 2, "name": "克制低频", "actions": [{"type": "low_shelf", "params": {"freq": 250, "gain": 0}}]},
            {"step": 3, "name": "轻压缩", "actions": [{"type": "compressor", "params": {"ratio": 2.0, "attack": 20, "release": 250, "threshold": -22}}]},
            {"step": 4, "name": "深远混响", "actions": [{"type": "reverb", "params": {"t60": 2.0, "dry_wet": 0.40, "width": 1.0}}]},
            {"step": 5, "name": "暗调高频", "actions": [{"type": "high_shelf", "params": {"freq": 10000, "gain": -1.0}}]},
        ],
    },

    # ==========================================================
    #  HL · 治愈温暖 (§13.6)
    # ==========================================================
    "HL": {
        "P01_vocal_presence_freq":    {"min": 2500, "rec": 3000, "max": 3500, "unit": "Hz"},
        "P02_vocal_presence_gain":    {"min": 1.5,  "rec": 2.0,  "max": 3.0,  "unit": "dB"},
        "P03_vocal_presence_q":       {"min": 0.5,  "rec": 0.6,  "max": 0.8,  "unit": ""},
        "P04_proximity_low_freq":     {"min": 150,  "rec": 200,  "max": 300,  "unit": "Hz"},
        "P05_proximity_low_gain":     {"min": 2.0,  "rec": 3.0,  "max": 4.0,  "unit": "dB"},
        "P06_compression_ratio":      {"min": 1.5,  "rec": 2.0,  "max": 2.5,  "unit": ":1"},
        "P07_compression_attack":     {"min": 10,   "rec": 20,   "max": 30,   "unit": "ms"},
        "P08_compression_release":    {"min": 150,  "rec": 250,  "max": 400,  "unit": "ms"},
        "P09_compression_threshold":  {"min": -28,  "rec": -24,  "max": -18,  "unit": "dB"},
        "P10_reverb_t60":             {"min": 0.6,  "rec": 1.0,  "max": 1.2,  "unit": "s"},
        "P11_reverb_dry_wet":         {"min": 0.12, "rec": 0.20, "max": 0.25, "unit": ""},
        "P12_reverb_width":           {"min": 0.7,  "rec": 0.85, "max": 1.0,  "unit": ""},
        "P13_harmonic_drive":         {"min": 0.10, "rec": 0.18, "max": 0.25, "unit": ""},
        "P14_high_shelf_freq":        {"min": 8000, "rec": 10000,"max": 12000,"unit": "Hz"},
        "P15_high_shelf_gain":        {"min": 1.0,  "rec": 2.0,  "max": 3.0,  "unit": "dB"},
        "risk_warnings": [
            "低频增益 > +4dB = 温暖变成闷热",
            "高频增益 > +3dB = 柔光变成刺眼",
            "混响 T60 > 1.2s = 亲密感变成空旷",
        ],
        "contraindications": [
            "低频已过重", "高频已过度突出",
        ],
        "processing_steps": [
            {"step": 1, "name": "温暖人声", "actions": [{"type": "peak_eq", "params": {"freq": 3000, "gain": 2.0, "q": 0.6}}]},
            {"step": 2, "name": "饱满低频", "actions": [{"type": "low_shelf", "params": {"freq": 200, "gain": 3.0}}]},
            {"step": 3, "name": "柔和压缩", "actions": [{"type": "compressor", "params": {"ratio": 2.0, "attack": 20, "release": 250, "threshold": -24}}]},
            {"step": 4, "name": "温暖谐波", "actions": [{"type": "harmonic_exciter", "params": {"drive": 0.18}}]},
            {"step": 5, "name": "近距混响", "actions": [{"type": "reverb", "params": {"t60": 1.0, "dry_wet": 0.20, "width": 0.85}}]},
            {"step": 6, "name": "柔光高频", "actions": [{"type": "high_shelf", "params": {"freq": 10000, "gain": 2.0}}]},
        ],
    },

    # ==========================================================
    #  DR · 黑暗浪漫 (§13.7)
    # ==========================================================
    "DR": {
        "P01_vocal_presence_freq":    {"min": 2500, "rec": 3000, "max": 4000, "unit": "Hz"},
        "P02_vocal_presence_gain":    {"min": 2.0,  "rec": 3.0,  "max": 4.0,  "unit": "dB"},
        "P03_vocal_presence_q":       {"min": 0.5,  "rec": 0.7,  "max": 1.0,  "unit": ""},
        "P04_proximity_low_freq":     {"min": 80,   "rec": 150,  "max": 200,  "unit": "Hz"},
        "P05_proximity_low_gain":     {"min": 2.0,  "rec": 3.5,  "max": 5.0,  "unit": "dB"},
        "P06_compression_ratio":      {"min": 2.0,  "rec": 3.0,  "max": 4.0,  "unit": ":1"},
        "P07_compression_attack":     {"min": 10,   "rec": 20,   "max": 30,   "unit": "ms"},
        "P08_compression_release":    {"min": 100,  "rec": 200,  "max": 350,  "unit": "ms"},
        "P09_compression_threshold":  {"min": -28,  "rec": -24,  "max": -20,  "unit": "dB"},
        "P10_reverb_t60":             {"min": 1.0,  "rec": 1.8,  "max": 2.5,  "unit": "s"},
        "P11_reverb_dry_wet":         {"min": 0.25, "rec": 0.35, "max": 0.45, "unit": ""},
        "P12_reverb_width":           {"min": 0.8,  "rec": 1.0,  "max": 1.2,  "unit": ""},
        "P13_harmonic_drive":         {"min": 0.15, "rec": 0.25, "max": 0.35, "unit": ""},
        "P14_high_shelf_freq":        {"min": 7000, "rec": 9000, "max": 11000,"unit": "Hz"},
        "P15_high_shelf_gain":        {"min": -1.0, "rec": 1.0,  "max": 2.0,  "unit": "dB"},
        "risk_warnings": [
            "中低频过重 (> +5dB) = 黑暗变成混沌",
            "高频衰减过度 (< -2dB) = 失去浪漫光泽",
            "压缩比 > 4:1 = 动态丧失",
        ],
        "contraindications": [
            "中低频已严重浑浊", "高频已过度衰减",
        ],
        "processing_steps": [
            {"step": 1, "name": "性感人声", "actions": [{"type": "peak_eq", "params": {"freq": 3000, "gain": 3.0, "q": 0.7}}]},
            {"step": 2, "name": "深沉低频", "actions": [{"type": "low_shelf", "params": {"freq": 150, "gain": 3.5}}]},
            {"step": 3, "name": "中等压缩", "actions": [{"type": "compressor", "params": {"ratio": 3.0, "attack": 20, "release": 200, "threshold": -24}}]},
            {"step": 4, "name": "暗色谐波", "actions": [{"type": "harmonic_exciter", "params": {"drive": 0.25}}]},
            {"step": 5, "name": "深邃混响", "actions": [{"type": "reverb", "params": {"t60": 1.8, "dry_wet": 0.35, "width": 1.0}}]},
            {"step": 6, "name": "克制高频", "actions": [{"type": "high_shelf", "params": {"freq": 9000, "gain": 1.0}}]},
        ],
    },

    # ==========================================================
    #  WL · 废土机械 (§13.8)
    # ==========================================================
    "WL": {
        "P01_vocal_presence_freq":    {"min": 3000, "rec": 4000, "max": 5000, "unit": "Hz"},
        "P02_vocal_presence_gain":    {"min": 2.0,  "rec": 3.5,  "max": 5.0,  "unit": "dB"},
        "P03_vocal_presence_q":       {"min": 0.8,  "rec": 1.0,  "max": 1.5,  "unit": ""},
        "P04_proximity_low_freq":     {"min": 50,   "rec": 80,   "max": 120,  "unit": "Hz"},
        "P05_proximity_low_gain":     {"min": 4.0,  "rec": 5.5,  "max": 7.0,  "unit": "dB"},
        "P06_compression_ratio":      {"min": 4.0,  "rec": 6.0,  "max": 10.0, "unit": ":1"},
        "P07_compression_attack":     {"min": 1,    "rec": 3,    "max": 5,    "unit": "ms"},
        "P08_compression_release":    {"min": 30,   "rec": 50,   "max": 80,   "unit": "ms"},
        "P09_compression_threshold":  {"min": -36,  "rec": -30,  "max": -26,  "unit": "dB"},
        "P10_reverb_t60":             {"min": 0.2,  "rec": 0.4,  "max": 0.6,  "unit": "s"},
        "P11_reverb_dry_wet":         {"min": 0.05, "rec": 0.10, "max": 0.15, "unit": ""},
        "P12_reverb_width":           {"min": 0.5,  "rec": 0.7,  "max": 0.9,  "unit": ""},
        "P13_harmonic_drive":         {"min": 0.40, "rec": 0.55, "max": 0.70, "unit": ""},
        "P14_high_shelf_freq":        {"min": 5000, "rec": 7000, "max": 9000, "unit": "Hz"},
        "P15_high_shelf_gain":        {"min": 1.0,  "rec": 2.5,  "max": 4.0,  "unit": "dB"},
        "risk_warnings": [
            "谐波驱动 > 0.70 = 完全失真噪音",
            "低频增益 > +7dB = 次低频压倒一切",
            "压缩 ratio > 10:1 = 动态完全压扁",
        ],
        "contraindications": [
            "失真已严重破坏音乐性", "次低频已压倒一切",
        ],
        "processing_steps": [
            {"step": 1, "name": "锋利人声", "actions": [{"type": "peak_eq", "params": {"freq": 4000, "gain": 3.5, "q": 1.0}}]},
            {"step": 2, "name": "冲击低频", "actions": [{"type": "low_shelf", "params": {"freq": 80, "gain": 5.5}}]},
            {"step": 3, "name": "极限压缩", "actions": [{"type": "compressor", "params": {"ratio": 6.0, "attack": 3, "release": 50, "threshold": -30}}]},
            {"step": 4, "name": "重度失真", "actions": [{"type": "harmonic_exciter", "params": {"drive": 0.55}}]},
            {"step": 5, "name": "极干空间", "actions": [{"type": "reverb", "params": {"t60": 0.4, "dry_wet": 0.10, "width": 0.7}}]},
            {"step": 6, "name": "金属高频", "actions": [{"type": "high_shelf", "params": {"freq": 7000, "gain": 2.5}}]},
        ],
    },

    # ==========================================================
    #  CN · 电影感 (§13.9)
    # ==========================================================
    "CN": {
        "P01_vocal_presence_freq":    {"min": 2500, "rec": 3000, "max": 4000, "unit": "Hz"},
        "P02_vocal_presence_gain":    {"min": 2.0,  "rec": 3.0,  "max": 4.5,  "unit": "dB"},
        "P03_vocal_presence_q":       {"min": 0.5,  "rec": 0.7,  "max": 1.0,  "unit": ""},
        "P04_proximity_low_freq":     {"min": 100,  "rec": 180,  "max": 250,  "unit": "Hz"},
        "P05_proximity_low_gain":     {"min": 1.0,  "rec": 2.5,  "max": 4.0,  "unit": "dB"},
        "P06_compression_ratio":      {"min": 1.5,  "rec": 2.5,  "max": 3.0,  "unit": ":1"},
        "P07_compression_attack":     {"min": 15,   "rec": 25,   "max": 40,   "unit": "ms"},
        "P08_compression_release":    {"min": 150,  "rec": 300,  "max": 500,  "unit": "ms"},
        "P09_compression_threshold":  {"min": -28,  "rec": -22,  "max": -18,  "unit": "dB"},
        "P10_reverb_t60":             {"min": 1.5,  "rec": 2.5,  "max": 3.5,  "unit": "s"},
        "P11_reverb_dry_wet":         {"min": 0.20, "rec": 0.30, "max": 0.40, "unit": ""},
        "P12_reverb_width":           {"min": 0.9,  "rec": 1.0,  "max": 1.0,  "unit": ""},
        "P13_harmonic_drive":         {"min": 0.10, "rec": 0.20, "max": 0.30, "unit": ""},
        "P14_high_shelf_freq":        {"min": 9000, "rec": 11000,"max": 14000,"unit": "Hz"},
        "P15_high_shelf_gain":        {"min": 1.0,  "rec": 2.5,  "max": 4.0,  "unit": "dB"},
        "risk_warnings": [
            "混响 T60 > 3.5s = 叙事感变成迷失感",
            "压缩比 > 3:1 = 电影感的呼吸被打平",
            "人声 EQ > +4.5dB = 人声脱离画面",
        ],
        "contraindications": [
            "混响已过度", "动态已被压缩过重",
        ],
        "processing_steps": [
            {"step": 1, "name": "叙事人声", "actions": [{"type": "peak_eq", "params": {"freq": 3000, "gain": 3.0, "q": 0.7}}]},
            {"step": 2, "name": "宽广低频", "actions": [{"type": "low_shelf", "params": {"freq": 180, "gain": 2.5}}]},
            {"step": 3, "name": "保留动态", "actions": [{"type": "compressor", "params": {"ratio": 2.5, "attack": 25, "release": 300, "threshold": -22}}]},
            {"step": 4, "name": "丰富谐波", "actions": [{"type": "harmonic_exciter", "params": {"drive": 0.20}}]},
            {"step": 5, "name": "史诗混响", "actions": [{"type": "reverb", "params": {"t60": 2.5, "dry_wet": 0.30, "width": 1.0}}]},
            {"step": 6, "name": "影院高频", "actions": [{"type": "high_shelf", "params": {"freq": 11000, "gain": 2.5}}]},
        ],
    },
}


# ============================================================
#  便捷函数
# ============================================================

def get_chain_params(code: str) -> dict:
    """获取指定情绪代码的完整 15 参数工艺链"""
    if code not in CRAFT_CHAINS_15PARAMS:
        raise KeyError(f"Unknown chain: {code}. Available: {list(CRAFT_CHAINS_15PARAMS.keys())}")
    return CRAFT_CHAINS_15PARAMS[code]


def get_recommended_params(code: str) -> dict[str, float]:
    """提取指定情绪代码的所有推荐参数值 → {param_name: rec_value}"""
    chain = get_chain_params(code)
    return {
        k: v["rec"] for k, v in chain.items()
        if isinstance(v, dict) and "rec" in v
    }


def get_param_range(code: str, param_id: str) -> tuple[float, float, float]:
    """获取 (min, rec, max)"""
    chain = get_chain_params(code)
    p = chain[param_id]
    return (p["min"], p["rec"], p["max"])


def get_risk_warnings(code: str) -> list[str]:
    """获取指定情绪代码的风险警告"""
    return get_chain_params(code).get("risk_warnings", [])


def get_contraindications(code: str) -> list[str]:
    """获取指定情绪代码的禁忌症"""
    return get_chain_params(code).get("contraindications", [])


def list_all_chains() -> list[str]:
    """列出所有已定义工艺链"""
    return list(CRAFT_CHAINS_15PARAMS.keys())
