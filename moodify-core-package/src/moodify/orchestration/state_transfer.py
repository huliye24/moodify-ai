"""
state_transfer.py — 波场状态转移函数 (SPEC §14)
==================================================
将每个 DSP 处理步骤形式化为 WS_A -> WS_B 的映射。

单步:  WS(n+1) = saturate(T_i(WS(n), theta_i, ET))
链合成: WS_final = T_master o T_layer o T_space o T_dynamic o T_spectrum(WS_raw)

五个 T 函数 (SPEC §14.2):
  T_spectrum — 频谱清理 (主要 E, 次要 T/H)
  T_dynamic  — 动态塑形 (主要 D, 次要 T/E)
  T_space    — 空间重构 (主要 S, 次要 T/E)
  T_layer    — 分层增强 (主要 H, 次要 E/S)
  T_master   — 母带打磨 (综合, E/D 为主)
"""

import numpy as np
from dataclasses import dataclass
from typing import Callable

from moodify.data_types import WaveStateDiagnosis
from moodify.knowledge.emotion_targets import get_safety_bounds, resolve_emotion


@dataclass
class WaveStateProcess:
    """处理五维波场状态 (§2.3) — 所有值 ∈ [0, 1]"""
    E: float = 0.5  # 频率均衡度
    D: float = 0.5  # 动态呼吸感
    S: float = 0.5  # 空间层次感
    T: float = 0.5  # 瞬态清晰度
    H: float = 0.5  # 谐波丰富度

    def to_array(self) -> np.ndarray:
        return np.array([self.E, self.D, self.S, self.T, self.H])

    @classmethod
    def from_array(cls, arr: np.ndarray) -> "WaveStateProcess":
        return cls(E=float(arr[0]), D=float(arr[1]), S=float(arr[2]),
                   T=float(arr[3]), H=float(arr[4]))

    def to_dict(self) -> dict:
        return {"E": self.E, "D": self.D, "S": self.S, "T": self.T, "H": self.H}


def saturate(ws: WaveStateProcess) -> WaveStateProcess:
    """饱和保护 — 确保所有维度 ∈ [0, 1] (§14.4)"""
    return WaveStateProcess(
        E=max(0.0, min(1.0, ws.E)),
        D=max(0.0, min(1.0, ws.D)),
        S=max(0.0, min(1.0, ws.S)),
        T=max(0.0, min(1.0, ws.T)),
        H=max(0.0, min(1.0, ws.H)),
    )


class StateTransferEngine:
    """波场状态转移引擎 (§14)"""

    # 五个 T 函数的经验 Delta 矩阵 (§14.2 + 附录 D)
    # (P5, P25, P50, P75, P95) 对每个维度的效应
    T_EFFECTS = {
        "spectrum": {
            "E": (0.05, 0.10, 0.18, 0.25, 0.35),
            "D": (-0.01, 0.00, 0.00, 0.02, 0.05),
            "S": (0.00, 0.00, 0.00, 0.02, 0.05),
            "T": (0.02, 0.04, 0.07, 0.10, 0.15),
            "H": (-0.05, -0.02, 0.00, 0.02, 0.05),
        },
        "dynamic": {
            "E": (0.00, 0.03, 0.08, 0.12, 0.18),
            "D": (0.02, 0.08, 0.15, 0.22, 0.30),
            "S": (0.00, 0.00, 0.00, 0.02, 0.05),
            "T": (-0.10, -0.05, -0.01, 0.05, 0.12),
            "H": (0.00, 0.00, 0.00, 0.00, 0.02),
        },
        "space": {
            "E": (0.00, 0.00, 0.01, 0.03, 0.05),
            "D": (0.00, 0.02, 0.04, 0.06, 0.10),
            "S": (0.05, 0.12, 0.22, 0.30, 0.40),
            "T": (-0.15, -0.10, -0.07, -0.04, -0.01),
            "H": (0.00, 0.00, 0.00, 0.00, 0.02),
        },
        "layer": {
            "E": (0.02, 0.05, 0.08, 0.12, 0.18),
            "D": (0.00, 0.00, 0.00, 0.01, 0.03),
            "S": (0.02, 0.05, 0.08, 0.10, 0.15),
            "T": (0.00, 0.00, 0.00, 0.02, 0.05),
            "H": (0.05, 0.12, 0.22, 0.32, 0.45),
        },
        "master": {
            "E": (0.05, 0.08, 0.10, 0.12, 0.15),
            "D": (0.05, 0.07, 0.08, 0.09, 0.10),
            "S": (0.00, 0.00, 0.02, 0.03, 0.05),
            "T": (0.00, 0.00, 0.00, 0.02, 0.03),
            "H": (0.00, 0.02, 0.04, 0.06, 0.08),
        },
    }

    def apply_transfer(self,
                       ws_in: WaveStateProcess,
                       t_type: str,
                       dsp_strength: float = 0.5,
                       emotion_target: str = "温柔"
                       ) -> tuple[WaveStateProcess, list[str]]:
        """执行单步状态转移"""
        effects = self.T_EFFECTS[t_type]
        delta = {}
        for dim in ["E", "D", "S", "T", "H"]:
            p = effects[dim]
            if dsp_strength <= 0.5:
                t = dsp_strength / 0.5
                delta[dim] = p[0] + t * (p[2] - p[0])
            else:
                t = (dsp_strength - 0.5) / 0.5
                delta[dim] = p[2] + t * (p[4] - p[2])

        ws_out = WaveStateProcess(
            E=ws_in.E + delta["E"],
            D=ws_in.D + delta["D"],
            S=ws_in.S + delta["S"],
            T=ws_in.T + delta["T"],
            H=ws_in.H + delta["H"],
        )
        ws_out = saturate(ws_out)
        warnings = self._check_safety_bounds(ws_out, emotion_target)

        return ws_out, warnings

    def apply_chain_transfer(self,
                             ws_raw: WaveStateProcess,
                             chain_types: list[str],
                             dsp_strengths: list[float] | None = None,
                             emotion_target: str = "温柔"
                             ) -> tuple[WaveStateProcess, dict]:
        """
        执行完整状态转移链:
        T_master o T_layer o T_space o T_dynamic o T_spectrum (ws_raw)
        """
        if dsp_strengths is None:
            dsp_strengths = [0.5] * len(chain_types)

        ws_current = ws_raw
        all_warnings = []
        delta_accumulated = {"E": 0.0, "D": 0.0, "S": 0.0, "T": 0.0, "H": 0.0}

        for t_type, strength in zip(chain_types, dsp_strengths):
            ws_before = ws_current
            ws_current, warnings = self.apply_transfer(
                ws_current, t_type, strength, emotion_target
            )
            all_warnings.extend(warnings)
            for dim in delta_accumulated:
                delta_accumulated[dim] += getattr(ws_current, dim) - getattr(ws_before, dim)

        for dim in delta_accumulated:
            delta_accumulated[dim] = round(delta_accumulated[dim], 3)

        return ws_current, {"warnings": all_warnings, "delta": delta_accumulated}

    def _check_safety_bounds(self, ws: WaveStateProcess,
                              emotion: str) -> list[str]:
        """检查处理后 WS 是否在情绪安全区间内 (§14.3)"""
        try:
            bounds = get_safety_bounds(emotion)
        except KeyError:
            return []

        warnings = []
        for dim_key, dim_val in [("E", ws.E), ("D", ws.D), ("S", ws.S),
                                  ("T", ws.T), ("H", ws.H)]:
            lo, hi = bounds[dim_key]
            if dim_val < lo:
                warnings.append(f"{dim_key}={dim_val:.2f} < safety lo={lo}")
            elif dim_val > hi:
                warnings.append(f"{dim_key}={dim_val:.2f} > safety hi={hi}")
        return warnings

    @staticmethod
    def diagnostic_to_process(ws_diag: WaveStateDiagnosis) -> WaveStateProcess:
        """诊断五维 → 处理五维桥接映射 (§2.4)"""
        s = ws_diag.Spectrum
        d = ws_diag.Dynamics
        sp = ws_diag.Space
        l = ws_diag.Layers
        e = ws_diag.Emotion

        tilt_penalty = min(abs(s.S5_SpectralTilt.value) / 12.0, 1.0)
        E = max(0.0, min(1.0, s.S3_MidClarity.value * 0.7 + (1.0 - tilt_penalty) * 0.3))
        D = max(0.0, min(1.0, (d.D1_LRA.value - 2.0) / 14.0))
        corr_score = 1.0 - sp.SP1_Correlation.value
        rt60_penalty = min(sp.SP3_RT60Consist.value / 0.8, 1.0)
        S = max(0.0, min(1.0, corr_score * 0.7 + (1.0 - rt60_penalty) * 0.3))
        T = max(0.0, min(1.0, l.L3_DrumDetect.value * 1.1))
        H = max(0.0, min(1.0, 1.0 - e.E3_FatigueRisk.value / 120.0))

        return WaveStateProcess(E=E, D=D, S=S, T=T, H=H)

    @staticmethod
    def compute_delta(ws_before: WaveStateProcess,
                      ws_after: WaveStateProcess) -> dict:
        """计算状态差 dWS = WS_final - WS_raw"""
        return {
            "dE": round(ws_after.E - ws_before.E, 3),
            "dD": round(ws_after.D - ws_before.D, 3),
            "dS": round(ws_after.S - ws_before.S, 3),
            "dT": round(ws_after.T - ws_before.T, 3),
            "dH": round(ws_after.H - ws_before.H, 3),
        }
