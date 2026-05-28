"""
operators.py — Moodify 处理算子模块
=====================================
GCS-001 第 9 节：T(θ): W_raw → W_processed

每个算子接收 (audio, sr, params) → 返回 processed_audio。
所有算子都是纯函数，无副作用，输出与输入同 shape。
"""

from __future__ import annotations

import numpy as np
from scipy.signal import sosfilt, butter, lfilter
from scipy.signal import convolve


# ============================================================
#  EQ — 参数均衡器 (FFT-based, correct shelf/peak)
# ============================================================

def apply_eq(audio: np.ndarray, sr: int,
             bands: dict[str, float] | None = None,
             low_shelf_gain_db: float = 0.0,
             low_shelf_freq: float = 200.0,
             high_shelf_gain_db: float = 0.0,
             high_shelf_freq: float = 6000.0,
             peak_freq: float = 1000.0,
             peak_gain_db: float = 0.0,
             peak_q: float = 1.0) -> np.ndarray:
    """
    频域 EQ：low shelf + peaking + high shelf。

    使用 FFT 在频域直接构造幅频响应曲线，避免 IIR 滤波器设计误差。
    """
    result = audio.copy()
    is_stereo = result.ndim > 1

    if bands:
        for band_name, gain_db in bands.items():
            if band_name in ("Sub", "Bass"):
                low_shelf_gain_db += gain_db * 0.5
            elif band_name == "Air":
                high_shelf_gain_db += gain_db * 0.5
            elif band_name == "Presence":
                peak_freq, peak_gain_db = 3500.0, peak_gain_db + gain_db * 0.5
            elif band_name == "Mid":
                peak_freq, peak_gain_db = 1000.0, peak_gain_db + gain_db * 0.5
            elif band_name == "Low-Mid":
                peak_freq, peak_gain_db = 350.0, peak_gain_db + gain_db * 0.3

    # 如果没有任何调整，直接返回
    if (abs(low_shelf_gain_db) < 0.1 and abs(high_shelf_gain_db) < 0.1
            and abs(peak_gain_db) < 0.1):
        return result

    # 对每声道逐块 FFT 处理（大文件分块避免内存爆炸）
    block_s = 4.0  # 4 秒块
    block_len = int(block_s * sr)
    overlap = block_len // 4  # 25% overlap for smooth transitions

    def _process_channel(signal):
        n = len(signal)
        out = np.zeros(n)
        weight = np.zeros(n)  # overlap-add weights

        pos = 0
        while pos < n:
            end = min(pos + block_len, n)
            chunk = signal[pos:end]
            chunk_len = len(chunk)

            # FFT
            X = np.fft.rfft(chunk, n=block_len * 2)
            freqs = np.fft.rfftfreq(block_len * 2, 1.0 / sr)

            # 构造幅频响应曲线
            response = np.ones(len(freqs))
            response = _apply_shelf_freq(response, freqs, low_shelf_freq,
                                         low_shelf_gain_db, "low")
            response = _apply_shelf_freq(response, freqs, high_shelf_freq,
                                         high_shelf_gain_db, "high")
            response = _apply_peak_freq(response, freqs, peak_freq,
                                        peak_gain_db, peak_q)

            # 应用响应
            Y = X * response
            y_chunk = np.fft.irfft(Y, n=block_len * 2)[:chunk_len]

            # 重叠相加
            fade = np.ones(chunk_len)
            if pos > 0:
                fade[:overlap] = np.linspace(0, 1, overlap)
            if end < n:
                fade[-overlap:] = np.linspace(1, 0, overlap)
            out[pos:end] += y_chunk * fade

            pos += block_len - overlap

        return out

    if is_stereo:
        for ch in range(result.shape[1]):
            result[:, ch] = _process_channel(result[:, ch])
    else:
        result = _process_channel(result)

    # 防止削波
    peak = np.max(np.abs(result))
    if peak > 0.98:
        result *= 0.98 / peak

    return result


def _apply_shelf_freq(response, freqs, freq, gain_db, stype):
    """在频域响应上施加 shelf 曲线。"""
    if abs(gain_db) < 0.1:
        return response
    gain_lin = 10.0 ** (gain_db / 20.0)
    # 平滑过渡：用 sigmoid 在 freq 附近过渡
    # transition width: 1 octave
    if stype == "low":
        curve = 1.0 + (gain_lin - 1.0) * (1.0 / (1.0 + np.exp((freqs - freq) / (freq * 0.3))))
    else:  # high
        curve = 1.0 + (gain_lin - 1.0) * (1.0 / (1.0 + np.exp(-(freqs - freq) / (freq * 0.3))))
    return response * curve


def _apply_peak_freq(response, freqs, freq, gain_db, q):
    """在频域响应上施加 peaking 曲线。"""
    if abs(gain_db) < 0.1:
        return response
    gain_lin = 10.0 ** (gain_db / 20.0)
    bw = freq / max(q, 0.1)
    # Gaussian-shaped peak
    curve = 1.0 + (gain_lin - 1.0) * np.exp(-((freqs - freq) / bw) ** 2)
    return response * curve


# ============================================================
#  Compressor — 动态压缩器
# ============================================================

def apply_compressor(audio: np.ndarray, sr: int,
                     threshold_db: float = -18.0,
                     ratio: float = 2.0,
                     attack_ms: float = 10.0,
                     release_ms: float = 200.0,
                     makeup_gain_db: float = 0.0) -> np.ndarray:
    """
    前馈 RMS 压缩器。

    threshold_db : 阈值 (dBFS)，超过此值开始压缩
    ratio        : 压缩比，2.0 = 2:1
    attack_ms    : 起音时间 (ms)
    release_ms   : 释音时间 (ms)
    """
    result = audio.copy()
    is_stereo = result.ndim > 1

    if is_stereo:
        mono = result.mean(axis=1)
    else:
        mono = result

    # RMS 检测（attack/release 平滑）
    attack_coeff  = np.exp(-1.0 / (attack_ms * sr / 1000.0))
    release_coeff = np.exp(-1.0 / (release_ms * sr / 1000.0))

    rms_smooth = 0.0
    gain_reduction = np.ones(len(mono))

    for n in range(len(mono)):
        rect = mono[n] ** 2
        if rect > rms_smooth:
            rms_smooth = attack_coeff * rms_smooth + (1 - attack_coeff) * rect
        else:
            rms_smooth = release_coeff * rms_smooth + (1 - release_coeff) * rect

        level_db = 10.0 * np.log10(rms_smooth + 1e-12)
        if level_db > threshold_db:
            overshoot = level_db - threshold_db
            reduction_db = overshoot * (1.0 - 1.0 / ratio)
            gain_reduction[n] = 10.0 ** (-reduction_db / 20.0)
        else:
            gain_reduction[n] = 1.0

    # 平滑增益曲线（避免突变）
    from scipy.ndimage import uniform_filter1d
    smooth_len = int(sr * 0.002)  # 2ms smoothing
    smooth_len = max(3, smooth_len)
    gain_reduction = uniform_filter1d(gain_reduction, smooth_len)

    # 应用增益 + makeup
    makeup_lin = 10.0 ** (makeup_gain_db / 20.0)
    if is_stereo:
        for ch in range(result.shape[1]):
            result[:, ch] *= gain_reduction * makeup_lin
    else:
        result *= gain_reduction * makeup_lin

    return result


# ============================================================
#  Reverb — 混响
# ============================================================

def apply_reverb(audio: np.ndarray, sr: int,
                 rt60_s: float = 1.5,
                 dry_wet: float = 0.3,
                 pre_delay_ms: float = 30.0) -> np.ndarray:
    """
    Schroeder 型简易混响。

    rt60_s      : RT60 混响时间 (秒)
    dry_wet     : 湿信号比例 [0, 1]
    pre_delay_ms: 预延迟 (ms)
    """
    result = audio.copy()
    is_stereo = result.ndim > 1
    if is_stereo:
        mono = result.mean(axis=1)
    else:
        mono = result

    # 预延迟
    delay_samp = int(pre_delay_ms * sr / 1000.0)
    if delay_samp > 0:
        delayed = np.pad(mono[:-delay_samp] if len(mono) > delay_samp else mono,
                         (delay_samp, 0), mode="constant")
    else:
        delayed = mono

    # Schroeder 混响：4 个梳状滤波器 + 2 个全通
    # 简化版
    reverb_signal = _schroeder_reverb(delayed, sr, rt60_s)

    # 干湿混合
    wet_gain = dry_wet
    dry_gain = 1.0 - dry_wet
    mixed = dry_gain * mono + wet_gain * reverb_signal[:len(mono)]

    if is_stereo:
        # 左右略有差异
        reverb_r = _schroeder_reverb(delayed, sr, rt60_s * 1.1)
        for ch in range(result.shape[1]):
            rv = reverb_signal if ch == 0 else reverb_r
            result[:, ch] = dry_gain * result[:, ch] + wet_gain * rv[:len(mono)]
    else:
        result = mixed

    # 防止削波
    peak = np.max(np.abs(result))
    if peak > 0.95:
        result *= 0.95 / peak

    return result


def _schroeder_reverb(signal: np.ndarray, sr: int, rt60: float) -> np.ndarray:
    """简化 Schroeder 混响器。"""
    # 梳状滤波器延迟长度（素数，避免共振）
    comb_delays = [int(sr * d) for d in [0.0297, 0.0371, 0.0411, 0.0437]]
    comb_gains  = [10.0 ** (-3.0 * d / rt60) for d in [0.0297, 0.0371, 0.0411, 0.0437]]

    output = np.zeros(len(signal) + max(comb_delays) + 2000)
    for delay, gain in zip(comb_delays, comb_gains):
        for n in range(len(signal)):
            output[n + delay] += signal[n] * gain
            if n + delay < len(output) - delay:
                output[n + delay] += output[n] * gain * 0.5

    return output[:len(signal) + 2000]


# ============================================================
#  Stereo Enhancer — 立体声增强
# ============================================================

def apply_stereo_enhancer(audio: np.ndarray, sr: int,
                          width: float = 1.0) -> np.ndarray:
    """
    M/S 立体声宽度控制。

    width = 0.0 → 纯单声道
    width = 1.0 → 原始宽度
    width = 2.0 → 宽度加倍
    """
    if audio.ndim < 2 or audio.shape[1] < 2:
        return audio

    mid  = (audio[:, 0] + audio[:, 1]) / 2.0
    side = (audio[:, 0] - audio[:, 1]) / 2.0

    side *= width

    result = np.zeros_like(audio)
    result[:, 0] = mid + side
    result[:, 1] = mid - side
    return result


# ============================================================
#  Limiter — 峰值限制器
# ============================================================

def apply_limiter(audio: np.ndarray, sr: int,
                  ceiling_db: float = -1.0,
                  release_ms: float = 50.0) -> np.ndarray:
    """
    砖墙限幅器。防止削波。

    ceiling_db : 输出上限 (dBFS)
    """
    result = audio.copy()
    ceiling = 10.0 ** (ceiling_db / 20.0)
    release_coeff = np.exp(-1.0 / (release_ms * sr / 1000.0))

    is_stereo = result.ndim > 1
    if is_stereo:
        env = np.max(np.abs(result), axis=1)
    else:
        env = np.abs(result)

    gain = np.ones(len(env))
    gr_smooth = 1.0
    for n in range(len(env)):
        target_gain = min(1.0, ceiling / (env[n] + 1e-12))
        if target_gain < gr_smooth:
            gr_smooth = target_gain  # attack instant
        else:
            gr_smooth = release_coeff * gr_smooth + (1 - release_coeff) * target_gain
        gain[n] = gr_smooth

    if is_stereo:
        result[:, 0] *= gain
        result[:, 1] *= gain
    else:
        result *= gain

    return result


# ============================================================
#  算子注册表
# ============================================================

OPERATOR_REGISTRY = {
    "eq":                apply_eq,
    "compressor":        apply_compressor,
    "reverb":            apply_reverb,
    "stereo_enhancer":   apply_stereo_enhancer,
    "limiter":           apply_limiter,
}


def apply_chain(audio: np.ndarray, sr: int,
                steps: list[dict]) -> np.ndarray:
    """
    按顺序执行工艺链。

    steps = [
        {"op": "eq", "params": {"high_shelf_gain_db": -3.0}},
        {"op": "compressor", "params": {"ratio": 2.0}},
        {"op": "limiter", "params": {}},
    ]
    """
    result = audio.copy()
    for step in steps:
        op_name = step["op"]
        params = step.get("params", {})
        if op_name in OPERATOR_REGISTRY:
            result = OPERATOR_REGISTRY[op_name](result, sr, **params)
        else:
            raise ValueError(f"Unknown operator: {op_name}")
    return result
