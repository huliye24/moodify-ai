"""
craft_chain_match.py — CraftChainMatch 工艺链匹配算法 (SPEC §12)
=================================================================
5 子指标评分 + 硬阻断规则 + 动态权重更新。

MatchScore = 0.30*DefectCoverage + 0.30*EmotionTargetFit
           + 0.20*WaveStateCompatibility + 0.20*CraftReliability
           - 0.15*RiskScore

硬阻断:
  1. EmotionTargetFit == 0.0
  2. 缺陷匹配 contraindications
  3. 安全冲突
"""

import numpy as np
from dataclasses import dataclass

from moodify.data_types import CraftCardV2, WaveStateDiagnosis, EmotionTarget
from moodify.diagnosis.defect_classifier import Defect
from moodify.knowledge.emotion_targets import (
    get_emotion_target, get_safety_bounds, get_ideal_process_vector,
)
from moodify.diagnosis.health_scorer import HealthScorer


@dataclass
class MatchResult:
    craft_card: CraftCardV2
    score: float
    details: dict       # 五项子指标分解
    hard_blocked: bool = False
    block_reason: str = ""

    def __repr__(self):
        if self.hard_blocked:
            return f"MatchResult(BLOCKED: {self.block_reason})"
        return f"MatchResult({self.craft_card.craft_card_id}, score={self.score:.3f})"


class CraftChainMatch:
    """CraftChainMatch 工艺链匹配算法 (SPEC §12)"""

    def __init__(self, weights: dict | None = None):
        self.weights = weights or {
            "defect_coverage": 0.30,
            "emotion_fit": 0.30,
            "ws_compatibility": 0.20,
            "reliability": 0.20,
            "risk": 0.15,
        }
        self.alpha = 10.0  # 先验强度
        self._scorer = HealthScorer()

    def match(self,
              defects: list[Defect],
              emotion_target: str,
              ws_raw: WaveStateDiagnosis,
              craft_library: list[CraftCardV2],
              top_k: int = 3) -> list[MatchResult]:
        """返回 top_k 最佳匹配工艺卡"""
        candidates = []

        for card in craft_library:
            result = self._score_single(card, defects, emotion_target, ws_raw)
            if not result.hard_blocked:
                candidates.append(result)

        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates[:top_k]

    def _score_single(self, card, defects, emotion_target_str, ws_raw) -> MatchResult:
        emotion_fit = self._emotion_target_fit(card, emotion_target_str)
        if emotion_fit == 0.0:
            return MatchResult(card, 0.0, {}, True, "情绪完全不匹配")

        for defect in defects:
            for contra in card.diagnostic_markers.contraindications:
                if self._defect_matches_contra(defect, contra):
                    return MatchResult(card, 0.0, {}, True, f"禁忌症: {contra}")

        defect_cov = self._defect_coverage(card, defects)
        ws_compat = self._wave_state_compatibility(card, ws_raw, emotion_target_str)
        reliability = self._craft_reliability(card)
        risk = self._risk_score(card, defects, emotion_target_str)

        w = self.weights
        score = (
            w["defect_coverage"] * defect_cov
            + w["emotion_fit"] * emotion_fit
            + w["ws_compatibility"] * ws_compat
            + w["reliability"] * reliability
            - w["risk"] * risk
        )
        score = max(0.0, min(1.0, score))

        return MatchResult(craft_card=card, score=score, details={
            "defect_coverage": defect_cov,
            "emotion_fit": emotion_fit,
            "ws_compatibility": ws_compat,
            "reliability": reliability,
            "risk": risk,
        })

    # ——— 5 sub-metrics ————————————————————

    def _defect_coverage(self, card, defects) -> float:
        if len(defects) == 0:
            return 0.5
        common = card.diagnostic_markers.common_defects
        covered = 0
        for d in defects:
            for cd in common:
                if self._keyword_overlap(d.description_zh, cd):
                    covered += 1
                    break
        return covered / len(defects)

    def _emotion_target_fit(self, card, emotion_str: str) -> float:
        try:
            et = get_emotion_target(emotion_str)
        except KeyError:
            return 0.0
        ct_primary = card.target_emotion.primary
        if ct_primary == et["primary"]:
            return 1.0
        if et["primary"] in card.target_emotion.secondary:
            return 0.8
        if card.target_emotion.primary_class == et["primary_class"]:
            return 0.4
        return 0.0

    def _wave_state_compatibility(self, card, ws_raw,
                                   emotion_str: str) -> float:
        ws_vec = self._scorer._diagnosis_to_process_vector(ws_raw)
        try:
            ideal = get_ideal_process_vector(emotion_str)
            bounds = get_safety_bounds(emotion_str)
            radius = np.array([(hi - lo) / 2 for lo, hi in
                               [bounds["E"], bounds["D"], bounds["S"],
                                bounds["T"], bounds["H"]]])
        except KeyError:
            ideal = np.array([0.55, 0.55, 0.45, 0.55, 0.50])
            radius = np.ones(5) * 0.3

        dist = np.linalg.norm((ws_vec - ideal) / (radius + 1e-12))
        max_dist = np.sqrt(5) * 2
        return max(0.0, 1.0 - dist / max_dist)

    def _craft_reliability(self, card) -> float:
        cm = card.confidence_metrics
        n = cm.evidence_count
        return (
            min(n / 50.0, 1.0) * 0.5
            + cm.reproducibility * 0.3
            + cm.user_preference * 0.2
        )

    def _risk_score(self, card, defects, emotion_str: str) -> float:
        base = card.confidence_metrics.risk_incidence
        multiplier = 1.0
        for d in defects:
            for w in card.risk_warnings:
                if self._keyword_overlap(d.description_zh, w):
                    multiplier = 2.0
                    break
        return min(1.0, base * multiplier)

    # ——— Helpers ————————————————————

    @staticmethod
    def _keyword_overlap(text1: str, text2: str) -> bool:
        k1 = set(text1.replace("，", ",").replace("、", ",").split(","))
        k2 = set(text2.replace("，", ",").replace("、", ",").split(","))
        # Also check substring containment
        for a in k1:
            a = a.strip()
            if len(a) < 2:
                continue
            for b in k2:
                b = b.strip()
                if len(b) < 2:
                    continue
                if a in b or b in a:
                    return True
        return False

    @staticmethod
    def _defect_matches_contra(defect: Defect, contra: str) -> bool:
        return CraftChainMatch._keyword_overlap(defect.description_zh, contra)


def generate_craft_cards_from_data() -> list[CraftCardV2]:
    """从 C3 数据文件生成 8 张完整 CraftCardV2 (用于工艺库初始化)"""
    from moodify.knowledge.emotion_targets import EMOTION_TARGETS_V2
    from moodify.knowledge.craft_chains import CRAFT_CHAINS_15PARAMS, PARAM_KEYS
    from moodify.data_types import (
        CraftCardV2, ApplicableSources,
        DiagnosticMarkers, ProcessingStep, ParameterRange,
        ConfidenceMetrics, VersionEntry,
    )

    cards = []
    for emotion_key, target in EMOTION_TARGETS_V2.items():
        code = target["code"]
        chain = CRAFT_CHAINS_15PARAMS.get(code)
        if not chain:
            continue

        param_ranges = {}
        for pk in PARAM_KEYS:
            if pk in chain:
                p = chain[pk]
                param_ranges[pk] = ParameterRange(
                    min=p["min"], rec=p["rec"], max=p["max"], unit=p["unit"]
                )

        card = CraftCardV2(
            craft_card_id=f"CC-{code}-001",
            name_zh=target["name_cn"],
            name_en=target["name_en"],
            target_emotion=EmotionTarget(
                primary=target["primary"],
                secondary=target.get("secondary", []),
                intensity=0.7,
                primary_class=target.get("primary_class", ""),
            ),
            applicable_sources=ApplicableSources(**target.get("applicable_sources", {})),
            diagnostic_markers=DiagnosticMarkers(
                embryo_direction=target.get("embryo_direction", ""),
                common_defects=target.get("common_defects", []),
                contraindications=target.get("contraindications", []),
            ),
            processing_chain=[
                ProcessingStep(**s) for s in chain.get("processing_steps", [])
            ],
            parameter_ranges=param_ranges,
            risk_warnings=chain.get("risk_warnings", []),
            confidence_metrics=ConfidenceMetrics(),
            version_history=[
                VersionEntry(
                    version="1.0",
                    date="2026-05-27",
                    author="工川署",
                    changes="初始版本 - 基于 SPEC §13",
                )
            ],
        )
        cards.append(card)
    return cards
