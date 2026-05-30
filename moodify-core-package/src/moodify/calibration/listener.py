"""校准实验 — AI 听者抽象 + DiagnosisListener 实现。

三层过滤:
  Layer 1: 可辨性检测 — 两个版本的 5D WS 距离是否 > 阈值
  Layer 2: 方向偏好 — 哪个版本更接近目标情绪的理想向量
  Layer 3: 冲突检测 — AI 排名 vs 代理排名, 标记不一致样本
"""

from __future__ import annotations

import abc
import numpy as np


class AudioListener(abc.ABC):
    """AI 听者抽象 — 对处理后的音频版本做排序判断。

    不同实现:
      DiagnosisListener: 用 Moodify 诊断引擎重新测量 (始终可用)
      GeminiAudioListener: Gemini 2.5 Pro 音频输入 (需要 API key, 未来实现)
    """

    @abc.abstractmethod
    def name(self) -> str:
        """听者名称, 用于报告标识。"""
        ...

    @abc.abstractmethod
    def is_discriminable(
        self, audios: list[np.ndarray], sr: int,
        threshold: float = 0.08,
    ) -> bool:
        """Layer 1: 多个版本之间是否有可辨差异。

        Args:
            audios: 处理后的音频列表
            sr: 采样率
            threshold: 5D WS 距离阈值, 低于此值视为不可辨

        Returns:
            True 如果至少一对的差异超过阈值
        """
        ...

    @abc.abstractmethod
    def rank_versions(
        self, audios: list[np.ndarray], sr: int,
        emotion_code: str,
    ) -> tuple[list[int], list[float], np.ndarray | None]:
        """Layer 2: 按目标情绪匹配度排序。

        Args:
            audios: 处理后的音频列表
            sr: 采样率
            emotion_code: 目标情绪代码 ("GA", "DR", ...)

        Returns:
            (ranks, distances, ideal_vec)
            ranks[i] = 1-based rank of audios[i] (1 = best match)
            distances[i] = distance from ideal vector
            ideal_vec = (5,) 目标理想向量 (含 vector_bias 如果有)
        """
        ...


class DiagnosisListener(AudioListener):
    """用 Moodify 诊断引擎作为听者。

    对处理后的音频重新诊断 → 得到真实 5D WS 向量 →
    与目标情绪的理想向量比较 → 距离越小 = 越接近目标情绪。

    这不是代理评估的重复——代理用的是 T_EFFECTS 预估,
    这里用的是真实 DSP 输出 + 重新诊断。
    两者的差距就是代理误差, 也就是校准信号。
    """

    def __init__(self, vector_bias: dict | None = None):
        self._vector_bias = vector_bias or {}

    def name(self) -> str:
        return "DiagnosisListener"

    def is_discriminable(
        self, audios: list[np.ndarray], sr: int,
        threshold: float = 0.04,
    ) -> bool:
        n = len(audios)
        if n < 2:
            return False

        ws_vectors = []
        for audio in audios:
            try:
                ws = self._diagnose_audio(audio, sr)
                ws_vectors.append(ws)
            except Exception:
                return True  # 诊断失败 → 保守假设可辨

        # 检查是否有任意一对的 5D 距离超过阈值
        discriminable_pairs = 0
        total_pairs = 0
        for i in range(n):
            for j in range(i + 1, n):
                d = float(np.linalg.norm(ws_vectors[i] - ws_vectors[j]))
                total_pairs += 1
                if d >= threshold:
                    discriminable_pairs += 1

        # 超过 10% 的对可辨 → 整体可辨
        return discriminable_pairs >= max(1, total_pairs * 0.2)

    def rank_versions(
        self, audios: list[np.ndarray], sr: int,
        emotion_code: str,
    ) -> tuple[list[int], list[float], np.ndarray | None]:
        from moodify.knowledge.emotion_targets import get_ideal_process_vector
        from moodify.orchestration.state_transfer import StateTransferEngine

        ideal = get_ideal_process_vector(emotion_code).copy()
        if self._vector_bias:
            for i, dim in enumerate(["E", "D", "S", "T", "H"]):
                ideal[i] += self._vector_bias.get(dim, 0.0)
            ideal = np.clip(ideal, 0.0, 1.0)

        distances = []
        for audio in audios:
            try:
                ws_vec = self._diagnose_audio(audio, sr)
                d = float(np.linalg.norm(ws_vec - ideal))
                distances.append(d)
            except Exception:
                distances.append(999.0)

        # 按距离升序排列 → rank
        order = np.argsort(distances)
        ranks = np.zeros(len(audios), dtype=int)
        for rank_pos, idx in enumerate(order):
            ranks[idx] = rank_pos + 1

        return ranks.tolist(), [float(d) for d in distances], ideal

    @staticmethod
    def _diagnose_audio(audio: np.ndarray, sr: int) -> np.ndarray:
        """In-memory 5D diagnosis — no tempfile, no disk I/O."""
        from moodify.optimizer.calibrate import diagnose_lightweight
        return diagnose_lightweight(audio, sr)
