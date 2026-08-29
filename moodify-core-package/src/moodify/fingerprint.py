"""PHYS-003 处理器效应指纹 — THD / CR_eff / 瞬态保持度.

PHYS-003 §3-4: 为压缩/限制/饱和/失真四类处理器定义效应指纹 (PEF).
PEF = {CR_eff, T_p, ΔL, THD, R_odd/even, S}.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np


@dataclass
class ProcessorFingerprint:
    """处理链效应指纹 (PHYS-003 §3.3, §4.2).

    Attributes:
        cr_eff: 有效压缩比 (实际动态范围变化 / 标称压缩比)
        thd: 总谐波失真 [%]
        thd_odd: 奇次谐波失真分量 [%]
        thd_even: 偶次谐波失真分量 [%]
        transient_preservation: 瞬态保持度 [0, 1], 1=完全保留
        attack_time_ratio: 实际起音时间 / 原始起音时间
        spectral_centroid_shift: 谱质心偏移 [Hz] (处理后 - 处理前)
        confidence_level: 计算置信等级
    """

    cr_eff: float = 0.0
    thd: float = 0.0
    thd_odd: float = 0.0
    thd_even: float = 0.0
    transient_preservation: float = 1.0
    attack_time_ratio: float = 1.0
    spectral_centroid_shift: float = 0.0
    confidence_level: Literal["high", "medium", "low"] = "medium"

    def to_dict(self) -> dict:
        return {
            "cr_eff": self.cr_eff,
            "thd_pct": self.thd,
            "thd_odd_pct": self.thd_odd,
            "thd_even_pct": self.thd_even,
            "transient_preservation": self.transient_preservation,
            "attack_time_ratio": self.attack_time_ratio,
            "spectral_centroid_shift_hz": self.spectral_centroid_shift,
            "confidence_level": self.confidence_level,
        }


def compute_thd(audio_input: np.ndarray, audio_output: np.ndarray,
                sr: int, test_freq: float = 1000.0) -> ProcessorFingerprint:
    """测量处理链的 THD 效应指纹 (PHYS-003 §6 审计协议).

    Args:
        audio_input: 输入音频 (mono, 1-D)
        audio_output: 输出音频 (mono, 1-D)
        sr: 采样率 [Hz]
        test_freq: 测试基频 [Hz], 默认 1000 Hz

    Returns:
        ProcessorFingerprint with thd, thd_odd, thd_even populated
    """
    fp = ProcessorFingerprint()

    try:
        n = min(len(audio_input), len(audio_output))
        n_fft = min(n, 2 ** 14)
        fft_in = np.abs(np.fft.rfft(audio_input[:n_fft]))
        fft_out = np.abs(np.fft.rfft(audio_output[:n_fft]))
        freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
        freq_res = freqs[1] - freqs[0]  # bin 宽度 [Hz]

        # 基波 bin 索引
        idx_fundamental = int(test_freq / freq_res)
        if idx_fundamental >= len(fft_in):
            fp.confidence_level = "low"
            return fp

        fundamental_in = fft_in[idx_fundamental]
        fundamental_out = fft_out[idx_fundamental]

        # 谐波功率 (2-10 次) — 按 bin 索引查找
        harmonic_power_in = 0.0
        harmonic_power_out = 0.0
        harmonic_power_odd = 0.0
        harmonic_power_even = 0.0
        for k in range(2, 11):
            h_idx = idx_fundamental * k
            if h_idx < len(fft_in):
                p_in = fft_in[h_idx] ** 2
                p_out = fft_out[h_idx] ** 2
                harmonic_power_in += p_in
                harmonic_power_out += p_out
                if k % 2 == 0:
                    harmonic_power_even += p_out
                else:
                    harmonic_power_odd += p_out

        if fundamental_in > 1e-10:
            fp.thd = float(100.0 * np.sqrt(harmonic_power_in) / fundamental_in)
        if fundamental_out > 1e-10:
            fp.thd = float(100.0 * np.sqrt(harmonic_power_out) / fundamental_out)
            fp.thd_odd = float(100.0 * np.sqrt(harmonic_power_odd) / fundamental_out)
            fp.thd_even = float(100.0 * np.sqrt(harmonic_power_even) / fundamental_out)

        fp.confidence_level = "high"
    except Exception:
        fp.thd = 0.0
        fp.confidence_level = "low"

    return fp


def estimate_cr_eff(nominal_ratio: float, threshold_db: float,
                    input_peak_dbfs: float) -> float:
    """估计有效压缩比 CR_eff (PHYS-003 §3.1 定义 1).

    CR_eff = ΔL_in / ΔL_out, 反映实际动态范围变化.
    简化模型: 超阈值比例越大, 有效压缩比越接近标称比.
    未超过阈值时 CR_eff = 1.0 (无压缩).

    Args:
        nominal_ratio: 标称压缩比 [1:1]
        threshold_db: 压缩阈值 [dB]
        input_peak_dbfs: 输入峰值电平 [dBFS]

    Returns:
        有效压缩比 (≥ 1.0)
    """
    if input_peak_dbfs > threshold_db:
        over_threshold = input_peak_dbfs - threshold_db
        effective = min(nominal_ratio, max(1.0, over_threshold / 6.0))
    else:
        effective = 1.0
    return effective
