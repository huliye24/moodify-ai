#!/usr/bin/env python3
"""mrs_metrics.py — Moodify Reality Score v0.1 计算引擎.

MRS = Moodify Reality Score: 0-100 声音真实度综合评分.

架构:
  Feature Extraction → Sub-Scores → Plastic Penalty → Final MRS

特征来源:
  - 复用 moodify.reality_metrics.extract_reality_features() (7组特征)
  - 新增: harsh band, spectral slope, ZCR, harmonic/noise ratio

子指标 (0-100):
  spectral_reality  — 频谱真实度 (质心/斜率/频带平衡)
  dynamic_reality   — 动态真实度 (crest/DR/瞬态)
  texture_reality   — 质感真实度 (粗糙度/平滑度/尖峰)
  spatial_reality   — 空间真实度 (宽度/相关/相位)
  anti_fatigue      — 听感疲劳风险 (亮度/响度/动态)
  balance_score     — 综合平衡度
  plastic_risk      — AI 塑料感风险 (处罚项,从总分减去)

用法:
    from workers.mrs_metrics import compute_mrs

    result = compute_mrs("audio.wav", "configs/mrs_weights.yaml")
    print(result["mrs"])          # 82.5
    print(result["explain"])      # ["高频能量偏高...", ...]
"""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import yaml

# ── 确保 moodify 在路径中 ─────────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_MOODIFY_SRC = _PROJECT_ROOT / "moodify-core-package" / "src"
if str(_MOODIFY_SRC) not in sys.path:
    sys.path.insert(0, str(_MOODIFY_SRC))

from moodify.reality_metrics import (
    extract_reality_features,
    _load_mono_stereo,
    _spectrum_features,
    _dynamic_features,
    _transient_features,
    _space_features,
    _texture_features,
    EPS,
)

# ═══════════════════════════════════════════════════════════════
#  Configuration
# ═══════════════════════════════════════════════════════════════

DEFAULT_CONFIG_PATH = str(_PROJECT_ROOT / "configs" / "mrs_weights.yaml")


def _load_config(config_path: Optional[str] = None) -> dict:
    path = config_path or DEFAULT_CONFIG_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"MRS 配置文件不存在: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# ═══════════════════════════════════════════════════════════════
#  Extra feature extractors (beyond reality_metrics)
# ═══════════════════════════════════════════════════════════════

def _harsh_band_energy(mono: np.ndarray, sr: int,
                        f_low: float = 2500, f_high: float = 5000) -> float:
    """计算刺耳频段 (2.5-5kHz) 的能量占比."""
    n = len(mono)
    fft = np.abs(np.fft.rfft(mono * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    total = np.sum(fft ** 2) + EPS
    mask = (freqs >= f_low) & (freqs <= f_high)
    return float(np.sum(fft[mask] ** 2) / total)


def _spectral_slope(mono: np.ndarray, sr: int) -> float:
    """拟合频谱斜率 (dB/octave), 负值表示高频衰减."""
    n = len(mono)
    fft = np.abs(np.fft.rfft(mono * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    valid = (freqs > 100) & (freqs < sr / 2)
    if np.sum(valid) < 10:
        return 0.0
    log_f = np.log2(freqs[valid])
    db_spec = 20.0 * np.log10(fft[valid] + EPS)
    slope = float(np.polyfit(log_f, db_spec, 1)[0])
    return slope


def _zero_crossing_rate(mono: np.ndarray) -> float:
    """归一化过零率."""
    if len(mono) < 2:
        return 0.0
    crossings = np.sum(np.abs(np.diff(np.sign(mono)))) / 2
    return float(crossings / len(mono))


def _harmonic_noise_ratio(mono: np.ndarray, sr: int) -> float:
    """简化的谐波/噪声比估计.

    通过检测频谱的周期性峰值结构来估计.
    """
    n = len(mono)
    fft = np.abs(np.fft.rfft(mono * np.hanning(n)))
    if len(fft) < 20:
        return 0.5
    # 简化: 用 cepstrum 峰值
    log_spec = np.log(fft + EPS)
    cep = np.fft.irfft(log_spec)
    if len(cep) < 10:
        return 0.5
    peak = float(np.max(cep[1:min(200, len(cep))]))
    rms_cep = float(np.sqrt(np.mean(cep[50:] ** 2)) + EPS)
    hn_ratio = peak / rms_cep
    return float(np.clip(hn_ratio / 10.0, 0.0, 1.0))


def _spectral_contrast(mono: np.ndarray, sr: int) -> float:
    """频谱对比度: 峰值频带 vs 谷值频带的能量比."""
    n = len(mono)
    fft = np.abs(np.fft.rfft(mono * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1.0 / sr)

    bands = [(200, 500), (500, 2000), (2000, 5000), (5000, 8000)]
    peaks = []
    valleys = []
    for f1, f2 in bands:
        mask = (freqs >= f1) & (freqs <= f2)
        if np.sum(mask) > 5:
            band_spec = fft[mask]
            sorted_spec = np.sort(band_spec)
            n_top = max(1, len(sorted_spec) // 10)
            peak = float(np.mean(sorted_spec[-n_top:]))
            valley = float(np.mean(sorted_spec[:n_top]))
            peaks.append(peak)
            valleys.append(valley + EPS)

    if not peaks:
        return 0.5
    contrast = float(np.mean([p / (v + EPS) for p, v in zip(peaks, valleys)]))
    return float(np.clip(contrast / 5.0, 0.0, 1.0))


def _compute_lufs_estimate(mono: np.ndarray, sr: int) -> float:
    """估算 LUFS (回退到 RMS dB)."""
    try:
        import pyloudnorm as pyln
        meter = pyln.Meter(sr)
        audio = mono if mono.ndim == 1 else mono
        return float(meter.integrated_loudness(audio))
    except (ImportError, Exception):
        rms = np.sqrt(np.mean(mono ** 2) + EPS)
        return float(20.0 * math.log10(rms))


def _short_time_energy_variance(mono: np.ndarray, sr: int) -> float:
    """短时能量方差 (50ms 窗口)."""
    win_len = int(0.05 * sr)
    hop = win_len // 2
    if len(mono) < win_len:
        return 0.0
    energies = []
    for i in range(0, len(mono) - win_len, hop):
        w = mono[i:i + win_len]
        energies.append(float(np.mean(w ** 2)))
    if len(energies) < 3:
        return 0.0
    return float(np.std(energies) / (np.mean(energies) + EPS))


# ═══════════════════════════════════════════════════════════════
#  Sub-Score Calculators (each returns 0-100 + explain)
# ═══════════════════════════════════════════════════════════════

def _clamp_score(v: float) -> float:
    return round(max(0.0, min(100.0, v)), 1)


def _spectral_reality_score(features: dict, cfg: dict) -> tuple[float, list[str]]:
    """频谱真实度: 质心/斜率/频带平衡是否自然."""
    spec = features.get("spectrum", {})
    explain: list[str] = []
    score = 100.0

    centroid_norm = spec.get("centroid_norm", 0.15)
    centroid_hz = centroid_norm * features.get("sample_rate", 44100) / 2

    hi_cent = cfg.get("spectrum", {}).get("high_centroid_hz", 4500)
    lo_cent = cfg.get("spectrum", {}).get("low_centroid_hz", 800)

    if centroid_hz > hi_cent:
        penalty = min(20, (centroid_hz - hi_cent) / 200)
        score -= penalty
        explain.append(f"谱质心偏高 ({centroid_hz:.0f}Hz), 声音偏亮偏尖")
    elif centroid_hz < lo_cent:
        penalty = min(20, (lo_cent - centroid_hz) / 80)
        score -= penalty
        explain.append(f"谱质心偏低 ({centroid_hz:.0f}Hz), 声音偏闷")
    else:
        explain.append(f"谱质心正常 ({centroid_hz:.0f}Hz)")

    # 频带平衡
    band_sub = spec.get("band_sub", 0.05)
    band_bass = spec.get("band_bass", 0.1)
    band_presence = spec.get("band_presence", 0.1)
    band_air = spec.get("band_air", 0.05)

    sub_db = 20.0 * math.log10(max(band_sub, EPS))
    bass_db = 20.0 * math.log10(max(band_bass, EPS))

    if sub_db < -30:
        score -= 10
        explain.append("极低频缺失, 缺少物理重量感")
    if bass_db < -18:
        score -= 8
        explain.append("低频偏薄, 缺乏温暖感")

    if band_presence > 0.3:
        score -= 10
        explain.append("中高频过强, 可能存在刺耳感")

    # 频谱斜率
    slope = features.get("_extra", {}).get("spectral_slope", -6)
    if slope > -3:
        score -= 8
        explain.append("频谱过平 (slope > -3dB/oct), 缺乏自然衰减")
    elif slope < -15:
        score -= 5
        explain.append("高频衰减过陡 (slope < -15dB/oct), 声音可能发闷")

    return _clamp_score(score), explain


def _dynamic_reality_score(features: dict, cfg: dict) -> tuple[float, list[str]]:
    """动态真实度: crest/dynamic range/瞬态是否自然."""
    dyn = features.get("dynamic", {})
    trans = features.get("transient", {})
    explain: list[str] = []
    score = 100.0

    crest = dyn.get("crest_factor", 4.0)
    dr = dyn.get("dynamic_range", 5.0)
    flux_mean = trans.get("spectral_flux_mean", 0.1)
    energy_change = trans.get("short_time_energy_change", 0.3)

    dyn_cfg = cfg.get("dynamics", {})
    crest_min = dyn_cfg.get("crest_ideal_min", 3.0)
    crest_max = dyn_cfg.get("crest_ideal_max", 8.0)
    dr_min = dyn_cfg.get("dynamic_range_ideal_min_db", 5)

    if crest < crest_min:
        penalty = min(25, (crest_min - crest) * 8)
        score -= penalty
        explain.append(f"动态被压扁 (crest={crest:.1f}), 音乐缺乏呼吸感")
    elif crest > crest_max:
        penalty = min(15, (crest - crest_max) * 2)
        score -= penalty
        explain.append(f"峰值过高 (crest={crest:.1f}), 可能存在削波风险")
    else:
        explain.append(f"动态正常 (crest={crest:.1f})")

    if dr < dr_min:
        penalty = min(20, (dr_min - dr) * 4)
        score -= penalty
        explain.append(f"动态范围过窄 (DR={dr:.1f}dB), 整首听起来太平")

    if flux_mean < 0.05:
        score -= 10
        explain.append("频谱变化极小, 缺乏音色演变")
    elif flux_mean > 0.5:
        score -= 5
        explain.append("频谱变化剧烈, 可能不稳定")

    if energy_change > 1.0:
        score -= 8
        explain.append("短时能量波动大, 段落衔接不平滑")

    return _clamp_score(score), explain


def _texture_reality_score(features: dict, cfg: dict) -> tuple[float, list[str]]:
    """质感真实度: 粗糙度/平滑度/尖峰/谐波."""
    tex = features.get("texture", {})
    extra = features.get("_extra", {})
    explain: list[str] = []
    score = 100.0

    roughness = tex.get("roughness_proxy", 0.05)
    hf_smooth = tex.get("hf_smoothness", 0.5)
    spike = tex.get("spike_score", 0.01)
    hn_ratio = extra.get("harmonic_noise_ratio", 0.5)
    zcr = extra.get("zero_crossing_rate", 0.05)
    spec_contrast = extra.get("spectral_contrast", 0.5)

    tex_cfg = cfg.get("texture", {})

    if roughness > tex_cfg.get("roughness_high", 0.15):
        penalty = min(20, (roughness - 0.15) * 100)
        score -= penalty
        explain.append(f"频谱粗糙度高 ({roughness:.3f}), 声音有毛刺感")
    else:
        explain.append(f"频谱粗糙度正常 ({roughness:.3f})")

    if spike > tex_cfg.get("spike_high", 0.05):
        score -= 12
        explain.append(f"频谱尖峰多 ({spike:.4f}), 存在数字化共振")

    # ZCR 过低 → 缺乏质感细节
    if zcr < tex_cfg.get("zcr_low", 0.02):
        score -= 8
        explain.append("过零率极低, 声音缺乏质感细节")
    elif zcr > tex_cfg.get("zcr_high", 0.15):
        score -= 5
        explain.append("过零率偏高, 信号可能噪声化")

    # 谐波/噪声比
    if hn_ratio < 0.2:
        score -= 10
        explain.append("谐波结构弱, 声音偏向噪声")
    elif hn_ratio > 0.6:
        explain.append(f"谐波结构清晰 (HNR={hn_ratio:.2f})")

    # 频谱对比度
    if spec_contrast < 0.2:
        score -= 8
        explain.append("频谱对比度低, 频带间缺乏层次")
    elif spec_contrast > 0.8:
        explain.append(f"频谱对比度高 ({spec_contrast:.2f}), 层次分明")

    score += 5 * hf_smooth  # 高频平滑加分
    return _clamp_score(score), explain


def _spatial_reality_score(features: dict, cfg: dict) -> tuple[float, list[str]]:
    """空间真实度: 宽度/相关/相位是否自然."""
    space = features.get("space", {})
    explain: list[str] = []
    score = 100.0

    corr = space.get("lr_correlation", 0.5)
    ms_ratio = space.get("mid_side_ratio", 0.5)
    width = space.get("stereo_width", 0.5)
    phase = space.get("phase_anomaly", 0.0)

    sp_cfg = cfg.get("spatial", {})
    corr_min = sp_cfg.get("correlation_ideal_min", 0.3)
    corr_max = sp_cfg.get("correlation_ideal_max", 0.85)

    if corr < corr_min:
        penalty = min(20, (corr_min - corr) * 40)
        score -= penalty
        explain.append(f"声道相关性极低 ({corr:.2f}), 声场过宽, 单声道兼容风险")
    elif corr > corr_max:
        penalty = min(15, (corr - corr_max) * 50)
        score -= penalty
        explain.append(f"声道相关性过高 ({corr:.2f}), 立体声场过窄")
    else:
        explain.append(f"立体声宽度正常 (corr={corr:.2f})")

    if phase > 0.3:
        score -= 15
        explain.append(f"相位异常 ({phase:.2f}), 可能存在反相问题")

    if ms_ratio > sp_cfg.get("side_ratio_high", 2.0):
        score -= 10
        explain.append(f"侧边能量过强 (M/S={ms_ratio:.2f}), 虚宽感")

    if width < 0.1:
        score -= 10
        explain.append(f"立体声宽度极窄 ({width:.3f}), 近乎单声道")

    # 单声道处理: 降级但不报错
    is_mono = abs(corr - 1.0) < 0.001 and abs(width) < 0.01
    if is_mono:
        score = min(score, 75.0)
        explain.append("单声道音频, 空间评分降级处理")

    return _clamp_score(score), explain


def _anti_fatigue_score(features: dict, cfg: dict) -> tuple[float, list[str]]:
    """听感疲劳风险: 反比指标 (越不疲劳分数越高)."""
    spec = features.get("spectrum", {})
    dyn = features.get("dynamic", {})
    extra = features.get("_extra", {})
    explain: list[str] = []
    score = 100.0

    harsh_ratio = extra.get("harsh_band_energy", 0.1)
    lufs = extra.get("lufs_estimate", -14)
    flatness = spec.get("flatness", 0.3)
    crest = dyn.get("crest_factor", 4.0)

    sp_cfg = cfg.get("spectrum", {})
    dyn_cfg = cfg.get("dynamics", {})

    # 刺耳频段
    if harsh_ratio > 0.25:
        penalty = min(25, (harsh_ratio - 0.25) * 100)
        score -= penalty
        explain.append(f"2.5-5kHz 能量过强 ({harsh_ratio:.1%}), 长时间听容易疲劳")
    elif harsh_ratio > 0.15:
        score -= 8
        explain.append(f"刺耳频段略高 ({harsh_ratio:.1%}), 持续听可能感到疲劳")

    # 响度
    if lufs > dyn_cfg.get("excessive_lufs", -9):
        score -= 15
        explain.append(f"响度过高 ({lufs:.1f} LUFS), 对耳朵有冲击")
    elif lufs < dyn_cfg.get("low_lufs", -23):
        score -= 5
        explain.append(f"响度偏低 ({lufs:.1f} LUFS), 需要主动调大音量")

    # 频谱平度
    if flatness > 0.7:
        score -= 12
        explain.append(f"频谱过平 ({flatness:.2f}), 缺乏自然起伏, 容易听觉疲劳")

    # 动态平坦
    if crest < 2.5:
        score -= 15
        explain.append(f"动态极端平坦 (crest={crest:.1f}), 全曲无喘息空间")

    return _clamp_score(score), explain


def _balance_score(features: dict, _cfg: dict) -> tuple[float, list[str]]:
    """综合平衡度: 各维度偏差的倒数."""
    sub_scores = {
        "spectral": features.get("_sub_spectral", 50),
        "dynamic": features.get("_sub_dynamic", 50),
        "texture": features.get("_sub_texture", 50),
        "spatial": features.get("_sub_spatial", 50),
        "fatigue": features.get("_sub_fatigue", 50),
    }
    vals = np.array(list(sub_scores.values()))
    std = float(np.std(vals))
    balance = 100.0 - std * 4
    explain = []
    if std > 10:
        explain.append(f"各维度不均衡 (std={std:.1f}), 某些维度明显短板")
    elif std < 5:
        explain.append(f"各维度非常均衡 (std={std:.1f})")
    else:
        explain.append(f"维度平衡度尚可 (std={std:.1f})")
    return _clamp_score(balance), explain


def _plastic_risk_score(features: dict, cfg: dict) -> tuple[float, list[str]]:
    """AI 塑料感风险: 0-100 (越高越像塑料)."""
    spec = features.get("spectrum", {})
    dyn = features.get("dynamic", {})
    space = features.get("space", {})
    trans = features.get("transient", {})
    extra = features.get("_extra", {})
    explain: list[str] = []
    risk = 0.0

    pc = cfg.get("plastic", {})

    # 1. 频谱太平 (AI 常见特征)
    flatness = spec.get("flatness", 0.3)
    if flatness > pc.get("flatness_trigger", 0.65):
        contrib = min(30, (flatness - 0.4) * 80)
        risk += contrib
        explain.append(f"频谱异常平坦 ({flatness:.2f}) → AI 频谱特征 +{contrib:.0f}")

    # 2. 动态过平 (过度压缩)
    crest = dyn.get("crest_factor", 4.0)
    if crest < pc.get("crest_trigger", 2.5):
        contrib = min(25, (2.5 - crest) * 15)
        risk += contrib
        explain.append(f"动态过度压缩 (crest={crest:.1f}) → 塑料感 +{contrib:.0f}")

    # 3. 声场过窄 (虚假 stereo)
    corr = space.get("lr_correlation", 0.5)
    if corr > pc.get("high_correlation_trigger", 0.9):
        contrib = min(15, (corr - 0.85) * 100)
        risk += contrib
        explain.append(f"声场过窄 (corr={corr:.2f}) → 空间塑料感 +{contrib:.0f}")

    # 4. 瞬态偏软 (AI 缺乏 attack)
    flux = trans.get("spectral_flux_mean", 0.1)
    if flux < 0.08:
        contrib = min(15, (0.08 - flux) * 200)
        risk += contrib
        explain.append(f"音色变化极小 (flux={flux:.3f}) → 缺乏生命力 +{contrib:.0f}")

    # 5. 高频亮但不通透 (harsh + low hn_ratio)
    harsh = extra.get("harsh_band_energy", 0.1)
    hn = extra.get("harmonic_noise_ratio", 0.5)
    if harsh > 0.2 and hn < 0.3:
        contrib = 15
        risk += contrib
        explain.append("高频亮但谐波弱 → 假亮感 (AI 典型特征) +15")

    return _clamp_score(risk), explain


# ═══════════════════════════════════════════════════════════════
#  Main MRS computation
# ═══════════════════════════════════════════════════════════════

def compute_mrs(audio_path: str, config_path: Optional[str] = None) -> dict:
    """计算单个音频文件的完整 MRS.

    Args:
        audio_path: WAV/MP3/FLAC 文件路径
        config_path: MRS 权重配置文件 (默认 configs/mrs_weights.yaml)

    Returns:
        {
            "audio_path": str,
            "duration_s": float,
            "sample_rate": int,
            "mrs": float,          # 0-100 总分
            "subscores": {...},     # 7 个子分数
            "raw_features": {...},  # 原始特征值
            "explain": [...]        # 自然语言解释
        }
    """
    cfg = _load_config(config_path)
    weights = cfg.get("weights", {})
    score_cfg = cfg.get("scoring", {})

    # ── 输入验证 ────────────────────────────────────
    if not os.path.exists(audio_path):
        return {
            "audio_path": audio_path,
            "error": f"文件不存在: {audio_path}",
            "mrs": 0.0,
            "subscores": {},
            "explain": ["文件不存在"],
        }

    # ── 特征提取 ────────────────────────────────────
    try:
        mono, stereo, sr = _load_mono_stereo(audio_path)
    except Exception as e:
        return {
            "audio_path": audio_path,
            "error": f"音频加载失败: {e}",
            "mrs": 0.0,
            "subscores": {},
            "explain": [f"音频加载失败: {e}"],
        }

    duration = len(mono) / sr
    if duration < score_cfg.get("min_duration_s", 0.5):
        return {
            "audio_path": audio_path,
            "duration_s": duration,
            "sample_rate": sr,
            "mrs": 0.0,
            "subscores": {"error": "音频过短"},
            "explain": [f"音频过短 ({duration:.1f}s), 无法可靠评估"],
        }

    # 静音检测
    rms = float(np.sqrt(np.mean(mono ** 2)))
    rms_db = 20.0 * math.log10(rms + EPS)
    if rms_db < score_cfg.get("silence_threshold_db", -60):
        return {
            "audio_path": audio_path,
            "duration_s": duration,
            "sample_rate": sr,
            "mrs": 0.0,
            "subscores": {},
            "raw_features": {"rms_db": round(rms_db, 1)},
            "explain": [f"静音或极低信号 (RMS={rms_db:.1f}dB)"],
        }

    # 核心特征 (复用 reality_metrics)
    spec = _spectrum_features(mono, sr)
    dyn = _dynamic_features(mono, sr)
    trans = _transient_features(mono, sr)
    space = _space_features(stereo)
    tex = _texture_features(mono, sr)

    # 扩展特征
    extra = {
        "harsh_band_energy": _harsh_band_energy(mono, sr),
        "spectral_slope": _spectral_slope(mono, sr),
        "zero_crossing_rate": _zero_crossing_rate(mono),
        "harmonic_noise_ratio": _harmonic_noise_ratio(mono, sr),
        "spectral_contrast": _spectral_contrast(mono, sr),
        "lufs_estimate": _compute_lufs_estimate(mono, sr),
        "short_time_energy_variance": _short_time_energy_variance(mono, sr),
    }

    features = {
        "spectrum": spec,
        "dynamic": dyn,
        "transient": trans,
        "space": space,
        "texture": tex,
        "sample_rate": sr,
        "_extra": extra,
    }

    # ── 子指标计算 ──────────────────────────────────
    all_explain: list[str] = []
    subscores: dict[str, float] = {}

    sub_spectral, exp_spec = _spectral_reality_score(features, cfg)
    subscores["spectral_reality"] = sub_spectral
    all_explain.extend(exp_spec)
    features["_sub_spectral"] = sub_spectral

    sub_dynamic, exp_dyn = _dynamic_reality_score(features, cfg)
    subscores["dynamic_reality"] = sub_dynamic
    all_explain.extend(exp_dyn)
    features["_sub_dynamic"] = sub_dynamic

    sub_texture, exp_tex = _texture_reality_score(features, cfg)
    subscores["texture_reality"] = sub_texture
    all_explain.extend(exp_tex)
    features["_sub_texture"] = sub_texture

    sub_spatial, exp_spa = _spatial_reality_score(features, cfg)
    subscores["spatial_reality"] = sub_spatial
    all_explain.extend(exp_spa)
    features["_sub_spatial"] = sub_spatial

    sub_fatigue, exp_fat = _anti_fatigue_score(features, cfg)
    subscores["anti_fatigue"] = sub_fatigue
    all_explain.extend(exp_fat)
    features["_sub_fatigue"] = sub_fatigue

    sub_balance, exp_bal = _balance_score(features, cfg)
    subscores["balance_score"] = sub_balance
    all_explain.extend(exp_bal)

    plastic, exp_pla = _plastic_risk_score(features, cfg)
    subscores["plastic_risk"] = plastic
    all_explain.extend(exp_pla)

    # ── 总分计算 ────────────────────────────────────
    mrs = (
        weights.get("spectral_reality", 0.22) * subscores["spectral_reality"]
        + weights.get("dynamic_reality", 0.20) * subscores["dynamic_reality"]
        + weights.get("texture_reality", 0.18) * subscores["texture_reality"]
        + weights.get("spatial_reality", 0.15) * subscores["spatial_reality"]
        + weights.get("anti_fatigue", 0.15) * subscores["anti_fatigue"]
        + weights.get("balance_score", 0.10) * subscores["balance_score"]
        - weights.get("plastic_risk_penalty", 0.25) * subscores["plastic_risk"]
    )
    mrs = _clamp_score(mrs)

    # ── 构建 raw_features (标准化输出) ──────────────
    raw = {
        "duration_s": round(duration, 1),
        "sample_rate": sr,
        "spectral_centroid_hz": round(spec.get("centroid_norm", 0) * sr / 2, 1),
        "spectral_flatness": round(spec.get("flatness", 0), 4),
        "spectral_slope_db_oct": round(extra.get("spectral_slope", 0), 2),
        "crest_factor": round(dyn.get("crest_factor", 0), 2),
        "dynamic_range_db": round(dyn.get("dynamic_range", 0), 1),
        "lufs_estimate": round(extra.get("lufs_estimate", 0), 1),
        "lr_correlation": round(space.get("lr_correlation", 0), 3),
        "stereo_width": round(space.get("stereo_width", 0), 3),
        "mid_side_ratio": round(space.get("mid_side_ratio", 0), 3),
        "roughness_proxy": round(tex.get("roughness_proxy", 0), 4),
        "harmonic_noise_ratio": round(extra.get("harmonic_noise_ratio", 0), 3),
        "zero_crossing_rate": round(extra.get("zero_crossing_rate", 0), 4),
        "harsh_band_energy": round(extra.get("harsh_band_energy", 0), 4),
        "spectral_contrast": round(extra.get("spectral_contrast", 0), 3),
        "rms_db": round(20.0 * math.log10(rms + EPS), 1),
    }

    return {
        "audio_path": audio_path,
        "duration_s": round(duration, 1),
        "sample_rate": sr,
        "mrs": mrs,
        "subscores": {k: round(v, 1) for k, v in subscores.items()},
        "raw_features": raw,
        "explain": all_explain,
    }


# ═══════════════════════════════════════════════════════════════
#  Batch convenience
# ═══════════════════════════════════════════════════════════════

def compute_mrs_batch(audio_paths: list[str],
                       config_path: Optional[str] = None) -> list[dict]:
    """批量计算 MRS.

    Args:
        audio_paths: 音频文件路径列表
        config_path: MRS 配置路径

    Returns:
        [{compute_mrs result}, ...]
    """
    return [compute_mrs(p, config_path) for p in audio_paths]
