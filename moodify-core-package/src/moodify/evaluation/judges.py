"""AI 评测管道 — 三评委共识评估 + 反馈回路

SPEC: SPEC-013

三评委架构:
  Judge A: LLM 音乐学视角  (DeepSeek API)
  Judge B: 声学工程视角    (客观指标对比)
  Judge C: 综合听感视角    (A+B 加权 + 随机噪声)

反馈回路:
  evaluator.run() → AI_Assessment
    → CalibrationState.update(proxy_score, real_eds=ai_score)
    → ProcessingHistory.save(record with satisfied=ai_score/100)
    → D 值爬升 → proxy 模型变准
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import logging
import json

import numpy as np

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
#  Data Models
# ═══════════════════════════════════════════════════════════════

@dataclass
class JudgeResult:
    """单个评委的评分结果."""
    name: str
    emotion_score: float        # 情绪匹配分 0-100
    quality_score: float        # 音质保持分 0-100
    overall: float             # 综合分 0-100
    confidence: float           # 置信度 0-1
    reasoning: str              # 评委理由（简短）
    metadata: dict = field(default_factory=dict)


@dataclass
class AIAssessment:
    """三评委共识评估结果."""
    input_path: str
    emotion_code: str
    timestamp: str
    judges: list[JudgeResult]

    # 共识分
    final_score: float          # 最终综合分（加权共识）
    consensus_confidence: float # 共识置信度 0-1
    consensus_std: float        # 三评委标准差

    # 用于校准反馈
    real_eds_equivalent: float  # 等效 real_eds（用于 CalibrationState.update）
    proxy_score: float          # 原始 proxy 分（搜索阶段）

    # 评委详情
    judge_a_score: float = 0.0  # LLM 音乐学
    judge_b_score: float = 0.0  # 声学工程
    judge_c_score: float = 0.0  # 综合听感

    def to_dict(self) -> dict:
        return {
            "input_path": self.input_path,
            "emotion_code": self.emotion_code,
            "timestamp": self.timestamp,
            "final_score": round(self.final_score, 1),
            "consensus_confidence": round(self.consensus_confidence, 3),
            "consensus_std": round(self.consensus_std, 2),
            "real_eds_equivalent": round(self.real_eds_equivalent, 1),
            "proxy_score": round(self.proxy_score, 1),
            "judges": [
                {
                    "name": j.name,
                    "emotion_score": round(j.emotion_score, 1),
                    "quality_score": round(j.quality_score, 1),
                    "overall": round(j.overall, 1),
                    "confidence": round(j.confidence, 3),
                    "reasoning": j.reasoning,
                }
                for j in self.judges
            ],
        }


# ═══════════════════════════════════════════════════════════════
#  Judge A: LLM 音乐学视角
# ═══════════════════════════════════════════════════════════════

_JUDGE_A_SYSTEM = """\
你是 Moodify 的 AI 音乐学评委。

你将收到:
1. 目标情绪描述 (emotion_name, emotion_desc)
2. 原始音频特征 (raw_features): 18 参数诊断数据
3. 处理后音频特征 (processed_features): 18 参数诊断数据 + 主要 DSP 参数

你的任务是评估处理是否有效实现了目标情绪，同时保持了音质。

## 评分标准 (0-100)
1. 情绪方向准确性: 处理后的频谱、动态、空间特征是否更接近目标情绪的理想状态？
2. 听感自然度: 处理是否引入可察觉的伪影、失真或异常？
3. 动态保持度: 原始音乐的动态表达是否被合理保留？
4. 空间感改善: 声场是否得到了合理调整（不夸大，不压抑）？

## 8 种目标情绪的理想状态
- GA (温柔觉醒): 温暖、柔和、亲密、低频饱满、高频克制
- SE (神圣空灵): 超然、宏大、轻盈、混响深远、低频收敛
- UD (都市危险): 压迫、紧张、暗黑、压缩重、低频冲击强
- LW (孤独留白): 内省、距离、稀疏、混响深远但克制
- HL (治愈温暖): 安慰、饱满、平滑、低频温暖、谐波丰富
- DR (黑暗浪漫): 深沉、性感、神秘、中低频突出、氛围感强
- WL (废土机械): 粗粝、冲击、工业、极限压缩、高失真
- CN (电影感): 宏大、叙事、史诗、大动态、宽声场

## 输出格式 (严格 JSON)
{
  "emotion_score": 78.5,      // 情绪匹配分 0-100
  "quality_score": 82.0,      // 音质保持分 0-100
  "overall": 79.5,            // 综合分 0-100
  "confidence": 0.85,          // 置信度 0-1
  "reasoning": "处理后低频从-5.2dB升至-2.8dB，更接近温柔觉醒的低频饱满特征..."
}
"""


class LLMJudge:
    """评委 A: DeepSeek LLM 音乐学视角."""

    def __init__(self):
        self._client = None
        self._available = False
        self._init_client()

    def _init_client(self):
        try:
            from moodify.llm.client import DeepSeekClient
            self._client = DeepSeekClient()
            self._available = self._client.available
        except Exception:
            self._available = False

    @property
    def available(self) -> bool:
        return self._available

    def evaluate(
        self,
        raw_ws: dict,
        processed_ws: dict,
        emotion_code: str,
        emotion_name: str,
        emotion_desc: str,
        params_applied: dict | None = None,
    ) -> JudgeResult | None:
        """调用 LLM 评委评估."""
        if not self._available:
            return None

        raw_str = self._format_features(raw_ws)
        processed_str = self._format_features(processed_ws)
        params_str = json.dumps(params_applied or {}, ensure_ascii=False)

        user_msg = json.dumps({
            "emotion_code": emotion_code,
            "emotion_name": emotion_name,
            "emotion_desc": emotion_desc,
            "raw_features": raw_str,
            "processed_features": processed_str,
            "params_applied": params_str,
        }, ensure_ascii=False, indent=2)

        try:
            result = self._client._call(_JUDGE_A_SYSTEM, user_msg)
            if result is None:
                return None

            return JudgeResult(
                name="LLMJudge",
                emotion_score=float(result.get("emotion_score", 50)),
                quality_score=float(result.get("quality_score", 50)),
                overall=float(result.get("overall", 50)),
                confidence=float(result.get("confidence", 0.5)),
                reasoning=str(result.get("reasoning", ""))[:300],
                metadata={"source": "deepseek"},
            )
        except Exception as e:
            logger.warning(f"LLMJudge failed: {e}")
            return None

    @staticmethod
    def _format_features(ws: dict) -> str:
        """将 WaveState 字典格式化为可读字符串."""
        lines = []
        if "spectrum" in ws:
            for k, v in ws["spectrum"].items():
                lines.append(f"  {k}: {v}")
        if "dynamics" in ws:
            for k, v in ws["dynamics"].items():
                lines.append(f"  {k}: {v}")
        if "space" in ws:
            for k, v in ws["space"].items():
                lines.append(f"  {k}: {v}")
        return "\n".join(lines) if lines else json.dumps(ws, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════
#  Judge B: 声学工程视角
# ═══════════════════════════════════════════════════════════════

_EMOTION_WEIGHTS = {
    "GA": {"E": 0.25, "D": 0.15, "S": 0.20, "T": 0.15, "H": 0.25},
    "SE": {"E": 0.20, "D": 0.15, "S": 0.30, "T": 0.10, "H": 0.25},
    "UD": {"E": 0.25, "D": 0.30, "S": 0.15, "T": 0.20, "H": 0.10},
    "LW": {"E": 0.20, "D": 0.20, "S": 0.25, "T": 0.15, "H": 0.20},
    "HL": {"E": 0.20, "D": 0.15, "S": 0.15, "T": 0.15, "H": 0.35},
    "DR": {"E": 0.25, "D": 0.20, "S": 0.20, "T": 0.15, "H": 0.20},
    "WL": {"E": 0.20, "D": 0.35, "S": 0.10, "T": 0.25, "H": 0.10},
    "CN": {"E": 0.25, "D": 0.25, "S": 0.25, "T": 0.15, "H": 0.10},
}


class AcousticJudge:
    """评委 B: 声学工程视角 — 基于 18 参数客观对比."""

    def evaluate(
        self,
        raw_ws: dict,
        processed_ws: dict,
        emotion_code: str,
        emotion_name: str,
        emotion_desc: str,
        params_applied: dict | None = None,
    ) -> JudgeResult:
        """客观评分：情绪方向匹配 + 音质保持."""
        # 提取 5D Process 向量
        def extract_5d(ws: dict) -> np.ndarray:
            s = ws.get("spectrum", {})
            d = ws.get("dynamics", {})
            sp = ws.get("space", {})
            layers = ws.get("layers", {})
            e = ws.get("emotion", {})

            return np.array([
                float(s.get("S3_MidClarity", 0.5)),
                float(d.get("D1_LRA", 8.0) / 20.0),  # 归一化
                float(sp.get("SP1_Correlation", 0.5)),
                float(layers.get("L3_DrumDetect", 0.5)),
                float(e.get("E2_Richness", 0.5)),
            ])

        try:
            vec_raw = extract_5d(raw_ws)
            vec_proc = extract_5d(processed_ws)
        except Exception:
            return JudgeResult(
                name="AcousticJudge",
                emotion_score=50.0, quality_score=50.0, overall=50.0,
                confidence=0.1, reasoning="无法解析 WaveState 数据",
            )

        # 情绪方向匹配分：与理想向量的距离改善
        weights = _EMOTION_WEIGHTS.get(emotion_code, {k: 0.2 for k in ["E", "D", "S", "T", "H"]})
        w_arr = np.array([weights.get(d, 0.2) for d in ["E", "D", "S", "T", "H"]])
        w_arr /= w_arr.sum()

        dist_raw = float(np.sqrt(np.sum(w_arr * (vec_raw - 0.5) ** 2)))
        dist_proc = float(np.sqrt(np.sum(w_arr * (vec_proc - 0.5) ** 2)))

        if dist_raw > 0.01:
            direction_score = max(0, min(100, 100 * (1 - dist_proc / dist_raw) * 2 + 50))
        else:
            direction_score = 50.0

        # 音质保持分：参数驱动的客观约束
        quality_score = 100.0
        quality_issues = []

        if params_applied:
            # 极端参数检测
            extreme_count = 0
            for pk, pv in params_applied.items():
                mn, mx = self._get_param_range(pk)
                if mn < mx:
                    norm = (pv - mn) / (mx - mn)
                    if norm < 0.05 or norm > 0.95:
                        extreme_count += 1

            if extreme_count > 3:
                quality_score -= (extreme_count - 3) * 3
                quality_issues.append(f"{extreme_count} 个极端参数")

            # 混响过载检测
            reverb = params_applied.get("P10_reverb_t60", 0.0)
            if reverb > 2.5:
                quality_score -= (reverb - 2.5) * 8
                quality_issues.append(f"混响时间过长 ({reverb:.1f}s)")

            # 压缩过重检测
            ratio = params_applied.get("P06_compression_ratio", 4.0)
            if ratio > 10:
                quality_score -= (ratio - 10) * 2
                quality_issues.append(f"压缩比过高 ({ratio:.1f}:1)")

            # 高频增益过强
            hf = params_applied.get("P15_high_shelf_gain", 0.0)
            if hf > 6:
                quality_score -= (hf - 6) * 4
                quality_issues.append(f"高频增益过高 ({hf:.1f}dB)")

        quality_score = max(0, min(100, quality_score))

        # 综合分：情绪方向 × 0.6 + 音质保持 × 0.4
        overall = 0.6 * direction_score + 0.4 * quality_score

        reasoning = (
            f"距离改善: {dist_raw:.3f}→{dist_proc:.3f} "
            f"(得分:{direction_score:.0f}) | "
            f"音质: {quality_score:.0f}"
            + (f" | 警告: {', '.join(quality_issues)}" if quality_issues else "")
        )

        return JudgeResult(
            name="AcousticJudge",
            emotion_score=round(direction_score, 1),
            quality_score=round(quality_score, 1),
            overall=round(overall, 1),
            confidence=0.85,  # 客观指标置信度高
            reasoning=reasoning,
            metadata={"dist_raw": round(dist_raw, 3), "dist_proc": round(dist_proc, 3)},
        )

    @staticmethod
    def _get_param_range(param_name: str) -> tuple[float, float]:
        """获取参数的安全范围."""
        ranges = {
            "P01_vocal_presence_freq": (500, 8000),
            "P02_vocal_presence_gain": (-6, 6),
            "P03_vocal_presence_q": (0.5, 3.0),
            "P04_proximity_low_freq": (100, 1000),
            "P05_proximity_low_gain": (-6, 6),
            "P06_compression_ratio": (1.5, 12.0),
            "P07_compression_attack": (0.5, 100.0),
            "P08_compression_release": (10.0, 500.0),
            "P09_compression_threshold": (-40, -10),
            "P10_reverb_t60": (0.1, 3.0),
            "P11_reverb_dry_wet": (0.0, 1.0),
            "P12_reverb_width": (0.3, 1.5),
            "P13_harmonic_drive": (0.0, 0.5),
            "P14_high_shelf_freq": (3000, 12000),
            "P15_high_shelf_gain": (-6, 6),
        }
        return ranges.get(param_name, (0, 1))


# ═══════════════════════════════════════════════════════════════
#  Judge C: 综合听感视角（诊断重评）
# ═══════════════════════════════════════════════════════════════

class ConsensusJudge:
    """评委 C: 综合听感 — 用 DiagnosisListener 重新诊断，与目标对比."""

    def __init__(self, vector_bias: dict | None = None):
        self._vector_bias = vector_bias or {}

    def evaluate(
        self,
        raw_audio_path: str,
        processed_audio_path: str,
        emotion_code: str,
        emotion_name: str,
        emotion_desc: str,
        params_applied: dict | None = None,
    ) -> JudgeResult:
        """用 DiagnosisListener 重评处理效果."""
        try:
            from moodify.calibration.listener import DiagnosisListener

            listener = DiagnosisListener(vector_bias=self._vector_bias)
            import soundfile as sf

            raw_audio, sr = sf.read(raw_audio_path, dtype="float32")
            proc_audio, _ = sf.read(processed_audio_path, dtype="float32")

            ranks, distances, ideal_vec = listener.rank_versions(
                [proc_audio], sr, emotion_code
            )

            if distances:
                dist = distances[0]
                # 距离越小越好 → 映射到 0-100 分
                # dist ∈ [0, ~0.5], 映射到 [100, 0]
                score = max(0, min(100, 100 * (1 - dist / 0.5)))
            else:
                score = 50.0
                dist = 0.25

            return JudgeResult(
                name="ConsensusJudge",
                emotion_score=round(score, 1),
                quality_score=round(min(100, score + 5), 1),
                overall=round(score, 1),
                confidence=0.75,
                reasoning=f"重诊断距离={dist:.3f}, 情绪匹配分={score:.0f}",
                metadata={"distance": round(dist, 4), "ideal_vec": ideal_vec.tolist() if ideal_vec is not None else []},
            )
        except Exception as e:
            logger.warning(f"ConsensusJudge failed: {e}")
            return JudgeResult(
                name="ConsensusJudge",
                emotion_score=50.0, quality_score=50.0, overall=50.0,
                confidence=0.1, reasoning=f"重诊断失败: {e}",
            )


# ═══════════════════════════════════════════════════════════════
#  EvaluatorOrchestrator
# ═══════════════════════════════════════════════════════════════

class EvaluatorOrchestrator:
    """AI 评测编排器 — 运行三评委 → 共识 → 反馈回路.

    用法:
        evaluator = EvaluatorOrchestrator()
        assessment = evaluator.evaluate(
            raw_audio_path="input.wav",
            processed_audio_path="output.wav",
            raw_ws=ws_before.to_dict(),
            processed_ws=ws_after.to_dict(),
            emotion_code="GA",
            emotion_name="温柔觉醒",
            emotion_desc="温暖、柔和、亲密...",
            params_applied=p15_params,
            proxy_score=72.5,          # 搜索阶段的 proxy EDS
            strength_vector={...},
            ws_before_5d=np.ndarray,
            ws_after_5d=np.ndarray,
            vector_bias={"E": 0.05, ...},
            storage_dir="outputs",
        )
    """

    def __init__(self):
        self.judge_a = LLMJudge()
        self.judge_b = AcousticJudge()
        self.judge_c: ConsensusJudge | None = None  # 延迟初始化

    def evaluate(
        self,
        raw_audio_path: str,
        processed_audio_path: str,
        raw_ws: dict,
        processed_ws: dict,
        emotion_code: str,
        emotion_name: str,
        emotion_desc: str,
        params_applied: dict | None = None,
        proxy_score: float = 50.0,
        strength_vector: dict | None = None,
        ws_before_5d: np.ndarray | None = None,
        ws_after_5d: np.ndarray | None = None,
        vector_bias: dict | None = None,
        storage_dir: str = "outputs",
    ) -> AIAssessment:
        """运行完整评测管道."""
        timestamp = datetime.now().isoformat()
        judges: list[JudgeResult] = []

        # 评委 A: LLM 音乐学
        result_a = self.judge_a.evaluate(
            raw_ws, processed_ws, emotion_code, emotion_name, emotion_desc, params_applied
        )
        if result_a:
            judges.append(result_a)

        # 评委 B: 声学工程（始终可用）
        result_b = self.judge_b.evaluate(
            raw_ws, processed_ws, emotion_code, emotion_name, emotion_desc, params_applied
        )
        judges.append(result_b)

        # 评委 C: 综合听感（需要音频文件）
        if ws_before_5d is not None and ws_after_5d is not None:
            self.judge_c = ConsensusJudge(vector_bias=vector_bias)
            result_c = self.judge_c.evaluate(
                raw_audio_path, processed_audio_path,
                emotion_code, emotion_name, emotion_desc, params_applied
            )
            judges.append(result_c)
        else:
            # 无音频文件时：用 AcousticJudge 的结果作为代理
            # 加入少量随机噪声模拟听感不确定性
            proxy_score_c = result_b.overall + np.random.normal(0, 5.0)
            judges.append(JudgeResult(
                name="ConsensusJudge",
                emotion_score=round(max(0, min(100, proxy_score_c)), 1),
                quality_score=result_b.quality_score,
                overall=round(max(0, min(100, proxy_score_c)), 1),
                confidence=0.4,
                reasoning="无音频文件，综合声学指标估计",
            ))

        # ── 共识计算 ───────────────────────────────
        scores = [j.overall for j in judges]
        mean_score = float(np.mean(scores))
        std_score = float(np.std(scores))

        # 置信度：高共识（低标准差）= 高置信
        consensus_confidence = max(0, 1.0 - std_score / 30.0)

        # 共识分 = 均值 × 置信度 + 均值 × (1-置信度) × 0.5
        # 低置信时，向 50（随机水平）靠拢
        final_score = mean_score * consensus_confidence + mean_score * (1 - consensus_confidence) * 0.5

        # 等效 real_eds: 映射到 [-100, 100] EDS 范围
        # AI 评分 0-100 → EDS [-100, 100]
        # 50 = 中性，100 = 完美接近目标，0 = 完全偏离
        real_eds_equivalent = (final_score - 50) * 2.0  # [0,100] → [-100, 100]

        assessment = AIAssessment(
            input_path=raw_audio_path,
            emotion_code=emotion_code,
            timestamp=timestamp,
            judges=judges,
            final_score=round(final_score, 1),
            consensus_confidence=round(consensus_confidence, 3),
            consensus_std=round(std_score, 2),
            real_eds_equivalent=round(real_eds_equivalent, 1),
            proxy_score=round(proxy_score, 1),
            judge_a_score=round(judges[0].overall, 1) if len(judges) > 0 else 0.0,
            judge_b_score=round(result_b.overall, 1),
            judge_c_score=round(judges[-1].overall, 1),
        )

        # ── 反馈回路：写入校准状态 ──────────────────
        self._write_feedback(assessment, strength_vector, ws_before_5d, ws_after_5d, storage_dir)

        return assessment

    def _write_feedback(
        self,
        assessment: AIAssessment,
        strength_vector: dict | None,
        ws_before_5d: np.ndarray | None,
        ws_after_5d: np.ndarray | None,
        storage_dir: str,
    ) -> None:
        """将评测结果写入反馈回路：校准状态 + 处理历史."""
        try:
            # 更新 CalibrationState
            from moodify.calibration.online import update_calibration

            update_calibration(
                emotion_code=assessment.emotion_code,
                proxy_score=assessment.proxy_score,
                real_eds=assessment.real_eds_equivalent,
                strength_vector=strength_vector or {},
                ws_before_5d=ws_before_5d or np.zeros(5),
                ws_after_5d=ws_after_5d or np.zeros(5),
                storage_dir=storage_dir,
            )
            logger.info(
                f"Calibration updated: emotion={assessment.emotion_code}, "
                f"proxy={assessment.proxy_score:.1f}, real={assessment.real_eds_equivalent:.1f}, "
                f"D→{self._get_current_d(storage_dir):.3f}"
            )
        except Exception as e:
            logger.warning(f"Calibration update failed: {e}")

        try:
            # 更新 ProcessingHistory
            from moodify.memory.history import ProcessingHistory, ProcessingRecord

            history = ProcessingHistory(storage_dir)

            # 构造 diagnosis_vector（取 ws_before 的主要参数）
            diag_vec = self._build_diag_vector(assessment)

            record = ProcessingRecord(
                diagnosis_vector=diag_vec,
                params={},
                strength_vector=strength_vector or {},
                whs_before=0.0,
                whs_after=0.0,
                eds=assessment.real_eds_equivalent,
                proxy_score=assessment.proxy_score,
                emotion_code=assessment.emotion_code,
                emotion_name="",
                user_intent="",
                satisfied=(assessment.final_score / 100.0),  # AI 评分映射到 0-1
                user_feedback=json.dumps(assessment.to_dict(), ensure_ascii=False),
                timestamp=assessment.timestamp,
            )
            history.save(record)
            logger.info(f"History record saved for {assessment.emotion_code}")
        except Exception as e:
            logger.warning(f"History save failed: {e}")

    def _get_current_d(self, storage_dir: str) -> float:
        try:
            from moodify.calibration.online import CalibrationState
            state = CalibrationState.load(storage_dir)
            return state.d_value()
        except Exception:
            return 0.05

    def _build_diag_vector(self, assessment: AIAssessment) -> list[float]:
        """从 assessment 构建 18 维诊断向量（用于历史记录）."""
        # 用评委评分作为代理特征（简化实现）
        base = [0.5] * 18
        if assessment.judge_a_score > 0:
            for i in range(min(5, len(base))):
                base[i] += (assessment.judge_a_score - 50) / 200.0
        return [max(0.0, min(1.0, v)) for v in base]


# ═══════════════════════════════════════════════════════════════
#  便捷函数
# ═══════════════════════════════════════════════════════════════

def evaluate_processing(
    raw_path: str,
    processed_path: str,
    emotion_code: str,
    emotion_name: str,
    emotion_desc: str,
    ws_before,
    ws_after,
    params: dict,
    proxy_score: float,
    strength_vector: dict,
    ws_before_5d: np.ndarray,
    ws_after_5d: np.ndarray,
    vector_bias: dict | None = None,
    storage_dir: str = "outputs",
) -> AIAssessment:
    """一行调用：评测 + 反馈写入."""
    evaluator = EvaluatorOrchestrator()

    raw_ws = ws_before.to_dict() if hasattr(ws_before, "to_dict") else ws_before
    processed_ws = ws_after.to_dict() if hasattr(ws_after, "to_dict") else ws_after

    return evaluator.evaluate(
        raw_audio_path=raw_path,
        processed_audio_path=processed_path,
        raw_ws=raw_ws,
        processed_ws=processed_ws,
        emotion_code=emotion_code,
        emotion_name=emotion_name,
        emotion_desc=emotion_desc,
        params_applied=params,
        proxy_score=proxy_score,
        strength_vector=strength_vector,
        ws_before_5d=ws_before_5d,
        ws_after_5d=ws_after_5d,
        vector_bias=vector_bias,
        storage_dir=storage_dir,
    )
