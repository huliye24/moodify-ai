"""MATH-001 命题 1 — ICC/κ 计算工具.

双途径: pingouin (优先, 完整 ICC 家族 + CI) / 手写 ANOVA (兜底).
MATH-001 定义 2-3: ICC ≥ 0.7 可接受, ICC ≥ 0.85 优秀.

ICCTracker: 跨多次诊断调用累积评分, 当数据充足时自动计算 ICC.
"""

from __future__ import annotations

from typing import Optional

import numpy as np


def compute_icc(
    ratings: list[list[float]],
    icc_type: str = "ICC3",
) -> dict:
    """计算组内相关系数 ICC (MATH-001 定义 2).

    Args:
        ratings: shape [n_raters × n_targets], 行=评估者, 列=对象
        icc_type: ICC 类型 ("ICC3" = ICC(3,1) 混合模型绝对一致性)

    Returns:
        {"icc": float, "p_value": float|None, "ci_95": [lower, upper],
         "n_raters": int, "n_targets": int, "method": str}

    优先使用 pingouin; 不可用时使用手写 ANOVA 兜底.
    """
    # 尝试 pingouin (完整 ICC 家族 + CI)
    try:
        import pingouin as pg
        import pandas as pd

        rater_col, target_col, rating_col = _ratings_to_long_format(ratings)
        df = pd.DataFrame({
            "rater": rater_col,
            "target": target_col,
            "rating": rating_col,
        })
        result = pg.intraclass_corr(
            data=df, targets="target", raters="rater", ratings="rating"
        )
        icc_row = result[result["Type"] == icc_type]
        if len(icc_row) > 0:
            row = icc_row.iloc[0]
            ci_str = str(row.get("CI95%", "0-0"))
            ci_parts = ci_str.split("-")
            return {
                "icc": float(row["ICC"]),
                "p_value": float(row["pValue"]) if "pValue" in row else None,
                "ci_95": [float(ci_parts[0]), float(ci_parts[1])],
                "n_raters": len(ratings),
                "n_targets": len(ratings[0]) if ratings else 0,
                "method": "pingouin",
            }
    except ImportError:
        pass

    # 手写 ANOVA 兜底
    return _icc_anova_fallback(ratings)


def _ratings_to_long_format(ratings: list[list[float]]) -> tuple[list, list, list]:
    """将矩阵格式 [rater × target] 转为列式 (rater, target, rating)."""
    rater_col, target_col, rating_col = [], [], []
    for r, rater_row in enumerate(ratings):
        for t, rating in enumerate(rater_row):
            rater_col.append(f"R{r}")
            target_col.append(f"T{t}")
            rating_col.append(rating)
    return rater_col, target_col, rating_col


def _icc_anova_fallback(ratings: list[list[float]]) -> dict:
    """双因素 ANOVA ICC 兜底实现 (ICC(3,1)).

    MATH-001 定义 2:
      ICC(2,k) = (BMS - WMS) / (BMS + (k-1)·WMS)
    此处实现 ICC(3,1): (MS_targets - MS_residual) / (MS_targets + (k-1)·MS_residual)
    """
    n_raters = len(ratings)
    n_targets = len(ratings[0]) if ratings else 0

    if n_raters < 2 or n_targets < 2:
        return {
            "icc": 0.0,
            "p_value": None,
            "ci_95": [0.0, 0.0],
            "n_raters": n_raters,
            "n_targets": n_targets,
            "method": "anova_fallback",
        }

    data = np.array(ratings, dtype=np.float64)
    grand_mean = data.mean()
    target_means = data.mean(axis=0)
    rater_means = data.mean(axis=1)

    # 平方和分解
    ss_targets = n_raters * np.sum((target_means - grand_mean) ** 2)
    ss_raters = n_targets * np.sum((rater_means - grand_mean) ** 2)
    ss_total = np.sum((data - grand_mean) ** 2)
    ss_residual = ss_total - ss_targets - ss_raters

    df_targets = n_targets - 1
    df_residual = (n_targets - 1) * (n_raters - 1)

    if df_targets <= 0 or df_residual <= 0:
        return {
            "icc": 0.0, "p_value": None,
            "ci_95": [0.0, 0.0],
            "n_raters": n_raters, "n_targets": n_targets,
            "method": "anova_fallback",
        }

    ms_targets = ss_targets / df_targets
    ms_residual = ss_residual / df_residual

    # ICC(3,1) 公式
    icc = (ms_targets - ms_residual) / (ms_targets + (n_raters - 1) * ms_residual)

    # Fisher Z 变换近似 p-value 和 CI
    icc_clipped = float(np.clip(icc, -0.999, 0.999))
    try:
        from scipy.stats import norm
        z = 0.5 * np.log((1.0 + icc_clipped) / (1.0 - icc_clipped))
        se = 1.0 / np.sqrt(n_targets - 2) if n_targets > 2 else 1.0
        z_stat = z / se
        p_value = 2.0 * (1.0 - norm.cdf(abs(z_stat)))
        ci_lower = np.tanh(z - 1.96 * se)
        ci_upper = np.tanh(z + 1.96 * se)
    except ImportError:
        p_value = None
        ci_lower, ci_upper = 0.0, 1.0

    return {
        "icc": icc_clipped,
        "p_value": float(p_value) if p_value is not None else None,
        "ci_95": [float(ci_lower), float(ci_upper)],
        "n_raters": n_raters,
        "n_targets": n_targets,
        "method": "anova_fallback",
    }


# ── ICC 追踪器 (SPEC-011 T6) ──────────────────────────

class ICCTracker:
    """跨诊断调用累积主观评分, 自动计算 ICC (MATH-001 命题 1).

    用法:
      tracker = ICCTracker(min_targets=5)
      tracker.record(rater="Alice", target="audio_001", e1=7, e2=6)
      tracker.record(rater="Bob",   target="audio_001", e1=6, e2=7)
      ...
      result = tracker.compute()  # 当 >=2 raters × >=min_targets 时计算 ICC
      if result and result["icc"] < 0.7:
          # 标记为低信度, 不进入优化
    """

    def __init__(self, min_targets: int = 5):
        self._ratings_e1: dict[str, dict[str, float]] = {}  # {rater: {target: score}}
        self._ratings_e2: dict[str, dict[str, float]] = {}
        self._min_targets = min_targets
        self._icc_cache: dict | None = None

    def record(self, rater: str, target: str,
               e1: float | None = None, e2: float | None = None) -> None:
        """记录一次评分."""
        if e1 is not None:
            self._ratings_e1.setdefault(rater, {})[target] = e1
        if e2 is not None:
            self._ratings_e2.setdefault(rater, {})[target] = e2
        self._icc_cache = None  # 数据变更, 清除缓存

    @property
    def n_raters(self) -> int:
        return len(self._ratings_e1) or len(self._ratings_e2)

    @property
    def n_targets(self) -> int:
        """所有评估者共同评分的对象数."""
        if not self._ratings_e1:
            return 0
        # 取所有评估者评分的交集
        targets_sets = [set(t.keys()) for t in self._ratings_e1.values()]
        return len(targets_sets[0].intersection(*targets_sets[1:])) if len(targets_sets) >= 2 else 0

    def compute(self) -> dict | None:
        """计算 ICC (缓存结果). 数据不足返回 None."""
        if self._icc_cache is not None:
            return self._icc_cache

        n_r = self.n_raters
        n_t = self.n_targets
        if n_r < 2 or n_t < self._min_targets:
            return None

        # 构建评分矩阵 (仅取所有 rater 都有评分的 targets)
        common_targets = None
        for rater_scores in self._ratings_e1.values():
            if common_targets is None:
                common_targets = set(rater_scores.keys())
            else:
                common_targets &= set(rater_scores.keys())
        if common_targets is None or len(common_targets) < self._min_targets:
            return None

        sorted_targets = sorted(common_targets)
        matrix = []
        for rater in sorted(self._ratings_e1.keys()):
            row = [self._ratings_e1[rater].get(t, 0.0) for t in sorted_targets]
            matrix.append(row)

        self._icc_cache = compute_icc(matrix)
        return self._icc_cache

    def confidence_level(self) -> str:
        """基于 ICC 的置信等级 (MATH-001 命题 1)."""
        result = self.compute()
        if result is None:
            return "low"  # 数据不足 → 默认低置信
        icc = result["icc"]
        if icc >= 0.85:
            return "high"
        elif icc >= 0.7:
            return "medium"
        else:
            return "low"

    def is_reliable(self) -> bool:
        """ICC ≥ 0.7 — 满足 MATH-001 信度门槛."""
        return self.confidence_level() in ("high", "medium")

    def reset(self) -> None:
        self._ratings_e1.clear()
        self._ratings_e2.clear()
        self._icc_cache = None
