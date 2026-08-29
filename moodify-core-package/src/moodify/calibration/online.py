"""在线校准引擎 — D 随处理量自动增长。

核心算法: 每次 moodify process 后对比 proxy 预测 vs DSP 实测,
用指数移动平均更新偏差估计。后续 proxy_evaluate 自动修正。

D(n) = D_0 + (D_max - D_0) * (1 - e^(-n/λ))
  n: 累计处理次数
  λ: 20 (每 20 次处理 D 增长 63% 的剩余空间)
  D_0 = 0.05, D_max = 0.40

原理:
  不需要人耳。proxy 预测的是 "T_EFFECTS 认为 DSP 会产生的效果"。
  重诊断测量的是 "DSP 实际产生的效果"。两者的系统性偏差 =
  代理指标的校准信号。每次处理自动提取这个信号。
"""

from __future__ import annotations

import json
import os
import math
import logging
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np

from moodify.orchestration.state_transfer import StateTransferEngine

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
#  CalibrationState — 持久化的校准数据
# ═══════════════════════════════════════════════════════════════

@dataclass
class EmotionCalibration:
    """单个情绪的校准统计。"""
    n: int = 0                          # 样本数
    mu_bias: float = 0.0                # 代理偏差均值 (real - proxy)
    sigma_bias: float = 0.0             # 代理偏差标准差
    mu_error_5d: list[float] = field(default_factory=lambda: [0.0]*5)  # 5D 逐维误差
    proxy_real_pairs: list[dict] = field(default_factory=list)          # 最近 20 对 (proxy, real)
    last_updated: str = ""


class CalibrationState:
    """全局校准状态 — 序列化到 outputs/calibration_state.json。

    读取:
      state = CalibrationState.load("outputs")
      bias = state.get_bias("GA")  → float

    更新 (在线):
      state.update("GA", proxy=72.0, real=68.0, strength=..., ws_before=..., ws_after=...)
      state.save()
    """

    def __init__(self, storage_dir: str = "outputs"):
        self._path = os.path.join(storage_dir, "calibration_state.json")
        self.emotions: dict[str, EmotionCalibration] = {}
        self.total_n: int = 0

    # ── 序列化 ────────────────────────────────

    @classmethod
    def load(cls, storage_dir: str = "outputs") -> "CalibrationState":
        state = cls(storage_dir)
        if os.path.exists(state._path):
            try:
                with open(state._path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                state.total_n = raw.get("total_n", 0)
                for code, edata in raw.get("emotions", {}).items():
                    ec = EmotionCalibration()
                    ec.n = edata.get("n", 0)
                    ec.mu_bias = edata.get("mu_bias", 0.0)
                    ec.sigma_bias = edata.get("sigma_bias", 0.0)
                    ec.mu_error_5d = edata.get("mu_error_5d", [0.0]*5)
                    ec.proxy_real_pairs = edata.get("proxy_real_pairs", [])
                    ec.last_updated = edata.get("last_updated", "")
                    state.emotions[code] = ec
            except Exception:
                pass
        return state

    def save(self) -> None:
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        raw = {
            "total_n": self.total_n,
            "emotions": {
                code: {
                    "n": ec.n,
                    "mu_bias": round(ec.mu_bias, 3),
                    "sigma_bias": round(ec.sigma_bias, 3),
                    "mu_error_5d": [round(v, 4) for v in ec.mu_error_5d],
                    "proxy_real_pairs": ec.proxy_real_pairs[-20:],  # 只保留最近 20 对
                    "last_updated": ec.last_updated,
                }
                for code, ec in self.emotions.items()
            },
        }
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(raw, f, ensure_ascii=False, indent=2)

    # ── 更新 (在线) ───────────────────────────

    def update(
        self,
        emotion_code: str,
        proxy_score: float,
        real_eds: float,
        strength_vector: dict,
        ws_before_5d: np.ndarray,
        ws_after_5d: np.ndarray,
    ) -> None:
        """处理完一首歌后调用。用指数移动平均更新偏差估计。

        Args:
            emotion_code: "GA", "DR", ...
            proxy_score: 搜索阶段代理预估的 EDS
            real_eds: 真实 DSP 输出重诊断后的 EDS
            strength_vector: 实际使用的 5D 强度
            ws_before_5d: 处理前 5D 波场 (真实诊断)
            ws_after_5d: 处理后 5D 波场 (真实重诊断)
        """
        if emotion_code not in self.emotions:
            self.emotions[emotion_code] = EmotionCalibration()

        ec = self.emotions[emotion_code]
        bias = real_eds - proxy_score

        # 指数移动平均 (α = 0.15 → 约 7 次处理后旧数据权重降到 50%)
        alpha = 0.15
        if ec.n == 0:
            ec.mu_bias = bias
            ec.sigma_bias = 0.0
        else:
            ec.mu_bias = (1 - alpha) * ec.mu_bias + alpha * bias
            ec.sigma_bias = math.sqrt(
                (1 - alpha) * ec.sigma_bias**2 + alpha * (bias - ec.mu_bias)**2
            )

        # 5D 逐维误差: 从 T_EFFECTS 计算预估 delta, 对比真实 delta
        chain_order = ["spectrum", "dynamic", "space", "layer", "master"]
        T_EFFECTS = StateTransferEngine.T_EFFECTS
        dims = ["E", "D", "S", "T", "H"]
        delta_proxy = np.zeros(5)
        for j, (t_type, s) in enumerate(zip(chain_order,
            [strength_vector.get(d, 0.5) for d in chain_order])):
            effects = T_EFFECTS[t_type]
            for k, dim in enumerate(dims):
                p = effects[dim]
                if s <= 0.5:
                    t = s / 0.5
                    delta_proxy[k] += p[0] + t * (p[2] - p[0])
                else:
                    t = (s - 0.5) / 0.5
                    delta_proxy[k] += p[2] + t * (p[4] - p[2])

        delta_real = np.asarray(ws_after_5d) - np.asarray(ws_before_5d)
        error_5d = delta_real - delta_proxy

        if ec.n == 0:
            ec.mu_error_5d = error_5d.tolist()
        else:
            for k in range(5):
                ec.mu_error_5d[k] = (1 - alpha) * ec.mu_error_5d[k] + alpha * float(error_5d[k])

        # 存储 proxy/real 对 (用于 Spearman ρ 估算)
        ec.proxy_real_pairs.append({
            "proxy": round(proxy_score, 1),
            "real": round(real_eds, 1),
            "bias": round(bias, 1),
            "timestamp": datetime.now().isoformat(),
        })

        ec.n += 1
        self.total_n += 1
        ec.last_updated = datetime.now().isoformat()

    # ── 查询 ──────────────────────────────────

    def get_bias(self, emotion_code: str) -> float:
        """获取某情绪的代理偏差修正值 (real - proxy)。"""
        ec = self.emotions.get(emotion_code)
        if ec is None or ec.n < 1:
            return 0.0
        return ec.mu_bias

    def get_error_5d(self, emotion_code: str) -> np.ndarray:
        """获取某情绪的 5D 逐维误差修正向量。"""
        ec = self.emotions.get(emotion_code)
        if ec is None or ec.n < 1:
            return np.zeros(5)
        return np.array(ec.mu_error_5d)

    def get_confidence(self, emotion_code: str) -> float:
        """返回该情绪校准数据的可信度 α ∈ [0, 1]。"""
        ec = self.emotions.get(emotion_code)
        if ec is None:
            return 0.0
        return min(1.0, ec.n / 10.0)  # 10 个样本后达到满可信度 (武器定理: L必须尽快转正)

    def estimate_rho(self, emotion_code: str) -> float | None:
        """从 proxy/real 对估计 Spearman ρ。"""
        ec = self.emotions.get(emotion_code)
        if ec is None or len(ec.proxy_real_pairs) < 8:
            return None
        from scipy.stats import spearmanr
        proxies = [p["proxy"] for p in ec.proxy_real_pairs]
        reals = [p["real"] for p in ec.proxy_real_pairs]
        try:
            return float(spearmanr(proxies, reals).statistic)
        except Exception:
            return None

    def d_value(self) -> float:
        """估算当前 D (数据资产质量)。

        D = D_0 + (D_max - D_0) * (1 - e^(-n_eff/λ))
        n_eff = 加权有效样本数 (考虑每个情绪的样本量)
        """
        D_0 = 0.05
        D_max = 0.40
        lam = 20.0

        if self.total_n == 0:
            return D_0

        # n_eff: 总和有效样本 (每个情绪最多贡献 30 的权重, 递减)
        n_eff = 0.0
        for ec in self.emotions.values():
            n_eff += min(ec.n, 30) * (1.0 - 0.3 * max(0, ec.n - 30) / 30)
        n_eff = max(0, n_eff)

        return D_0 + (D_max - D_0) * (1.0 - math.exp(-n_eff / lam))

    def summary(self) -> dict:
        """人类可读的校准状态摘要。"""
        return {
            "total_processed": self.total_n,
            "estimated_D": round(self.d_value(), 3),
            "emotions": {
                code: {
                    "n": ec.n,
                    "mu_bias": round(ec.mu_bias, 1),
                    "confidence": round(min(1.0, ec.n / 20.0), 2),
                    "rho": round(self.estimate_rho(code), 3) if self.estimate_rho(code) is not None else None,
                }
                for code, ec in self.emotions.items()
            },
        }


# ═══════════════════════════════════════════════════════════════
#  全局单例 (模块级缓存, 避免每次 proxy_evaluate 都读文件)
# ═══════════════════════════════════════════════════════════════

_state: CalibrationState | None = None
_state_dir: str = "outputs"


def get_state(storage_dir: str = "outputs") -> CalibrationState:
    """获取全局校准状态 (懒加载)。"""
    global _state, _state_dir
    if _state is None or _state_dir != storage_dir:
        _state = CalibrationState.load(storage_dir)
        _state_dir = storage_dir
    return _state


def update_calibration(
    emotion_code: str,
    proxy_score: float,
    real_eds: float,
    strength_vector: dict,
    ws_before_5d: np.ndarray,
    ws_after_5d: np.ndarray,
    storage_dir: str = "outputs",
) -> CalibrationState:
    """处理完成后调用 — 更新校准状态并持久化。

    这是 workflow_engine → 校准引擎的唯一接口。
    """
    state = get_state(storage_dir)
    state.update(emotion_code, proxy_score, real_eds, strength_vector,
                 ws_before_5d, ws_after_5d)
    state.save()
    return state


def correct_proxy_score(
    raw_proxy: float,
    emotion_code: str,
    storage_dir: str = "outputs",
) -> float:
    """对代理评分应用偏差修正。

    这是 proxy_evaluate → 校准引擎的唯一接口。

    Returns:
        corrected = raw_proxy + confidence * bias
        样本不足时 confidence=0 → 返回原始值 (无修正)
    """
    state = get_state(storage_dir)
    bias = state.get_bias(emotion_code)
    confidence = state.get_confidence(emotion_code)
    return raw_proxy + confidence * bias
