"""
health_scorer.py — WHS / EDS 评分器 (SPEC §6)
===============================================
WHS (Wave Health Score):  0-100 声学技术健康度评分
EDS (Emotion Development Score): 处理后向目标情绪靠近的程度

公式 (SPEC §6.1-§6.2):
  WHS = SUM(w_dim * dim_score_dim)
  EDS = 100 * (1 - norm_dist), where norm_dist = dist(WS_final, WS_target) / dist(WS_raw, WS_target)
"""

import numpy as np

from moodify.data_types import WaveStateDiagnosis
from moodify.diagnosis.defect_classifier import (
    DefectClassifier, Defect,
    DIMENSION_WEIGHTS,
)


# ============================================================
#  情绪目标理想波场状态 (临时, C3 完成后替换)
# ============================================================

# 每个情绪的理想处理五维向量 [E, D, S, T, H]
EMOTION_IDEAL_VECTORS = {
    "温柔": np.array([0.675, 0.625, 0.475, 0.575, 0.525]),
    "神圣": np.array([0.625, 0.700, 0.700, 0.500, 0.425]),
    "都市": np.array([0.525, 0.425, 0.350, 0.700, 0.650]),
    "孤独": np.array([0.550, 0.600, 0.475, 0.500, 0.400]),
    "治愈": np.array([0.675, 0.600, 0.400, 0.500, 0.550]),
    "黑暗": np.array([0.575, 0.550, 0.525, 0.625, 0.625]),
    "废土": np.array([0.475, 0.375, 0.300, 0.750, 0.750]),
    "电影": np.array([0.675, 0.675, 0.625, 0.575, 0.575]),
}

WHS_LEVELS = [
    (90, "优秀 — 接近专业录音水平"),
    (75, "良好 — 存在可识别但轻微的缺陷"),
    (60, "一般 — 存在明显的声学问题"),
    (40, "较差 — 多个维度存在中等以上缺陷"),
    (0,  "严重缺陷 — 原始音频质量极低"),
]

EDS_LEVELS = [
    (90, "优秀 — 处理后波场非常接近目标情绪的理想状态"),
    (75, "良好 — 显著向目标方向移动"),
    (60, "有效 — 有明显改善但未完全达到目标"),
    (40, "轻微改善 — 方向正确但效果有限"),
    (0,  "无明显改善或方向错误 — 需更换工艺链"),
]


class HealthScorer:
    """WHS + EDS 评分器 (SPEC §6.1-§6.2)"""

    def __init__(self, dimension_weights: dict | None = None):
        self.weights = dimension_weights or DIMENSION_WEIGHTS
        self._classifier = DefectClassifier()

    # ——— WHS ————————————————————————————————

    def compute_whs(self, ws: WaveStateDiagnosis,
                    defects: list[Defect] | None = None) -> dict:
        """
        计算波场健康分 (WHS)

        Args:
            ws: 18 参数诊断状态
            defects: 预分类的缺陷列表 (可选, 若为 None 则自动分类)

        Returns:
            {"WHS": float, "level": str, "dim_scores": dict, "defect_count": int}
        """
        if defects is None:
            defects = self._classifier.classify(ws)

        dim_scores = {}
        for dim_name in self.weights:
            severity_sum = self._classifier.get_dimension_severity_sum(defects, dim_name)
            dim_scores[dim_name] = 100.0 * (1.0 - severity_sum)

        whs = sum(self.weights[dim] * dim_scores[dim] for dim in self.weights)
        whs = max(0.0, min(100.0, whs))

        level_desc = "一般"
        for threshold, desc in WHS_LEVELS:
            if whs >= threshold:
                level_desc = desc
                break

        return {
            "WHS": round(whs, 1),
            "level": level_desc.split(" —")[0] if " —" in level_desc else level_desc,
            "level_desc": level_desc,
            "dim_scores": {dim: round(score, 1) for dim, score in dim_scores.items()},
            "defect_count": len(defects),
        }

    # ——— EDS ————————————————————————————————

    def compute_eds(self,
                    ws_raw: WaveStateDiagnosis,
                    ws_processed: WaveStateDiagnosis,
                    emotion_target: str,
                    target_vec: np.ndarray | None = None) -> float:
        """
        计算情绪显影分 (EDS)

        Args:
            ws_raw: 处理前的诊断状态
            ws_processed: 处理后的诊断状态
            emotion_target: 目标情绪名 (包含情绪关键词, 如 "温柔觉醒")

        Returns:
            float [-100, 100]. Positive = closer to target, negative = further from target.
        """
        if target_vec is None:
            target_vec = self._get_ideal_vector(emotion_target)

        raw_vec = self._diagnosis_to_process_vector(ws_raw)
        processed_vec = self._diagnosis_to_process_vector(ws_processed)

        dist_raw = np.linalg.norm(raw_vec - target_vec)
        dist_processed = np.linalg.norm(processed_vec - target_vec)

        if dist_raw < 1e-9:
            return 50.0

        norm_dist = dist_processed / dist_raw
        eds = 100.0 * (1.0 - norm_dist)
        return round(max(-100.0, min(100.0, eds)), 1)

    def get_eds_level(self, eds: float) -> str:
        """EDS 数值 → 等级描述"""
        for threshold, desc in EDS_LEVELS:
            if eds >= threshold:
                return desc.split(" —")[0]
        return "无效"

    # ——— 辅助 ————————————————————————————————

    def _get_ideal_vector(self, emotion: str) -> np.ndarray:
        """根据情绪名/代码获取理想处理五维向量。支持中文名和2字符代码。"""
        # 尝试 emotion_targets 的精确查询 (支持 "GA", "DR" 等代码)
        try:
            from moodify.knowledge.emotion_targets import get_ideal_process_vector
            return get_ideal_process_vector(emotion)
        except Exception:
            pass
        # 回退: 中文子串匹配
        for key in EMOTION_IDEAL_VECTORS:
            if key in emotion:
                return EMOTION_IDEAL_VECTORS[key]
        return np.array([0.55, 0.55, 0.45, 0.55, 0.50])

    @staticmethod
    def _diagnosis_to_process_vector(ws: WaveStateDiagnosis) -> np.ndarray:
        """
        诊断五维 → 处理五维向量 [E, D, S, T, H] each in [0, 1]
        桥接映射 (SPEC §2.4)
        """
        s = ws.Spectrum
        d = ws.Dynamics
        sp = ws.Space
        layers = ws.Layers
        e = ws.Emotion

        # E: S3_MidClarity 主导, S5_SpectralTilt 惩戒
        tilt_abs = abs(s.S5_SpectralTilt.value)
        tilt_penalty = min(tilt_abs / 12.0, 1.0)
        E = max(0.0, min(1.0, s.S3_MidClarity.value * 0.7 + (1.0 - tilt_penalty) * 0.3))

        # D: D1_LRA 主导, range [2, 16] → [0, 1]
        D = max(0.0, min(1.0, (d.D1_LRA.value - 2.0) / 14.0))

        # S: SP1_Correlation 反比 + SP3_RT60 惩戒
        corr_score = max(0.0, min(1.0, 1.0 - sp.SP1_Correlation.value))
        rt60_penalty = min(sp.SP3_RT60Consist.value / 0.8, 1.0)
        S = max(0.0, min(1.0, corr_score * 0.7 + (1.0 - rt60_penalty) * 0.3))

        # T: L3_DrumDetect 主导
        T = max(0.0, min(1.0, layers.L3_DrumDetect.value * 1.1))

        # H: E3_FatigueRisk 反比
        H = max(0.0, min(1.0, 1.0 - e.E3_FatigueRisk.value / 120.0))

        return np.array([E, D, S, T, H])

    @staticmethod
    def compute_delta(ws_before: dict, ws_after: dict) -> dict:
        """计算处理前后状态差 (用于 A/B 对比报告)"""
        delta = {}
        for key in ws_before:
            if key in ws_after and isinstance(ws_before[key], (int, float)):
                delta[key] = round(ws_after[key] - ws_before[key], 3)
        return delta

    def evaluate_processing(self,
                            ws_raw: WaveStateDiagnosis,
                            ws_processed: WaveStateDiagnosis,
                            emotion_target: str) -> dict:
        """
        综合评估: WHS 变化 + EDS + 缺陷变化

        Returns:
            {
                "whs_before": float,
                "whs_after": float,
                "whs_delta": float,
                "eds": float,
                "eds_level": str,
                "defects_before": int,
                "defects_after": int,
                "verdict": str,
            }
        """
        defects_before = self._classifier.classify(ws_raw, emotion_target)
        defects_after = self._classifier.classify(ws_processed, emotion_target)

        whs_before = self.compute_whs(ws_raw, defects_before)
        whs_after = self.compute_whs(ws_processed, defects_after)
        eds = self.compute_eds(ws_raw, ws_processed, emotion_target)

        whs_delta = whs_after["WHS"] - whs_before["WHS"]

        if whs_delta >= 5 and eds >= 60:
            verdict = "GOOD — WHS 和 EDS 均显著改善"
        elif whs_delta >= 0 and eds >= 40:
            verdict = "OK — 有改善但不够显著"
        elif whs_delta < -5:
            verdict = "REGRESSION — WHS 下降，建议回滚"
        else:
            verdict = "WEAK — 改动不明显"

        return {
            "whs_before": whs_before["WHS"],
            "whs_after": whs_after["WHS"],
            "whs_delta": round(whs_delta, 1),
            "eds": eds,
            "eds_level": self.get_eds_level(eds),
            "defects_before": len(defects_before),
            "defects_after": len(defects_after),
            "verdict": verdict,
        }
