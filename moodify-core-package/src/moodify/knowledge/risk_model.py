"""
risk_model.py — 完整三层风险模型 (SPEC §15)
=============================================
1. LFR (Listening Fatigue Risk) — 五因子听觉疲劳
2. ArtifactRisk — 伪影引入风险
3. EmotionDistortionRisk — 情感失真风险
4. TotalRisk — 复合风险 + 颜色等级 + 风险-收益决策
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional

from moodify.data_types import WaveStateDiagnosis
from moodify.knowledge.emotion_targets import get_emotion_target, get_ideal_process_vector
from moodify.diagnosis.health_scorer import HealthScorer


@dataclass
class RiskAssessment:
    """完整风险评估结果 (SPEC §15.5)"""
    lfr: float                                    # [0, 1]
    lfr_factors: dict                             # 五因子分解
    artifact_risk: float                          # [0, 1]
    artifact_factors: dict                        # 伪影子因子
    emotion_distortion: float                     # [0, 1]
    total_risk: float                             # [0, 1]
    level: str                                    # "green"/"yellow"/"orange"/"red"
    action: str                                   # "accept"/"warn"/"reduce"/"reject"
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class RiskModel:
    """完整三层风险模型 (SPEC §15)"""

    # 情绪风险容忍度 (§15.5)
    EMOTION_TOLERANCES = {
        "gentle_awakening": 0.3,
        "healing_warmth": 0.3,
        "sacred_ethereal": 0.4,
        "lonely_whitespace": 0.5,
        "cinematic": 0.5,
        "urban_danger": 0.65,
        "dark_romantic": 0.65,
        "wasteland_mechanical": 0.8,
    }

    def __init__(self):
        self._scorer = HealthScorer()
        self._lfr_factors_cache = {}
        self._artifact_factors_cache = {}

    # ——— Risk Assessment ————————————————————

    def assess(self,
               ws_raw: WaveStateDiagnosis,
               ws_processed: WaveStateDiagnosis,
               emotion_target: str,
               dsp_params: dict | None = None,
               separation_quality: dict | None = None,
               integrated_lufs: float | None = None) -> RiskAssessment:
        """完整风险评估 -> RiskAssessment"""

        lfr = self._compute_lfr(ws_processed, integrated_lufs)
        artifact = self._compute_artifact_risk(ws_raw, ws_processed,
                                                dsp_params, separation_quality)
        emotion_dist = self._compute_emotion_distortion(
            ws_raw, ws_processed, emotion_target)

        total = max(lfr, artifact, emotion_dist)

        # 获取该情绪的容忍度
        tolerance = self.EMOTION_TOLERANCES.get(emotion_target, 0.5)

        # 等级判定
        if total < tolerance:
            level, action = "green", "accept"
        elif total < tolerance + 0.3:
            level, action = "yellow", "warn"
        elif total < 0.8:
            level, action = "orange", "reduce"
        else:
            level, action = "red", "reject"

        warnings = self._generate_warnings(total, level, lfr, artifact,
                                            emotion_dist, ws_processed)
        recommendations = self._generate_recommendations(
            level, lfr, artifact, emotion_dist, ws_processed, dsp_params)

        return RiskAssessment(
            lfr=lfr,
            lfr_factors=self._lfr_factors_cache.copy(),
            artifact_risk=artifact,
            artifact_factors=self._artifact_factors_cache.copy(),
            emotion_distortion=emotion_dist,
            total_risk=total,
            level=level,
            action=action,
            warnings=warnings,
            recommendations=recommendations,
        )

    # ——— LFR: 五因子听觉疲劳 (§15.2) ————————

    def _compute_lfr(self, ws: WaveStateDiagnosis,
                     integrated_lufs: float | None = None) -> float:
        s = ws.Spectrum
        d = ws.Dynamics

        hfr = np.clip((s.S4_AirBand + 3.0) / 12.0, 0.0, 1.0)
        sibilance = self._estimate_sibilance(ws)
        lufs_val = integrated_lufs if integrated_lufs is not None else -14
        loudness_risk = np.clip((-10.0 - lufs_val) / 10.0, 0.0, 1.0)
        low_lra = np.clip((6.0 - d.D1_LRA) / 6.0, 0.0, 1.0)
        harsh = np.clip((d.D4_PLR - 6.0) / 12.0, 0.0, 1.0)

        self._lfr_factors_cache = {
            "HighFreqRoughness": round(hfr, 4),
            "SibilanceRisk": round(sibilance, 4),
            "IntegratedLoudnessRisk": round(loudness_risk, 4),
            "LowLRARisk": round(low_lra, 4),
            "HarshTransientRisk": round(harsh, 4),
        }

        return round(
            0.30 * hfr + 0.20 * sibilance + 0.20 * loudness_risk
            + 0.15 * low_lra + 0.15 * harsh, 4
        )

    @staticmethod
    def _estimate_sibilance(ws: WaveStateDiagnosis) -> float:
        s = ws.Spectrum
        presence_clarity = s.S3_MidClarity
        air_band = s.S4_AirBand
        risk = (1.0 - presence_clarity) * 0.5 + np.clip((air_band - 3) / 12.0, 0, 1) * 0.5
        return round(float(risk), 4)

    # ——— ArtifactRisk (§15.3) ————————————————

    def _compute_artifact_risk(self, ws_raw, ws_processed,
                                dsp_params=None, sep_quality=None) -> float:
        pumping = self._detect_pumping(dsp_params)
        phase = self._detect_phase_risk(dsp_params)
        harmonic = self._estimate_harmonic_dist(ws_processed, dsp_params)
        sep_artifact = self._estimate_sep_artifact(sep_quality)

        self._artifact_factors_cache = {
            "PumpingRisk": pumping,
            "PhaseShiftRisk": phase,
            "HarmonicDistRisk": harmonic,
            "SeparationArtifactRisk": sep_artifact,
        }
        return round(max(pumping, phase, harmonic, sep_artifact), 4)

    @staticmethod
    def _detect_pumping(dsp_params: dict | None) -> float:
        if not dsp_params:
            return 0.0
        ratio = dsp_params.get("compression_ratio", 2)
        release = dsp_params.get("compression_release", 150)
        if ratio > 4.0 and release < 50:
            return 0.8
        if ratio > 3.0 and release < 30:
            return 1.0
        if ratio > 2.0 and release < 20:
            return 0.3
        return 0.0

    @staticmethod
    def _detect_phase_risk(dsp_params: dict | None) -> float:
        if not dsp_params:
            return 0.0
        eq_params = ["vocal_presence_gain", "proximity_low_gain", "high_shelf_gain"]
        for key in eq_params:
            val = abs(dsp_params.get(key, 0))
            if val > 8:
                return 1.0
            if val > 6:
                return 0.5
        return 0.0

    @staticmethod
    def _estimate_harmonic_dist(ws: WaveStateDiagnosis,
                                 dsp_params: dict | None) -> float:
        if dsp_params:
            drive = dsp_params.get("harmonic_drive", 0)
            if drive > 0.6:
                return 0.8
            if drive > 0.4:
                return 0.4
        # 从诊断估算: 高频与中频比过高可能表示失真
        s = ws.Spectrum
        air_mid_ratio = abs(s.S4_AirBand / max(abs(s.S2_BassWarmth), 0.1))
        return float(np.clip(air_mid_ratio / 8.0, 0.0, 1.0))

    @staticmethod
    def _estimate_sep_artifact(sep_quality: dict | None) -> float:
        if not sep_quality:
            return 0.0
        min_sdr = sep_quality.get("min_sdr", 999)
        return float(np.clip(1.0 - min_sdr / 8.0, 0.0, 1.0))

    # ——— EmotionDistortionRisk (§15.4) ———————

    def _compute_emotion_distortion(self,
                                     ws_raw: WaveStateDiagnosis,
                                     ws_processed: WaveStateDiagnosis,
                                     emotion_target: str) -> float:
        try:
            ideal = get_ideal_process_vector(emotion_target)
        except KeyError:
            ideal = np.array([0.55, 0.55, 0.45, 0.55, 0.50])

        raw_vec = self._scorer._diagnosis_to_process_vector(ws_raw)
        proc_vec = self._scorer._diagnosis_to_process_vector(ws_processed)

        dist_raw = np.linalg.norm(raw_vec - ideal)
        if dist_raw < 1e-9:
            return 0.5

        dist_processed = np.linalg.norm(proc_vec - ideal)
        edr = dist_processed / dist_raw
        return round(min(1.0, edr), 4)

    # ——— Warnings & Recommendations ———————

    def _generate_warnings(self, total, level, lfr, artifact,
                            emotion_dist, ws) -> list[str]:
        w = []
        factors = self._lfr_factors_cache
        if factors.get("HighFreqRoughness", 0) > 0.5:
            w.append("高频粗糙度偏高 -> 降低 high_shelf_gain 或升高 high_shelf_freq")
        if factors.get("LowLRARisk", 0) > 0.5:
            w.append("动态过平 -> 降低 compression_ratio")
        if factors.get("SibilanceRisk", 0) > 0.5:
            w.append("齿音风险偏高 -> 考虑 DeEsser 或降低 presence gain")
        if level == "red":
            w.append(f"风险评分 {total:.2f} 达到红色级别, 强烈建议回滚")
        elif level == "orange":
            w.append(f"风险评分 {total:.2f} 较高, 建议减少处理强度")
        return w

    def _generate_recommendations(self, level, lfr, artifact,
                                   emotion_dist, ws, dsp_params) -> list[str]:
        recs = []
        if level == "red":
            recs.append("建议回滚处理, 更换工艺链或降低处理强度")
        elif level == "orange":
            recs.append("建议降低 compression_ratio 和 harmonic_drive")
            recs.append("考虑分批轻处理 (SPEC §10.4)")
        if self._artifact_factors_cache.get("PumpingRisk", 0) > 0.5:
            recs.append("检测到泵送效应 -> 增加 release 时间到 > 50ms 或降低 ratio")
        if self._artifact_factors_cache.get("PhaseShiftRisk", 0) > 0.5:
            recs.append("EQ 增益过大 -> 分批轻处理, 每轮 <= 3dB")
        return recs


class RiskBenefitDecider:
    """风险-收益决策器 (SPEC §15.5)"""

    def __init__(self, lambda_val: float = 1.5):
        self.lambda_val = lambda_val

    def decide(self, delta_eds: float,
               delta_risk: float) -> tuple[bool, str]:
        """
        dEmotionScore < lambda * dRisk -> reject

        Returns:
            (accepted: bool, reason: str)
        """
        if delta_risk <= 0:
            return True, "风险未增加, 接受处理"
        if delta_eds >= self.lambda_val * delta_risk:
            return True, f"情绪收益 ({delta_eds:.3f}) >= {self.lambda_val} x 风险增加 ({delta_risk:.3f})"
        return False, f"情绪收益 ({delta_eds:.3f}) < {self.lambda_val} x 风险增加 ({delta_risk:.3f}), 拒绝处理"
