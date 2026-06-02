#!/usr/bin/env python3
"""mrs_open_benchmark_v03.py — MRS Open Benchmark v0.3.1 开放式跑分引擎.

核心公式 (不变):
    MRS_open = 1000 + 300 * log10(D_ref / (D_real + eps))

v0.3.1 修改:
  - 新增 over_dark_penalty: 检测过度暗化处理
  - 增强 HQ damage penalty: 降低触发阈值, 提高最大惩罚
  - V7 验收阈值改为三级制: -20 / -40 / -80

继承 MRS v0.2 的八个子维度 (0-100), 转换为距离项后加权求和.
MRS_open 不设上限, 数值越高代表越接近真实音乐声波结构.

用法:
    from workers.mrs_open_benchmark_v03 import compute_mrs_open, calibrate_dref
    result = compute_mrs_open("audio.wav", d_ref=..., weights=...)
    calibration = calibrate_dref(audio_paths=["baseline1.wav", ...])
"""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path
from typing import Optional

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_MOODIFY_SRC = _PROJECT_ROOT / "moodify-core-package" / "src"
if str(_MOODIFY_SRC) not in sys.path:
    sys.path.insert(0, str(_MOODIFY_SRC))

# ── 复用 v0.2 的底层特征提取和子指标计算 ──────────────────
from workers.mrs_formula_v02 import (
    compute_mrs_abs,
    _extract_all_features,
    _spectral_reality,
    _dynamic_reality,
    _texture_reality,
    _spatial_reality,
    _transient_reality,
    _anti_fatigue,
    _plastic_risk,
    _balance_reality,
    _clamp,
    EPS,
)

EPS_V03 = 1e-12

# ═══════════════════════════════════════════════════════════════
#  Default weights for D_real (sum = 1.0)
# ═══════════════════════════════════════════════════════════════

DEFAULT_WEIGHTS: dict[str, float] = {
    "spectrum":   0.18,
    "dynamic":    0.16,
    "texture":    0.16,
    "space":      0.14,
    "transient":  0.14,
    "anti_fatigue": 0.08,
    "balance":    0.07,
    "plastic_risk": 0.07,
}

# ═══════════════════════════════════════════════════════════════
#  Default extra penalties (added to D_real)
# ═══════════════════════════════════════════════════════════════

DEFAULT_PENALTIES: dict[str, dict] = {
    "high_quality_damage": {
        "enabled": True,
        "trigger_d_real_low": 0.25,    # D_real 低于此值视为高质量样本
        "delta_texture": 0.05,          # v0.3.1: 从 0.10 降到 0.05 (更敏感)
        "delta_transient": 0.05,
        "delta_dynamic": 0.05,
        "delta_space": 0.05,
        "penalty_per_dim": 0.12,        # v0.3.1: 从 0.10 升到 0.12
        "max_penalty": 0.60,            # v0.3.1: 从 0.30 升到 0.60
        "crest_collapse_trigger": 2.0,  # v0.3.1 新增: crest 下降超过此值直接加罚
        "crest_collapse_penalty": 0.15,
    },
    "loudness_anomaly": {
        "enabled": True,
        "lufs_upper": -8,
        "lufs_lower": -30,
        "penalty": 0.15,
    },
    "extreme_flatness": {
        "enabled": True,
        "flatness_trigger": 0.80,
        "penalty": 0.08,
    },
    # v0.3.1 新增: over_dark_penalty
    "over_dark": {
        "enabled": True,
        "air_band_starvation": 0.005,   # air 频段能量低于此值触发
        "air_penalty": 0.08,
        "slope_steep_trigger": -9.0,    # 频谱斜率陡于此值触发 (正常 -3~-7)
        "slope_penalty": 0.10,
        "centroid_drop_ratio": 0.25,    # 质心相对参考下降超过 25% 触发
        "centroid_drop_penalty": 0.10,
        "combined_max_penalty": 0.25,   # over_dark 最大累计惩罚
    },
}

# ═══════════════════════════════════════════════════════════════
#  Spectral helpers for over_dark detection
# ═══════════════════════════════════════════════════════════════

def _compute_band_energy(mono: np.ndarray, sr: int, f_low: float, f_high: float) -> float:
    """Compute energy ratio in [f_low, f_high] band."""
    n = len(mono)
    fft = np.abs(np.fft.rfft(mono * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    total = np.sum(fft ** 2) + EPS_V03
    mask = (freqs >= f_low) & (freqs <= f_high)
    return float(np.sum(fft[mask] ** 2) / total)


def _compute_spectral_slope(mono: np.ndarray, sr: int) -> float:
    """Fit spectral slope in dB/octave. Negative = high-freq rolloff."""
    n = len(mono)
    fft = np.abs(np.fft.rfft(mono * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    valid = (freqs > 100) & (freqs < sr / 2)
    if np.sum(valid) < 10:
        return -6.0
    log_f = np.log2(freqs[valid])
    db_spec = 20.0 * np.log10(fft[valid] + EPS_V03)
    return float(np.polyfit(log_f, db_spec, 1)[0])

# ═══════════════════════════════════════════════════════════════
#  Core: D_real computation
# ═══════════════════════════════════════════════════════════════

def compute_d_real(
    audio_path: str,
    weights: Optional[dict[str, float]] = None,
    penalties: Optional[dict] = None,
    reference_subscores: Optional[dict[str, float]] = None,
    reference_raw: Optional[dict] = None,   # v0.3.1: reference raw_features for over_dark centroid comparison
) -> dict:
    """计算单音频到真实音乐参考系的距离 D_real.

    D_real 越小, 音频越接近真实音乐参考系.

    Args:
        audio_path: 音频文件路径
        weights: 8 维度权重 (sum to 1.0)
        penalties: 额外惩罚配置
        reference_subscores: 用于 high_quality_damage 检测的参考子分数 (如 before 版本的分数)
        reference_raw: v0.3.1 新增, 参考音频的 raw_features (用于 over_dark centroid 对比)

    Returns:
        {
            "audio_path": str,
            "d_real": float,
            "subscores": {...},
            "distances": {...},
            "weighted_distances": {...},
            "extra_penalties": {...},
            "extra_penalty_total": float,
            "mrs_abs": float,
            "raw_features": {...},   # v0.3.1: 包含 over_dark 信号
            "explain": [...],
        }
    """
    w = weights or DEFAULT_WEIGHTS
    p = penalties or DEFAULT_PENALTIES

    # ── 输入验证 ────────────────────────────────────────
    if not os.path.exists(audio_path):
        return {
            "audio_path": audio_path,
            "d_real": float("inf"),
            "error": f"文件不存在: {audio_path}",
            "explain": ["文件不存在"],
        }

    # ── 复用 v0.2 提取子指标 ────────────────────────────
    v02_result = compute_mrs_abs(audio_path)
    if "error" in v02_result:
        return {
            "audio_path": audio_path,
            "d_real": float("inf"),
            "error": v02_result.get("error", "unknown"),
            "explain": [v02_result.get("error", "unknown")],
        }

    subscores = v02_result.get("subscores", {})
    mrs_abs = v02_result.get("mrs_abs", 0.0)
    explain: list[str] = []

    # ── 将 0-100 子指标转换为距离项 ──────────────────────
    #  距离项越大 → 越不真实
    #  真实度越高 → 距离越小
    distances: dict[str, float] = {
        "spectrum":   (100.0 - subscores.get("spectral_reality", 50.0)) / 100.0,
        "dynamic":    (100.0 - subscores.get("dynamic_reality", 50.0)) / 100.0,
        "texture":    (100.0 - subscores.get("texture_reality", 50.0)) / 100.0,
        "space":      (100.0 - subscores.get("spatial_reality", 50.0)) / 100.0,
        "transient":  (100.0 - subscores.get("anti_fatigue", 50.0)) / 100.0,
        "anti_fatigue": (100.0 - subscores.get("anti_fatigue", 50.0)) / 100.0,
        "balance":    (100.0 - subscores.get("balance_reality", 50.0)) / 100.0,
        "plastic_risk": subscores.get("plastic_risk", 50.0) / 100.0,
    }

    # ── 加权求和 ─────────────────────────────────────────
    weighted: dict[str, float] = {}
    d_real = 0.0
    for dim, dist in distances.items():
        wd = dist * w.get(dim, 0.125)
        weighted[dim] = wd
        d_real += wd

    # ── 额外惩罚项 ───────────────────────────────────────
    extra_penalties: dict[str, float] = {}
    extra_total = 0.0

    # 1. High quality damage penalty (v0.3.1 enhanced)
    if p.get("high_quality_damage", {}).get("enabled", True):
        hq = p["high_quality_damage"]
        if reference_subscores is not None:
            # 计算各维度的距离变化 (after - before)
            ref_distances = {
                "texture": (100.0 - reference_subscores.get("texture_reality", 50.0)) / 100.0,
                "dynamic": (100.0 - reference_subscores.get("dynamic_reality", 50.0)) / 100.0,
                "space": (100.0 - reference_subscores.get("spatial_reality", 50.0)) / 100.0,
                "transient": (100.0 - reference_subscores.get("anti_fatigue", 50.0)) / 100.0,
            }
            dims_damaged = 0
            for dim in ["texture", "transient", "dynamic", "space"]:
                delta = distances.get(dim, 0.0) - ref_distances.get(dim, 0.0)
                # v0.3.1: use configured delta threshold (default 0.05)
                trigger = hq.get("delta_" + dim, hq.get("delta_texture", 0.05))
                if delta > trigger:
                    dims_damaged += 1
                    explain.append(f"HQ damage: {dim} worsened by {delta:.3f}")

            if dims_damaged > 0:
                penalty = min(
                    hq.get("max_penalty", 0.60),
                    dims_damaged * hq.get("penalty_per_dim", 0.12)
                )
                extra_penalties["high_quality_damage"] = penalty
                extra_total += penalty
                explain.append(f"High quality damage penalty: +{penalty:.3f} ({dims_damaged} dims)")

            # v0.3.1 新增: Crest factor collapse detection
            if reference_raw is not None:
                raw = v02_result.get("raw_features", {})
                ref_crest = reference_raw.get("crest_factor", None)
                cur_crest = raw.get("crest_factor", None)
                if ref_crest is not None and cur_crest is not None and ref_crest > 2.0:
                    crest_drop = ref_crest - cur_crest
                    if crest_drop > hq.get("crest_collapse_trigger", 2.0):
                        cp = hq.get("crest_collapse_penalty", 0.15)
                        extra_penalties["crest_collapse"] = cp
                        extra_total += cp
                        explain.append(f"Crest collapse: {ref_crest:.1f} → {cur_crest:.1f} (drop={crest_drop:.1f}) +{cp:.3f}")

    # 2. Loudness anomaly penalty
    if p.get("loudness_anomaly", {}).get("enabled", True):
        la = p["loudness_anomaly"]
        raw = v02_result.get("raw_features", {})
        lufs = raw.get("lufs", -14.0)
        if lufs > la.get("lufs_upper", -8):
            penalty = la.get("penalty", 0.15)
            extra_penalties["loudness_anomaly"] = penalty
            extra_total += penalty
            explain.append(f"Loudness anomaly (LUFS={lufs:.1f} > -8): +{penalty:.3f}")
        elif lufs < la.get("lufs_lower", -30):
            penalty = la.get("penalty", 0.15) * 0.5
            extra_penalties["loudness_anomaly"] = penalty
            extra_total += penalty
            explain.append(f"Loudness too low (LUFS={lufs:.1f} < -30): +{penalty:.3f}")

    # 3. Extreme flatness penalty
    if p.get("extreme_flatness", {}).get("enabled", True):
        ef = p["extreme_flatness"]
        raw = v02_result.get("raw_features", {})
        flatness = raw.get("flatness", 0.3)
        if flatness > ef.get("flatness_trigger", 0.80):
            penalty = ef.get("penalty", 0.08)
            extra_penalties["extreme_flatness"] = penalty
            extra_total += penalty
            explain.append(f"Extreme spectral flatness ({flatness:.3f} > 0.80): +{penalty:.3f}")

    # 4. v0.3.1 新增: Over-dark penalty
    if p.get("over_dark", {}).get("enabled", True):
        od = p["over_dark"]
        raw = v02_result.get("raw_features", {})

        # 4a. Extract raw audio for spectral_slope and air band energy
        try:
            mono = v02_result.get("_mono", None)
            sr = raw.get("sample_rate", 44100)
            if mono is None:
                # Fallback: re-extract features
                feat = _extract_all_features(audio_path)
                mono = feat.get("_mono")
                sr = feat.get("sample_rate", 44100)

            od_penalty_total = 0.0
            od_signals: list[str] = []

            # Signal 1: Air band starvation (high frequencies missing)
            if mono is not None:
                air_energy = _compute_band_energy(mono, sr, 8000, 16000)
                if air_energy < od.get("air_band_starvation", 0.005):
                    p_air = od.get("air_penalty", 0.08)
                    od_penalty_total += p_air
                    od_signals.append(f"air_band={air_energy:.4f} < {od['air_band_starvation']}")

                # Signal 2: Excessively steep spectral slope (too much rolloff)
                slope = _compute_spectral_slope(mono, sr)
                if slope < od.get("slope_steep_trigger", -9.0):
                    p_slope = od.get("slope_penalty", 0.10)
                    od_penalty_total += p_slope
                    od_signals.append(f"slope={slope:.1f} < {od['slope_steep_trigger']}")

                # Signal 3: Centroid dropped significantly vs reference
                if reference_raw is not None:
                    ref_centroid = reference_raw.get("centroid_hz", None)
                    cur_centroid = raw.get("centroid_hz", None)
                    if ref_centroid is not None and cur_centroid is not None and ref_centroid > 500:
                        drop_ratio = (ref_centroid - cur_centroid) / ref_centroid
                        if drop_ratio > od.get("centroid_drop_ratio", 0.25):
                            p_cent = od.get("centroid_drop_penalty", 0.10)
                            od_penalty_total += p_cent
                            od_signals.append(f"centroid_drop={drop_ratio:.1%} (from {ref_centroid:.0f} to {cur_centroid:.0f})")

                # Cap and apply
                if od_penalty_total > 0:
                    capped = min(od_penalty_total, od.get("combined_max_penalty", 0.25))
                    extra_penalties["over_dark"] = round(capped, 6)
                    extra_total += capped
                    explain.append(f"Over-dark penalty: +{capped:.3f} ({'; '.join(od_signals)})")
            else:
                explain.append("Over-dark: skipped (no mono data)")
        except Exception as e:
            explain.append(f"Over-dark: error ({e})")

    d_real += extra_total

    return {
        "audio_path": audio_path,
        "d_real": round(d_real, 6),
        "subscores": subscores,
        "distances": {k: round(v, 6) for k, v in distances.items()},
        "weighted_distances": {k: round(v, 6) for k, v in weighted.items()},
        "extra_penalties": extra_penalties,
        "extra_penalty_total": round(extra_total, 6),
        "mrs_abs": mrs_abs,
        "raw_features": raw,
        "explain": explain,
    }


# ═══════════════════════════════════════════════════════════════
#  Core: MRS_open formula
# ═══════════════════════════════════════════════════════════════

def compute_mrs_open(
    audio_path: str,
    d_ref: float = 0.4,
    reference_subscores: Optional[dict[str, float]] = None,
    reference_raw: Optional[dict] = None,   # v0.3.1
    weights: Optional[dict[str, float]] = None,
    penalties: Optional[dict] = None,
) -> dict:
    """计算 MRS Open v0.3.1 开放式跑分.

    MRS_open = 1000 + 300 * log10(D_ref / (D_real + eps))

    Args:
        audio_path: 音频文件路径
        d_ref: 基准距离 (从基准样本校准)
        reference_subscores: 参考子分数 (用于 high quality damage 检测)
        reference_raw: v0.3.1 新增, 参考音频 raw_features (用于 over_dark/crest 对比)
        weights: D_real 权重
        penalties: 额外惩罚配置

    Returns:
        {
            "audio_path": str,
            "mrs_open": float,
            "d_real": float,
            "d_ref": float,
            "subscores": {...},
            "distances": {...},
            "mrs_abs": float,
            "extra_penalties": {...},
            "explain": [...],
        }
    """
    dreal_result = compute_d_real(audio_path, weights, penalties, reference_subscores, reference_raw)
    if "error" in dreal_result:
        return {
            "audio_path": audio_path,
            "mrs_open": 0.0,
            "d_real": dreal_result.get("d_real", float("inf")),
            "d_ref": d_ref,
            "error": dreal_result.get("error", "unknown"),
            "subscores": {},
            "explain": dreal_result.get("explain", []),
        }

    d_real = dreal_result["d_real"]

    if abs(d_real) < EPS_V03:
        d_real = EPS_V03

    mrs_open = 1000.0 + 300.0 * math.log10(d_ref / (d_real + EPS_V03))

    return {
        "audio_path": audio_path,
        "mrs_open": round(mrs_open, 1),
        "d_real": d_real,
        "d_ref": d_ref,
        "subscores": dreal_result.get("subscores", {}),
        "distances": dreal_result.get("distances", {}),
        "weighted_distances": dreal_result.get("weighted_distances", {}),
        "extra_penalties": dreal_result.get("extra_penalties", {}),
        "extra_penalty_total": dreal_result.get("extra_penalty_total", 0.0),
        "mrs_abs": dreal_result.get("mrs_abs", 0.0),
        "explain": dreal_result.get("explain", []),
    }


# ═══════════════════════════════════════════════════════════════
#  D_ref calibration
# ═══════════════════════════════════════════════════════════════

def calibrate_dref(
    audio_paths: list[str],
    weights: Optional[dict[str, float]] = None,
    penalties: Optional[dict] = None,
    method: str = "median",
) -> dict:
    """从基准样本集校准 D_ref.

    读取所有基准样本, 计算各自的 D_real, 取中位数或均值作为 D_ref.
    确保基准样本的 MRS_open 中位数 ≈ 1000.

    Args:
        audio_paths: 基准音频文件路径列表
        weights: D_real 权重
        penalties: 额外惩罚配置
        method: "median" (推荐) 或 "mean"

    Returns:
        {
            "d_ref": float,
            "calibration_method": str,
            "n_samples": int,
            "d_real_values": [...],
            "d_real_median": float,
            "d_real_mean": float,
            "baseline_median_mrs": float,
            "baseline_mean_mrs": float,
            "explain": [...],
        }
    """
    d_real_values: list[float] = []
    results: list[dict] = []

    for path in audio_paths:
        dr = compute_d_real(path, weights, penalties)
        if "error" not in dr:
            d_real_values.append(dr["d_real"])
            results.append(dr)

    if len(d_real_values) < 3:
        return {
            "d_ref": 0.4,
            "calibration_method": "fallback_default",
            "n_samples": len(d_real_values),
            "d_real_values": d_real_values,
            "explain": [f"样本不足 (< 3), 使用默认 D_ref = 0.4"],
        }

    arr = np.array(d_real_values)
    median = float(np.median(arr))
    mean = float(np.mean(arr))

    if method == "median":
        d_ref = median
    elif method == "mean":
        d_ref = mean
    else:
        d_ref = median

    d_ref = max(d_ref, EPS_V03)

    # 验证: 用校准后的 D_ref 反算基准样本的 MRS_open
    mrs_open_values = [
        1000.0 + 300.0 * math.log10(d_ref / (d + EPS_V03))
        for d in d_real_values
    ]
    median_mrs = float(np.median(mrs_open_values))
    mean_mrs = float(np.mean(mrs_open_values))

    explain = [
        f"Calibration method: {method}",
        f"Samples: {len(d_real_values)}",
        f"D_ref = {d_ref:.6f}",
        f"Baseline median D_real: {median:.6f}",
        f"Baseline mean D_real: {mean:.6f}",
        f"Baseline median MRS_open: {median_mrs:.1f}",
        f"Baseline mean MRS_open: {mean_mrs:.1f}",
    ]

    return {
        "d_ref": round(d_ref, 6),
        "calibration_method": method,
        "n_samples": len(d_real_values),
        "d_real_values": [round(d, 6) for d in d_real_values],
        "d_real_median": round(median, 6),
        "d_real_mean": round(mean, 6),
        "baseline_median_mrs": round(median_mrs, 1),
        "baseline_mean_mrs": round(mean_mrs, 1),
        "explain": explain,
    }


# ═══════════════════════════════════════════════════════════════
#  Theoretical formula verification (no audio needed)
# ═══════════════════════════════════════════════════════════════

def verify_theoretical_properties() -> dict:
    """验证 MRS_open 公式的纯数学性质 (V1, V2, V3).

    Returns:
        {test_name: {passed: bool, detail: ...}}
    """
    tests = {}

    # ── V1: Monotonicity ─────────────────────────────────
    d_real_vals = [10.0, 5.0, 2.0, 1.0, 0.5, 0.1, 0.01]
    d_ref = 1.0
    mrs_vals = [
        1000.0 + 300.0 * math.log10(d_ref / (d + EPS_V03))
        for d in d_real_vals
    ]

    inversions = 0
    for i in range(1, len(mrs_vals)):
        if mrs_vals[i] <= mrs_vals[i - 1]:
            inversions += 1

    tests["V1_monotonicity"] = {
        "passed": inversions == 0,
        "d_real_values": d_real_vals,
        "mrs_open_values": [round(m, 1) for m in mrs_vals],
        "inversions": inversions,
        "detail": f"D_real ↑ → MRS_open ↓: {inversions} inversions" if inversions == 0 else f"FAILED: {inversions} inversions",
    }

    # ── V2: Scaling law ──────────────────────────────────
    test_cases = [
        (1.0, 1000.0),
        (0.1, 1300.0),
        (0.01, 1600.0),
        (10.0, 700.0),
    ]
    scale_errors = []
    for d, expected in test_cases:
        actual = 1000.0 + 300.0 * math.log10(d_ref / (d + EPS_V03))
        error = abs(actual - expected)
        scale_errors.append({"d_real": d, "expected": expected, "actual": round(actual, 6), "error": round(error, 12)})

    max_error = max(e["error"] for e in scale_errors)
    tests["V2_scaling"] = {
        "passed": max_error < 1e-6,
        "test_cases": scale_errors,
        "max_error": max_error,
        "detail": f"Scaling law verified, max error = {max_error:.2e}",
    }

    # ── V3: No ceiling ───────────────────────────────────
    tiny_distances = [1e-1, 1e-2, 1e-3, 1e-4, 1e-5]
    tiny_results = []
    any_nan = False
    any_inf = False
    prev = None
    ceiling_detected = False

    for d in tiny_distances:
        m = 1000.0 + 300.0 * math.log10(d_ref / (d + EPS_V03))
        if math.isnan(m): any_nan = True
        if math.isinf(m): any_inf = True
        if prev is not None and m <= prev: ceiling_detected = True
        prev = m
        tiny_results.append({"d_real": d, "mrs_open": round(m, 1)})

    tests["V3_no_ceiling"] = {
        "passed": (not any_nan and not any_inf and not ceiling_detected),
        "tiny_results": tiny_results,
        "any_nan": any_nan,
        "any_inf": any_inf,
        "ceiling_detected": ceiling_detected,
        "detail": f"No ceiling: {not ceiling_detected}, no nan: {not any_nan}, no inf: {not any_inf}",
    }

    return tests


# ═══════════════════════════════════════════════════════════════
#  Batch convenience
# ═══════════════════════════════════════════════════════════════

def compute_mrs_open_batch(
    audio_paths: list[str],
    d_ref: float,
    weights: Optional[dict[str, float]] = None,
    penalties: Optional[dict] = None,
) -> list[dict]:
    """批量计算 MRS_open."""
    return [
        compute_mrs_open(p, d_ref, weights=weights, penalties=penalties)
        for p in audio_paths
    ]
