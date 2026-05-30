"""MATH-001 公理 D — 协议版本管理与测量记录.

公理 D (可审计性): 任何报告值必须绑定协议版本 π、工具版本 v、
数据版本 d_v、随机种子 s。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

# ── 协议版本常量 ──────────────────────────────────

PROTOCOL_VERSION = "π-1.0.0"  # 当前测量协议版本 (MATH-001)

# PHYS-002 推荐 STFT 标准配置: N_FFT=2048, hop=N_FFT/4=512, Hann 窗
STFT_CONFIG_STANDARD = {
    "n_fft": 2048,
    "hop_length": 512,
    "window": "hann",
    "zero_pad": False,
    "normalize": True,
}

# quick mode 使用的轻量配置 (N_FFT=1024, 保持 hop=512)
STFT_CONFIG_QUICK = {
    "n_fft": 1024,
    "hop_length": 512,
    "window": "hann",
    "zero_pad": False,
    "normalize": True,
}


@dataclass
class MeasurementRecord:
    """每次测量的完整记录 (MATH-001 公理 D 报告元组).

    MATH-001 §8.2: 报告元组 = (x, π, v, d_v, s).
    """

    parameter_name: str
    value: float
    uncertainty: float
    protocol_version: str = PROTOCOL_VERSION
    protocol_mode: Literal["quick", "full"] = "full"
    stft_config: dict = field(default_factory=lambda: STFT_CONFIG_STANDARD.copy())
    tool_version: str = "unknown"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence_level: str = "medium"
    is_fallback: bool = False
    fallback_note: str = ""

    def to_dict(self) -> dict:
        return {
            "parameter_name": self.parameter_name,
            "value": self.value,
            "uncertainty": self.uncertainty,
            "protocol_version": self.protocol_version,
            "protocol_mode": self.protocol_mode,
            "stft_config": self.stft_config,
            "tool_version": self.tool_version,
            "timestamp": self.timestamp.isoformat(),
            "confidence_level": self.confidence_level,
            "is_fallback": self.is_fallback,
            "fallback_note": self.fallback_note,
        }
