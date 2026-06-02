#!/usr/bin/env python3
"""mrs_formula_v02.py — MRS v0.2 三段式真实度公式验证模块.

核心公式:
    MRS_final = α * MRS_after + β * ΔMRS - γ * OPR - η * LoudnessPenalty

四组公开函数:
    compute_mrs_abs(audio_path, config_path)        → 绝对真实度
    compute_overprocessing_risk(before, after, cfg)  → 过度处理风险
    compute_loudness_penalty(audio_path, config)     → 响度惩罚
    compute_mrs_final(before, after, config)         → 最终 MRS

所有输出包含 explain 字段解释成因。
"""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import yaml

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_MOODIFY_SRC = _PROJECT_ROOT / "moodify-core-package" / "src"
if str(_MOODIFY_SRC) not in sys.path:
    sys.path.insert(0, str(_MOODIFY_SRC))

from moodify.reality_metrics import (
    _load_mono_stereo,
    _spectrum_features,
    _dynamic_features,
    _transient_features,
    _space_features,
    _texture_features,
    EPS,
)

DEFAULT_CFG = str(_PROJECT_ROOT / "runs" / "mrs_formula_validation_v02" / "configs" / "mrs_formula_v02.yaml")


def _load_cfg(path: Optional[str] = None) -> dict:
    p = path or DEFAULT_CFG
    if not os.path.exists(p):
        raise FileNotFoundError(f"MRS config not found: {p}")
    with open(p) as f:
        return yaml.safe_load(f) or {}


# ═══════════════════════════════════════════════════════════════
# Extra feature extractors
# ═══════════════════════════════════════════════════════════════

def _harsh_band_energy(mono: np.ndarray, sr: int) -> float:
    n = len(mono)
    fft = np.abs(np.fft.rfft(mono * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    total = np.sum(fft ** 2) + EPS
    mask = (freqs >= 2500) & (freqs <= 5000)
    return float(np.sum(fft[mask] ** 2) / total)


def _spectral_slope(mono: np.ndarray, sr: int) -> float:
    n = len(mono)
    fft = np.abs(np.fft.rfft(mono * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    valid = (freqs > 100) & (freqs < sr / 2)
    if np.sum(valid) < 10:
        return -6.0
    log_f = np.log2(freqs[valid])
    db_spec = 20.0 * np.log10(fft[valid] + EPS)
    return float(np.polyfit(log_f, db_spec, 1)[0])


def _zero_crossing_rate(mono: np.ndarray) -> float:
    if len(mono) < 2:
        return 0.0
    return float(np.sum(np.abs(np.diff(np.sign(mono)))) / 2 / len(mono))


def _harmonic_noise_ratio(mono: np.ndarray) -> float:
    n = len(mono)
    fft = np.abs(np.fft.rfft(mono * np.hanning(n)))
    log_spec = np.log(fft + EPS)
    cep = np.fft.irfft(log_spec)
    if len(cep) < 10:
        return 0.5
    peak = float(np.max(cep[1:min(200, len(cep))]))
    rms = float(np.sqrt(np.mean(cep[50:] ** 2)) + EPS)
    return float(np.clip(peak / rms / 10.0, 0.0, 1.0))


def _lufs_estimate(mono: np.ndarray, sr: int) -> float:
    try:
        import pyloudnorm as pyln
        return float(pyln.Meter(sr).integrated_loudness(mono))
    except Exception:
        rms_lin = np.sqrt(np.mean(mono ** 2) + EPS)
        return float(20.0 * math.log10(rms_lin))


def _short_time_energy_variance(mono: np.ndarray, sr: int) -> float:
    win_len = int(0.05 * sr)
    hop = win_len // 2
    if len(mono) < win_len:
        return 0.0
    energies = [float(np.mean(mono[i:i + win_len] ** 2))
                for i in range(0, len(mono) - win_len, hop)]
    if len(energies) < 3:
        return 0.0
    return float(np.std(energies) / (max(np.mean(energies), EPS)))


def _extract_all_features(audio_path: str) -> dict:
    mono, stereo, sr = _load_mono_stereo(audio_path)
    spec = _spectrum_features(mono, sr)
    dyn = _dynamic_features(mono, sr)
    trans = _transient_features(mono, sr)
    space = _space_features(stereo)
    tex = _texture_features(mono, sr)
    return {
        "spectrum": spec, "dynamic": dyn, "transient": trans,
        "space": space, "texture": tex,
        "sample_rate": sr, "duration_s": len(mono) / sr,
        "_mono": mono, "path": audio_path,
    }


# ═══════════════════════════════════════════════════════════════
# MRS_abs: Absolute Reality Score
# ═══════════════════════════════════════════════════════════════

def _clamp(v: float) -> float:
    return round(max(0.0, min(100.0, v)), 1)


def _spectral_reality(features: dict) -> tuple[float, list[str]]:
    s, e = features["spectrum"], []
    score = 100.0
    sr = features["sample_rate"]
    cent_hz = s.get("centroid_norm", 0.15) * sr / 2

    if cent_hz > 4500:
        d = min(20, (cent_hz - 4500) / 200)
        score -= d; e.append(f"谱质心偏高 ({cent_hz:.0f}Hz) → 偏亮偏尖 -{d:.0f}")
    elif cent_hz < 800:
        d = min(20, (800 - cent_hz) / 80)
        score -= d; e.append(f"谱质心偏低 ({cent_hz:.0f}Hz) → 偏闷 -{d:.0f}")
    else:
        e.append(f"谱质心正常 ({cent_hz:.0f}Hz)")

    sub_db = 20.0 * math.log10(max(s.get("band_sub", 0.01), EPS))
    bass_db = 20.0 * math.log10(max(s.get("band_bass", 0.05), EPS))
    if sub_db < -30: score -= 10; e.append("极低频缺失, 缺少重量感")
    if bass_db < -18: score -= 8; e.append("低频偏薄, 缺乏温暖感")
    if s.get("band_presence", 0.1) > 0.3: score -= 10; e.append("中高频过强, 刺耳风险")
    flat = s.get("flatness", 0.3)
    if flat > 0.7: score -= 12; e.append(f"频谱异常平坦 ({flat:.2f})")

    slope = _spectral_slope(features["_mono"], sr)
    if slope > -3: score -= 8; e.append("频谱过平, 缺乏自然衰减")
    elif slope < -15: score -= 5; e.append("高频衰减过陡, 声音发闷")
    return _clamp(score), e


def _dynamic_reality(features: dict) -> tuple[float, list[str]]:
    d, e = features["dynamic"], []
    score = 100.0
    crest = d.get("crest_factor", 4.0)
    dr = d.get("dynamic_range", 5.0)
    if crest < 3.0: p = min(30, (3.0 - crest) * 10); score -= p; e.append(f"动态压扁 (crest={crest:.1f}) -{p:.0f}")
    elif crest > 8.0: p = min(15, (crest - 8.0) * 2); score -= p; e.append(f"峰值过高 (crest={crest:.1f}) -{p:.0f}")
    else: e.append(f"动态正常 (crest={crest:.1f})")
    if dr < 5: p = min(25, (5 - dr) * 5); score -= p; e.append(f"动态范围窄 (DR={dr:.1f}dB) -{p:.0f}")
    elif dr > 18: e.append(f"动态范围宽 ({dr:.1f}dB)")
    return _clamp(score), e


def _texture_reality(features: dict) -> tuple[float, list[str]]:
    t, sr, mono = features["texture"], features["sample_rate"], features["_mono"]
    e, score = [], 100.0
    rough = t.get("roughness_proxy", 0.05)
    spike = t.get("spike_score", 0.01)
    hn = _harmonic_noise_ratio(mono)
    zcr = _zero_crossing_rate(mono)
    if rough > 0.15: p = min(20, (rough - 0.15) * 100); score -= p; e.append(f"频谱粗糙 ({rough:.3f}) -{p:.0f}")
    else: e.append(f"粗糙度正常 ({rough:.3f})")
    if spike > 0.05: score -= 12; e.append(f"频谱尖峰多 ({spike:.4f}) → 数字化共振")
    if zcr < 0.02: score -= 8; e.append("过零率极低, 缺乏质感细节")
    elif zcr > 0.15: score -= 5; e.append("过零率偏高, 噪声化")
    if hn < 0.2: score -= 10; e.append("谐波结构弱, 偏向噪声")
    elif hn > 0.6: e.append(f"谐波清晰 (HNR={hn:.2f})")
    score += 5 * t.get("hf_smoothness", 0.5)
    return _clamp(score), e


def _spatial_reality(features: dict) -> tuple[float, list[str]]:
    sp, e = features["space"], []
    score = 100.0
    corr = sp.get("lr_correlation", 0.5)
    width = sp.get("stereo_width", 0.5)
    ms = sp.get("mid_side_ratio", 0.5)
    phase = sp.get("phase_anomaly", 0.0)
    if corr < 0.2: p = min(20, (0.2 - corr) * 50); score -= p; e.append(f"声道相关性极低 ({corr:.2f}) → 单声道兼容差 -{p:.0f}")
    elif corr > 0.9: p = min(15, (corr - 0.85) * 50); score -= p; e.append(f"声场过窄 ({corr:.2f}) -{p:.0f}")
    else: e.append(f"立体声宽度正常 (corr={corr:.2f})")
    if phase > 0.3: score -= 15; e.append(f"相位异常 ({phase:.2f})")
    if ms > 2.0: score -= 10; e.append(f"侧边能量过强 (M/S={ms:.2f}) → 虚宽")
    if width < 0.05 and corr > 0.99: score = min(score, 75.0); e.append("单声道, 空间评分降级")
    return _clamp(score), e


def _transient_reality(features: dict) -> tuple[float, list[str]]:
    t, e = features["transient"], []
    score = 100.0
    flux = t.get("spectral_flux_mean", 0.1)
    energy_ch = t.get("short_time_energy_change", 0.3)
    if flux < 0.05: score -= 12; e.append("频谱变化极小 → 缺乏音色演变")
    elif flux > 0.5: score -= 5; e.append("频谱变化剧烈 → 不稳定")
    if energy_ch > 1.0: score -= 8; e.append("能量波动大 → 段落衔接不平滑")
    return _clamp(score), e


def _balance_reality(features: dict) -> tuple[float, list[str]]:
    subs = {k: features.get(f"_sub_{k}", 50) for k in
            ["spectral", "dynamic", "texture", "spatial", "transient", "fatigue"]}
    std = float(np.std(list(subs.values())))
    b = 100.0 - std * 4
    e = [f"维度平衡度 std={std:.1f}" + (" ← 不均衡" if std > 10 else "")]
    return _clamp(b), e


def _anti_fatigue(features: dict) -> tuple[float, list[str]]:
    s, d, mono, sr = features["spectrum"], features["dynamic"], features["_mono"], features["sample_rate"]
    e, score = [], 100.0
    harsh = _harsh_band_energy(mono, sr)
    lufs = _lufs_estimate(mono, sr)
    crest = d.get("crest_factor", 4.0)
    flat = s.get("flatness", 0.3)
    if harsh > 0.25: p = min(25, (harsh - 0.25) * 100); score -= p; e.append(f"2.5-5kHz 过强 ({harsh:.1%}) → 易疲劳 -{p:.0f}")
    elif harsh > 0.15: score -= 8; e.append(f"刺耳频段略高 ({harsh:.1%})")
    if lufs > -9: score -= 15; e.append(f"响度过高 ({lufs:.1f} LUFS) → 冲击耳膜")
    elif lufs < -23: score -= 5; e.append(f"响度偏低 ({lufs:.1f} LUFS)")
    if flat > 0.7: score -= 12; e.append(f"频谱过平 ({flat:.2f}) → 疲劳")
    if crest < 2.5: score -= 15; e.append(f"动态平坦 (crest={crest:.1f}) → 无喘息空间")
    return _clamp(score), e


def _plastic_risk(features: dict) -> tuple[float, list[str]]:
    s, d, sp, t, mono, sr = (features["spectrum"], features["dynamic"],
                              features["space"], features["transient"],
                              features["_mono"], features["sample_rate"])
    e, risk = [], 0.0
    flat = s.get("flatness", 0.3)
    crest = d.get("crest_factor", 4.0)
    corr = sp.get("lr_correlation", 0.5)
    flux = t.get("spectral_flux_mean", 0.1)
    harsh = _harsh_band_energy(mono, sr)
    hn = _harmonic_noise_ratio(mono)
    if flat > 0.55: c = min(25, (flat - 0.35) * 80); risk += c; e.append(f"频谱异常平坦 ({flat:.2f}) → AI特征 +{c:.0f}")
    if crest < 3.0: c = min(25, (3.0 - crest) * 15); risk += c; e.append(f"动态过度压缩 (crest={crest:.1f}) → 塑料 +{c:.0f}")
    if corr > 0.85: c = min(15, (corr - 0.7) * 80); risk += c; e.append(f"声场过窄 (corr={corr:.2f}) → 空间塑料 +{c:.0f}")
    if corr < 0.0: c = min(20, abs(corr) * 25); risk += c; e.append(f"相位异常 (corr={corr:.2f}) → 声场损坏 +{c:.0f}")
    if flux < 0.12: c = min(15, (0.12 - flux) * 150); risk += c; e.append(f"音色变化极小 (flux={flux:.3f}) → 缺乏生命力 +{c:.0f}")
    if harsh > 0.15 and hn < 0.35: c = min(15, (1.0 - hn) * 20); risk += c; e.append(f"高频亮但谐波弱 (harsh={harsh:.1%}) → 假亮 +{c:.0f}")
    # Detect "over-dark" as plastic-like (artificially muffled)
    cent_hz = s.get("centroid_norm", 0.15) * features["sample_rate"] / 2
    if cent_hz < 900: c = min(20, (900 - cent_hz) / 45); risk += c; e.append(f"过度暗沉 (centroid={cent_hz:.0f}Hz) → 处理损伤 +{c:.0f}")
    return _clamp(risk), e


# ═══════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════

def compute_mrs_abs(audio_path: str, config_path: Optional[str] = None) -> dict:
    """计算单音频的绝对 MRS 真实度 (0-100)."""
    cfg = _load_cfg(config_path)
    fml = cfg.get("formula", {})
    if not os.path.exists(audio_path):
        return {"audio_path": audio_path, "mrs_abs": 0.0, "error": "file not found"}
    try:
        feat = _extract_all_features(audio_path)
    except Exception as exc:
        return {"audio_path": audio_path, "mrs_abs": 0.0, "error": str(exc)}

    duration = feat["duration_s"]
    if duration < 0.5:
        return {"audio_path": audio_path, "duration_s": duration, "mrs_abs": 0.0,
                "error": "audio too short"}

    rms_lin = np.sqrt(np.mean(feat["_mono"] ** 2) + EPS)
    if 20.0 * math.log10(rms_lin) < -60:
        return {"audio_path": audio_path, "duration_s": duration, "mrs_abs": 0.0,
                "error": "silence detected"}

    all_explain = []
    sub = {}
    for name, fn in [("spectral_reality", _spectral_reality),
                      ("dynamic_reality", _dynamic_reality),
                      ("texture_reality", _texture_reality),
                      ("spatial_reality", _spatial_reality),
                      ("transient_reality", _transient_reality),
                      ("anti_fatigue", _anti_fatigue),
                      ("balance_reality", _balance_reality)]:
        s, ex = fn(feat)
        sub[name] = s
        feat[f"_sub_{name.split('_')[0]}"] = s
        all_explain.extend(ex)

    # 先算 plastic_risk (独立于其他)
    plastic, exp_pla = _plastic_risk(feat)
    sub["plastic_risk"] = plastic
    all_explain.extend(exp_pla)

    # MRS_abs 暂时不包含 plastic_risk 惩罚 (那是 final 公式的事)
    mrs_abs = (
        0.24 * sub["spectral_reality"] + 0.20 * sub["dynamic_reality"] +
        0.18 * sub["texture_reality"] + 0.14 * sub["spatial_reality"] +
        0.12 * sub["transient_reality"] + 0.12 * sub["anti_fatigue"]
    )
    mrs_abs = _clamp(mrs_abs)

    raw = {
        "duration_s": round(feat["duration_s"], 1),
        "sample_rate": feat["sample_rate"],
        "centroid_hz": round(feat["spectrum"].get("centroid_norm", 0) * feat["sample_rate"] / 2, 1),
        "flatness": round(feat["spectrum"].get("flatness", 0), 4),
        "crest_factor": round(feat["dynamic"].get("crest_factor", 0), 2),
        "dynamic_range_db": round(feat["dynamic"].get("dynamic_range", 0), 1),
        "lr_correlation": round(feat["space"].get("lr_correlation", 0), 3),
        "stereo_width": round(feat["space"].get("stereo_width", 0), 3),
        "lufs": round(_lufs_estimate(feat["_mono"], feat["sample_rate"]), 1),
        "rms_db": round(20.0 * math.log10(rms_lin), 1),
    }

    return {"audio_path": audio_path, "mrs_abs": mrs_abs, "subscores": sub,
            "raw_features": raw, "explain": all_explain}


def compute_overprocessing_risk(before_path: str, after_path: str,
                                 config_path: Optional[str] = None) -> dict:
    """计算处理前后过度处理风险 (0-100)."""
    cfg = _load_cfg(config_path)
    thr = cfg.get("thresholds", {})
    before = compute_mrs_abs(before_path, config_path)
    after = compute_mrs_abs(after_path, config_path)
    if "error" in before or "error" in after:
        return {"opr": 100.0, "error": f"before={before.get('error')}, after={after.get('error')}"}

    bf_raw = before.get("raw_features", {})
    af_raw = after.get("raw_features", {})
    explain = []
    opr = 0.0

    # 1. Spectral shift risk
    b_cent, a_cent = bf_raw.get("centroid_hz", 2000), af_raw.get("centroid_hz", 2000)
    delta_cent = abs(a_cent - b_cent)
    max_shift = thr.get("max_spectral_centroid_shift_hz", 800)
    if delta_cent > max_shift:
        c = min(25, (delta_cent - max_shift) / 50)
        opr += c; explain.append(f"频谱质心偏移过大 (Δ={delta_cent:.0f}Hz) → +{c:.0f}")

    # 2. Over-dark risk
    if a_cent < thr.get("over_dark_centroid_hz", 1200):
        c = min(20, (1200 - a_cent) / 60)
        opr += c; explain.append(f"处理后过暗 (centroid={a_cent:.0f}Hz) → +{c:.0f}")

    # 3. Over-bright risk
    if a_cent > thr.get("over_bright_centroid_hz", 4500):
        c = min(20, (a_cent - 4500) / 200)
        opr += c; explain.append(f"处理后过亮 (centroid={a_cent:.0f}Hz) → +{c:.0f}")

    # 4. Dynamic damage risk
    b_crest, a_crest = bf_raw.get("crest_factor", 4), af_raw.get("crest_factor", 4)
    crest_drop = b_crest - a_crest
    max_drop = thr.get("max_crest_factor_drop", 2.0)
    if crest_drop > max_drop:
        c = min(25, (crest_drop - max_drop) * 8)
        opr += c; explain.append(f"Crest factor 下降 ({crest_drop:.1f}) → 动态损伤 +{c:.0f}")

    # 5. Phase damage risk
    b_corr, a_corr = bf_raw.get("lr_correlation", 0.5), af_raw.get("lr_correlation", 0.5)
    corr_drop = b_corr - a_corr
    if corr_drop > thr.get("max_correlation_drop", 0.3):
        c = min(15, (corr_drop - 0.3) * 30)
        opr += c; explain.append(f"声道相关性下降 ({corr_drop:.2f}) → 相位风险 +{c:.0f}")

    # 6. Loudness jump risk (also feeds into loudness penalty separately)
    b_lufs, a_lufs = bf_raw.get("lufs", -14), af_raw.get("lufs", -14)
    lufs_jump = a_lufs - b_lufs
    if lufs_jump > thr.get("max_safe_lufs_increase", 2.0):
        c = min(15, (lufs_jump - 2.0) * 5)
        opr += c; explain.append(f"响度跳升 ({lufs_jump:+.1f} LUFS) → +{c:.0f}")

    opr = _clamp(opr)
    return {"before_path": before_path, "after_path": after_path, "opr": opr,
            "opr_breakdown": {
                "spectral_shift_risk": _clamp(min(25, (delta_cent - max_shift) / 50) if delta_cent > max_shift else 0),
                "over_dark_risk": _clamp(min(20, (1200 - a_cent) / 60) if a_cent < 1200 else 0),
                "over_bright_risk": _clamp(min(20, (a_cent - 4500) / 200) if a_cent > 4500 else 0),
                "dynamic_damage_risk": _clamp(min(25, (crest_drop - max_drop) * 8) if crest_drop > max_drop else 0),
                "phase_damage_risk": _clamp(min(15, (corr_drop - 0.3) * 30) if corr_drop > 0.3 else 0),
                "loudness_jump_risk": _clamp(min(15, (lufs_jump - 2.0) * 5) if lufs_jump > 2.0 else 0),
            },
            "explain": explain}


def compute_loudness_penalty(audio_path: str,
                              config_path: Optional[str] = None) -> dict:
    """计算响度异常惩罚 (0-100)."""
    cfg = _load_cfg(config_path)
    thr = cfg.get("thresholds", {})
    abs_result = compute_mrs_abs(audio_path, config_path)
    if "error" in abs_result:
        return {"loudness_penalty": 50.0, "error": abs_result["error"]}

    lufs = abs_result.get("raw_features", {}).get("lufs", -14)
    rms_db = abs_result.get("raw_features", {}).get("rms_db", -14)
    penalty = 0.0
    explain = []

    if lufs > thr.get("max_safe_lufs_increase", 2.0):
        penalty += min(30, (lufs - (-9)) * 3)
        explain.append(f"LUFS 偏高 ({lufs:.1f} LUFS)")
    if lufs < -23:
        penalty += min(15, (-23 - lufs) * 2)
        explain.append(f"LUFS 偏低 ({lufs:.1f} LUFS)")

    peak_dbfs = abs_result.get("raw_features", {}).get("rms_db", -1)
    if rms_db > -1:
        penalty += 20
        explain.append(f"RMS 峰值接近 0dBFS")

    if not explain:
        explain.append("响度正常, 无惩罚")
    return {"audio_path": audio_path, "loudness_penalty": _clamp(penalty),
            "lufs": round(lufs, 1), "explain": explain}


def compute_mrs_final(before_path: str, after_path: str,
                       config_path: Optional[str] = None) -> dict:
    """计算 MRS_final = α*MRS_after + β*ΔMRS - γ*OPR - η*LoudnessPenalty."""
    cfg = _load_cfg(config_path)
    fml = cfg.get("formula", {})

    mrs_before = compute_mrs_abs(before_path, config_path)
    mrs_after = compute_mrs_abs(after_path, config_path)
    opr_result = compute_overprocessing_risk(before_path, after_path, config_path)
    lpen_result = compute_loudness_penalty(after_path, config_path)

    mrs_b = mrs_before.get("mrs_abs", 0)
    mrs_a = mrs_after.get("mrs_abs", 0)
    delta = mrs_a - mrs_b
    opr = opr_result.get("opr", 0)
    lpen = lpen_result.get("loudness_penalty", 0)

    alpha = fml.get("alpha", 0.55)
    beta = fml.get("beta", 0.30)
    gamma = fml.get("gamma", 0.25)
    eta = fml.get("eta", 0.15)

    mrs_final = alpha * mrs_a + beta * delta - gamma * opr - eta * lpen
    mrs_final = _clamp(mrs_final)

    explain = []
    if delta > 5: explain.append(f"处理后真实度上升 {delta:.1f} 分 ✅")
    elif delta < -5: explain.append(f"处理后真实度下降 {delta:.1f} 分 ⚠️")
    else: explain.append(f"真实度变化不大 (Δ={delta:.1f})")

    if opr > 30: explain.append(f"过度处理风险高 (OPR={opr:.0f}) ⚠️")
    elif opr > 15: explain.append(f"存在轻微过度处理 (OPR={opr:.0f})")
    else: explain.append(f"未发现明显过度处理 (OPR={opr:.0f})")

    if lpen > 20: explain.append(f"响度异常 (penalty={lpen:.0f}) ⚠️")
    elif lpen > 5: explain.append(f"轻微响度偏差 (penalty={lpen:.0f})")
    else: explain.append("响度正常 ✅")

    return {
        "before_path": before_path, "after_path": after_path,
        "mrs_before": mrs_b, "mrs_after": mrs_a,
        "delta_mrs": round(delta, 1),
        "opr": opr, "loudness_penalty": lpen,
        "mrs_final": mrs_final,
        "subscores_before": mrs_before.get("subscores", {}),
        "subscores_after": mrs_after.get("subscores", {}),
        "opr_breakdown": opr_result.get("opr_breakdown", {}),
        "explain": explain,
    }
