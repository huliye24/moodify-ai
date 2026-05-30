"""
defect_classifier.py — AI 音乐缺陷分类器 (SPEC §6.3)
=====================================================
从 18 参数诊断结果中识别缺陷、分级严重程度、按优先级排序。

缺陷等级定义 (SPEC §5):
  Level 1 (轻微): 接近健康范围边界
  Level 2 (中等): 明确异常
  Level 3 (严重): 严重偏离健康范围

优先级排序 (SPEC §6.3):
  P1 (安全级): 相位/单声道问题
  P2 (结构级): 频谱严重失衡/动态压平/段落断裂
  P3 (感知级): 空气感不足/低频空洞/人声淹没
  P4 (审美级): 其余轻微缺陷
"""

from dataclasses import dataclass, field
from typing import Optional

from moodify.data_types import WaveStateDiagnosis


@dataclass
class Defect:
    defect_id: str                 # "DEF-S-001"
    dimension: str                 # "Spectrum" | "Dynamics" | "Space" | "Layers" | "Emotion"
    parameter: str                 # "S1_SubPresence" etc.
    severity: int                  # 0=none, 1=mild, 2=moderate, 3=severe
    description_zh: str
    current_value: float
    healthy_range: str
    priority: int = 4              # 1-4, assigned during classification

    def to_dict(self) -> dict:
        return {
            "defect_id": self.defect_id,
            "dimension": self.dimension,
            "parameter": self.parameter,
            "severity": self.severity,
            "description_zh": self.description_zh,
            "current_value": self.current_value,
            "healthy_range": self.healthy_range,
            "priority": self.priority,
        }


# ============================================================
#  缺陷检测阈值 (SPEC §5.1-§5.5 + §6.3)
# ============================================================
# 格式: param -> {level1: (lo1, hi1), level2: (lo2, hi2), level3: (lo3, hi3)}
# lo=None 表示无下限, hi=None 表示无上限

def _thresh(level1=None, level2=None, level3=None):
    """Helper: 返回阈值字典, 每个元素为 (lo, hi)"""
    return {"level1": level1, "level2": level2, "level3": level3}


DEFECT_THRESHOLDS = {
    # ——— Spectrum (SPEC §5.1) ———
    "S1_SubPresence": _thresh(
        level1=(-4.0, -3.0, +3.0, +4.0),  # (low_lo, low_hi, high_lo, high_hi)
        level2=(-6.0, -4.0, +4.0, +6.0),
        level3=(None, -6.0, +6.0, None),
    ),
    "S2_BassWarmth": _thresh(
        level1=(-3.0, -2.0, +4.0, +6.0),
        level2=(-5.0, -3.0, +6.0, +8.0),
        level3=(None, -5.0, +8.0, None),
    ),
    "S3_MidClarity": _thresh(
        level1=(0.5, 0.6, None, None),   # only lower bound matters
        level2=(0.3, 0.5, None, None),
        level3=(None, 0.3, None, None),
    ),
    "S4_AirBand": _thresh(
        level1=(-4.0, -3.0, +6.0, +8.0),
        level2=(-6.0, -4.0, +8.0, +10.0),
        level3=(None, -6.0, +10.0, None),
    ),
    "S5_SpectralTilt": _thresh(
        level1=(6.0, 8.0, None, None),   # |S5| > 6 -> level1
        level2=(8.0, 12.0, None, None),
        level3=(12.0, None, None, None),
    ),
    # ——— Dynamics (SPEC §5.2) ———
    "D1_LRA": _thresh(
        level1=(4.0, 6.0, 14.0, 16.0),
        level2=(2.0, 4.0, 16.0, 20.0),
        level3=(None, 2.0, 20.0, None),
    ),
    "D2_ChorusImpact": _thresh(
        level1=(1.0, 2.0, 6.0, 8.0),
        level2=(0.5, 1.0, 8.0, 10.0),
        level3=(None, 0.5, 10.0, None),
    ),
    "D3_MicroDynamics": _thresh(
        level1=(0.8, 1.5, None, None),
        level2=(0.3, 0.8, None, None),
        level3=(None, 0.3, None, None),
    ),
    "D4_PLR": _thresh(
        level1=(6.0, 8.0, None, None),
        level2=(4.0, 6.0, None, None),
        level3=(None, 4.0, None, None),
    ),
    # ——— Space (SPEC §5.3) ———
    "SP1_Correlation": _thresh(
        level1=(0.3, 0.4, None, None),   # low freq deficiency
        level2=(0.1, 0.3, 0.9, None),
        level3=(None, 0.1, None, None),
    ),
    "SP2_ForeBackSep": _thresh(
        level1=(1.0, 3.0, None, None),
        level2=(0.0, 1.0, 15.0, None),
        level3=(None, 0.0, None, None),
    ),
    "SP3_RT60Consist": _thresh(
        level1=(0.3, 0.5, None, None),
        level2=(0.5, 0.8, None, None),
        level3=(0.8, None, None, None),
    ),
    "SP4_WidthHealth": None,  # bool: handled separately (False = safety defect)
    # ——— Layers (SPEC §5.4) ———
    "L1_VocalSNR": _thresh(
        level1=(3.0, 6.0, None, None),
        level2=(0.0, 3.0, None, None),
        level3=(None, 0.0, None, None),
    ),
    "L2_BassClarity": _thresh(
        level1=(0.3, 0.5, None, None),
        level2=(0.15, 0.3, None, None),
        level3=(None, 0.15, None, None),
    ),
    "L3_DrumDetect": _thresh(
        level1=(0.4, 0.6, None, None),
        level2=(0.2, 0.4, None, None),
        level3=(None, 0.2, None, None),
    ),
    # ——— Emotion (SPEC §5.5) ———
    "E3_FatigueRisk": _thresh(
        level1=(50.0, 80.0, None, None),
        level2=(80.0, 120.0, None, None),
        level3=(120.0, None, None, None),
    ),
    "E4_SectionCont": _thresh(
        level1=(0.5, 0.7, None, None),
        level2=(0.3, 0.5, None, None),
        level3=(None, 0.3, None, None),
    ),
}

# 维度 → 参数映射
DIMENSION_PARAMS = {
    "Spectrum": ["S1_SubPresence", "S2_BassWarmth", "S3_MidClarity", "S4_AirBand", "S5_SpectralTilt"],
    "Dynamics": ["D1_LRA", "D2_ChorusImpact", "D3_MicroDynamics", "D4_PLR"],
    "Space":    ["SP1_Correlation", "SP2_ForeBackSep", "SP3_RT60Consist", "SP4_WidthHealth"],
    "Layers":   ["L1_VocalSNR", "L2_BassClarity", "L3_DrumDetect"],
    "Emotion":  ["E3_FatigueRisk", "E4_SectionCont"],
}

# 参数中文名
PARAM_NAMES_ZH = {
    "S1_SubPresence": "次低频存在感",
    "S2_BassWarmth": "低频温暖感",
    "S3_MidClarity": "中频清晰度",
    "S4_AirBand": "高频空气感",
    "S5_SpectralTilt": "频谱斜率",
    "D1_LRA": "响度范围",
    "D2_ChorusImpact": "副歌冲击力",
    "D3_MicroDynamics": "微动态",
    "D4_PLR": "峰响比",
    "SP1_Correlation": "声道相关性",
    "SP2_ForeBackSep": "前后景分离度",
    "SP3_RT60Consist": "RT60一致性",
    "SP4_WidthHealth": "宽度健康度",
    "L1_VocalSNR": "人声信噪比",
    "L2_BassClarity": "低频清晰度",
    "L3_DrumDetect": "鼓组检测率",
    "E3_FatigueRisk": "听觉疲劳风险",
    "E4_SectionCont": "段落连续性",
}

# 健康范围描述
HEALTHY_RANGES = {
    "S1_SubPresence": "[-3, +3] dB",
    "S2_BassWarmth": "[-2, +4] dB",
    "S3_MidClarity": "[0.6, 1.0]",
    "S4_AirBand": "[-3, +6] dB",
    "S5_SpectralTilt": "[-6, +6] dB/oct",
    "D1_LRA": "[6, 14] LU",
    "D2_ChorusImpact": "[2, 6] LU",
    "D3_MicroDynamics": "[1.5, ...] LU",
    "D4_PLR": "[8, ...] dB",
    "SP1_Correlation": "[0.4, 0.9]",
    "SP2_ForeBackSep": "[3, 12] dB",
    "SP3_RT60Consist": "[0, 0.3] s",
    "SP4_WidthHealth": "True",
    "L1_VocalSNR": "[6, ...] dB",
    "L2_BassClarity": "[0.5, 1.0]",
    "L3_DrumDetect": "[0.6, 1.0]",
    "E3_FatigueRisk": "[0, 50]",
    "E4_SectionCont": "[0.7, 1.0]",
}

# 严重度权重 (SPEC §6.1)
SEVERITY_WEIGHTS = {0: 0.0, 1: 0.25, 2: 0.5, 3: 0.75}

# 维度权重 (SPEC §6.1)
DIMENSION_WEIGHTS = {
    "Spectrum": 0.30,
    "Dynamics": 0.25,
    "Space":    0.20,
    "Layers":   0.15,
    "Emotion":  0.10,
}


class DefectClassifier:
    """AI 音乐缺陷分类器 (SPEC §6.3)"""

    def __init__(self, thresholds: dict | None = None):
        self.thresholds = thresholds or DEFECT_THRESHOLDS

    def classify(self, ws: WaveStateDiagnosis,
                 emotion_target: str = "") -> list[Defect]:
        """从诊断结果中分类所有缺陷"""
        defects = []
        seq = {"Spectrum": 0, "Dynamics": 0, "Space": 0, "Layers": 0, "Emotion": 0}

        for dim_name, param_names in DIMENSION_PARAMS.items():
            for param in param_names:
                value = self._get_param_value(ws, param)
                if value is None:
                    continue

                severity = self._get_severity(param, value)
                if severity > 0:
                    seq[dim_name] += 1
                    defect = Defect(
                        defect_id=f"DEF-{dim_name[0]}-{seq[dim_name]:03d}",
                        dimension=dim_name,
                        parameter=param,
                        severity=severity,
                        description_zh=self._describe(param, value, severity),
                        current_value=value,
                        healthy_range=HEALTHY_RANGES.get(param, "N/A"),
                    )
                    defects.append(defect)

        # 特殊处理: SP4_WidthHealth (bool)
        if not ws.Space.SP4_WidthHealth:
            defects.append(Defect(
                defect_id="DEF-SP-999",
                dimension="Space",
                parameter="SP4_WidthHealth",
                severity=3,
                description_zh="相位反相或单声道兼容性崩溃",
                current_value=0,
                healthy_range="True",
            ))

        # 分配优先级
        defects = self._assign_priorities(defects, emotion_target)
        defects.sort(key=lambda d: (d.priority, -d.severity))

        return defects

    def classify_sorted(self, ws: WaveStateDiagnosis,
                        emotion_target: str = "") -> list[Defect]:
        """分类缺陷并按优先级排序"""
        return self.classify(ws, emotion_target)

    def _get_param_value(self, ws: WaveStateDiagnosis, param: str) -> float | None:
        """从 WaveStateDiagnosis 中提取参数值.

        自动从 ParameterWithUncertainty 中解包 .value,
        SP4_WidthHealth (bool) 特殊处理.
        """
        try:
            if param.startswith("S"):
                raw = getattr(ws.Spectrum, param, None)
            elif param.startswith("D"):
                raw = getattr(ws.Dynamics, param, None)
            elif param.startswith("SP"):
                raw = getattr(ws.Space, param, None)
            elif param.startswith("L"):
                raw = getattr(ws.Layers, param, None)
            elif param.startswith("E"):
                raw = getattr(ws.Emotion, param, None)
            else:
                return None
            # Unwrap ParameterWithUncertainty, pass bool through
            if hasattr(raw, 'value') and not isinstance(raw, bool):
                return float(raw.value)
            return None if raw is None else float(raw) if not isinstance(raw, bool) else None
        except Exception:
            return None

    def _get_severity(self, param: str, value: float) -> int:
        """单个参数 → 严重等级 0/1/2/3"""
        thresh = self.thresholds.get(param)
        if thresh is None:
            return 0

        for level in [3, 2, 1]:
            lvl_data = thresh.get(f"level{level}")
            if lvl_data is None:
                continue
            lo_low, lo_high, hi_low, hi_high = lvl_data

            # 检查下限
            if lo_low is not None and lo_high is not None:
                if lo_low < value <= lo_high:
                    return level
            elif lo_low is None and lo_high is not None:
                if value <= lo_high:
                    return level

            # 检查上限
            if hi_low is not None and hi_high is not None:
                if hi_low <= value < hi_high:
                    return level
            elif hi_low is not None and hi_high is None:
                if value >= hi_low:
                    return level

            # 对称阈值 (|S5| 类)
            if lo_low is not None and lo_high is None and hi_low is None:
                abs_val = abs(value)
                if abs_val >= lo_low and (level == 3 or abs_val < thresh.get(f"level{level+1}", (float('inf'),))[0]):
                    return level

        return 0

    def _assign_priorities(self, defects: list[Defect],
                           emotion_target: str = "") -> list[Defect]:
        """分配 1-4 优先级 (SPEC §6.3)"""
        for d in defects:
            # P1 (安全级): SP4=False, SP1 < 0.1
            if d.parameter == "SP4_WidthHealth":
                d.priority = 1
            elif d.parameter == "SP1_Correlation" and d.current_value < 0.1:
                d.priority = 1
            elif d.parameter == "S3_MidClarity" and d.severity >= 2:
                d.priority = 2
            elif d.parameter == "D1_LRA" and d.current_value < 2.0:
                d.priority = 2
            elif d.parameter == "E4_SectionCont" and d.severity >= 2:
                d.priority = 2
            elif d.parameter == "S4_AirBand" and d.current_value < -6.0:
                d.priority = 3
            elif d.parameter == "S1_SubPresence" and d.current_value < -6.0:
                d.priority = 3
            elif d.parameter == "L1_VocalSNR" and d.current_value < 0.0:
                d.priority = 3
            else:
                d.priority = 4
        return defects

    def _describe(self, param: str, value: float, severity: int) -> str:
        """生成缺陷中文描述"""
        name = PARAM_NAMES_ZH.get(param, param)
        levels = ["", "轻微", "中等", "严重"]
        direction = ""
        if value < 0:
            direction = "偏低"
        else:
            direction = "偏高"

        if param == "S3_MidClarity":
            return f"{name}{levels[severity]}不足 ({value:.2f})"
        elif param in ("SP1_Correlation", "L2_BassClarity", "L3_DrumDetect", "E4_SectionCont"):
            return f"{name}{levels[severity]}偏低 ({value:.3f})"
        elif param == "S5_SpectralTilt":
            return f"{name}{levels[severity]}异常 (|{value:.1f}| dB/oct)"
        elif param in ("E3_FatigueRisk",):
            return f"{name}{levels[severity]}升高 ({value:.1f})"
        else:
            return f"{name}{levels[severity]}{direction} ({value:.1f})"

    def get_defect_summary(self, defects: list[Defect]) -> dict:
        """缺陷概况统计"""
        summary = {
            "total": len(defects),
            "by_severity": {1: 0, 2: 0, 3: 0},
            "by_dimension": {"Spectrum": 0, "Dynamics": 0, "Space": 0, "Layers": 0, "Emotion": 0},
            "by_priority": {1: 0, 2: 0, 3: 0, 4: 0},
        }
        for d in defects:
            summary["by_severity"][d.severity] = summary["by_severity"].get(d.severity, 0) + 1
            summary["by_dimension"][d.dimension] = summary["by_dimension"].get(d.dimension, 0) + 1
            summary["by_priority"][d.priority] = summary["by_priority"].get(d.priority, 0) + 1
        return summary

    def get_dimension_severity_sum(self, defects: list[Defect],
                                    dim_name: str) -> float:
        """计算单维度的严重度加权和 (用于 WHS 计算)"""
        total = 0.0
        count = 0
        max_possible = len(DIMENSION_PARAMS.get(dim_name, [])) * 0.75
        for d in defects:
            if d.dimension == dim_name:
                total += SEVERITY_WEIGHTS.get(d.severity, 0)
                count += 1
        return total / max(max_possible, 1)
