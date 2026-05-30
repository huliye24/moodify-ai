"""PHYS-007 守恒约束审计 — 能量守恒与动态范围守恒.

PHYS-007 §4-5: 四类守恒约束 (能量/动态范围/相位/信息).
PHYS-001 定理 2: ΔL_out - ΔL_in = ΔL_dynamics + ΔL_spectral + ΔL_residual.
若 |ΔL_residual| > 3σ → 触发守恒违反警告.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass
class ConservationReport:
    """处理链守恒审计报告 (PHYS-007 §4).

    Attributes:
        delta_e_residual: 能量残差 [dB]
        cm_energy: 能量守恒裕度 (≥ 0, 1=完美守恒)
        cm_dynamic_range: 动态范围守恒裕度
        cm_phase: 相位守恒裕度
        cm_info: 信息守恒裕度
        energy_grade: 审计等级 (safe/warning/violation)
        warning_message: 警告信息 (空字符串表示无警告)
    """

    delta_e_residual: float = 0.0
    cm_energy: float = 1.0
    cm_dynamic_range: float = 1.0
    cm_phase: float = 1.0
    cm_info: float = 1.0
    energy_grade: Literal["safe", "warning", "violation"] = "safe"
    warning_message: str = ""

    def to_dict(self) -> dict:
        return {
            "delta_e_residual_db": self.delta_e_residual,
            "cm_energy": self.cm_energy,
            "cm_dynamic_range": self.cm_dynamic_range,
            "cm_phase": self.cm_phase,
            "cm_info": self.cm_info,
            "energy_grade": self.energy_grade,
            "warning_message": self.warning_message,
        }


def audit_conservation(
    l_in: float,
    l_out: float,
    l_dynamics: float = 0.0,
    l_spectral: float = 0.0,
    sigma_noise: float = 0.1,
) -> ConservationReport:
    """PHYS-001 定理 2 和 PHYS-007 §5.2 定义的能量守恒审计.

    审计方程:
      ΔL_residual = L_out - L_in - ΔL_dynamics - ΔL_spectral

      |ΔL_residual| ≤ 3σ → safe
      3σ < |ΔL_residual| ≤ 12σ → warning
      |ΔL_residual| > 12σ → violation

    Args:
        l_in: 输入响度 [LUFS]
        l_out: 输出响度 [LUFS]
        l_dynamics: 动态处理贡献的响度变化 [LUFS]
        l_spectral: 频谱处理贡献的响度变化 [LUFS]
        sigma_noise: 测量噪声标准差 [LUFS], 默认 0.1 LU

    Returns:
        ConservationReport with audit grade and warning
    """
    delta_residual = l_out - l_in - l_dynamics - l_spectral
    cm = 1.0 - abs(delta_residual) / max(abs(l_in), 0.01)

    grade: Literal["safe", "warning", "violation"] = "safe"
    msg = ""

    if abs(delta_residual) > 12.0 * sigma_noise:
        grade = "violation"
        msg = (
            f"能量守恒严重违反: ΔE_residual = {delta_residual:.2f} dB > 12σ "
            f"(σ = {sigma_noise:.2f} LU). 处理链可能存在未报告的能量注入或损失."
        )
    elif abs(delta_residual) > 3.0 * sigma_noise:
        grade = "warning"
        msg = (
            f"能量守恒轻微违反: ΔE_residual = {delta_residual:.2f} dB > 3σ "
            f"(σ = {sigma_noise:.2f} LU). 建议检查测量协议或处理链配置."
        )

    return ConservationReport(
        delta_e_residual=delta_residual,
        cm_energy=cm,
        energy_grade=grade,
        warning_message=msg,
    )
