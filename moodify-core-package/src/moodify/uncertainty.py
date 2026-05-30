"""MATH-006 误差传播与区间推断 — 不确定度计算工具.

MATH-006 §3-5: Delta Method / Bootstrap / Hierarchical Bayesian.
MATH-001 公理 D: 每个报告值必须绑定不确定度。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class UncertaintyResult:
    """单参数的不确定度报告 (MATH-006 §8.1 强制报告字段).

    Attributes:
        point_estimate: 点估计 x̂
        standard_uncertainty: 标准不确定度 u(x̂) = σ/√n
        confidence_level: 置信等级 (high/medium/low/fallback)
        ci_lower: 95% CI 下界
        ci_upper: 95% CI 上界
        n_observations: 观测数 n
        method: 计算方法 (bootstrap/analytical/rule_of_thumb)
        provenance: 数据来源 (experiment/computed/fallback)
        protocol_version: 测量协议版本
        tool_version: 工具版本
    """

    point_estimate: float = 0.0
    standard_uncertainty: float = 0.0
    confidence_level: str = "medium"
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    n_observations: int = 0
    method: str = "rule_of_thumb"
    provenance: str = "experiment"
    protocol_version: str = "unknown"
    tool_version: str = "unknown"
    confidence_level_detail: str = ""

    def to_dict(self) -> dict:
        return {
            "point_estimate": self.point_estimate,
            "standard_uncertainty": self.standard_uncertainty,
            "confidence_level": self.confidence_level,
            "ci_95": [self.ci_lower, self.ci_upper],
            "n_observations": self.n_observations,
            "method": self.method,
            "provenance": self.provenance,
            "protocol_version": self.protocol_version,
            "tool_version": self.tool_version,
        }

    @staticmethod
    def from_bootstrap(samples: list[float],
                       confidence: float = 0.95) -> UncertaintyResult:
        """从 Bootstrap 样本计算不确定度 (百分位法).

        NOTE: MATH-006 §4.3 推荐 BCa 方法作为默认。当前使用百分位法。
        升级路径: scipy.stats.bootstrap(method='BCa') (SciPy >= 1.7).
        """
        import math
        import statistics

        mean = statistics.mean(samples)
        std = statistics.stdev(samples) if len(samples) > 1 else 0.0
        alpha = 1 - confidence
        n = len(samples)
        sorted_samples = sorted(samples)
        idx_lower = int(n * alpha / 2)
        idx_upper = int(n * (1 - alpha / 2)) - 1
        return UncertaintyResult(
            point_estimate=mean,
            standard_uncertainty=std / math.sqrt(n) if n > 0 else 0.0,
            ci_lower=sorted_samples[max(0, idx_lower)],
            ci_upper=sorted_samples[min(n - 1, idx_upper)],
            n_observations=n,
            method="bootstrap",
        )

    @staticmethod
    def from_rule_of_thumb(point: float,
                           relative_uncertainty: float = 0.1) -> UncertaintyResult:
        """从经验相对不确定度估算 (MATH-006 §5.3 小样本默认)."""
        u = abs(point * relative_uncertainty)
        return UncertaintyResult(
            point_estimate=point,
            standard_uncertainty=u,
            confidence_level="low",
            method="rule_of_thumb",
        )

    def __str__(self) -> str:
        ci = (f"[{self.ci_lower:.3f}, {self.ci_upper:.3f}]"
              if self.ci_lower is not None else "N/A")
        return (f"{self.point_estimate:.3f} ± {self.standard_uncertainty:.3f} "
                f"(95% CI: {ci}, {self.confidence_level})")


class ConfidenceLevel:
    """置信度等级 (MATH-001 命题 1: 信度门槛)."""

    HIGH = "high"       # ICC ≥ 0.7, u/x < 0.05
    MEDIUM = "medium"   # ICC ≥ 0.5, u/x < 0.10
    LOW = "low"         # ICC < 0.5 or u/x ≥ 0.10
    FALLBACK = "fallback"  # 使用了回退路径

    @staticmethod
    def classify(icc: Optional[float], relative_uncertainty: float) -> str:
        if icc is not None and icc >= 0.7 and relative_uncertainty < 0.05:
            return ConfidenceLevel.HIGH
        if icc is not None and icc >= 0.5 and relative_uncertainty < 0.10:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW
