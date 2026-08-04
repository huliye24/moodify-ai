"""
operators.py — Moodify 处理算子模块
=====================================
GCS-001 第 9 节：T(θ): W_raw → W_processed

每个算子接收 (audio, sr, params) → 返回 processed_audio。
所有算子都是纯函数，无副作用，输出与输入同 shape。
"""

from __future__ import annotations

import numpy as np

from moodify.processing.rbj_eq import (
    apply_rbj_eq,
)


# ============================================================
#  EQ — 参数均衡器
#     mode="rbj" (default) → RBJ biquad (AEP-ACU-002)
#     mode="legacy_fft"    → 旧 FFT sigmoid/Gaussian (deprecated)
# ============================================================

def _resolve_eq_params(bands: dict[str, float] | None,
                       low_shelf_gain_db, low_shelf_freq,
                       high_shelf_gain_db, high_shelf_freq,
                       peak_freq, peak_gain_db, peak_q):
    """Convert semantic band names → EQ parameters. Returns (ls_gain, ls_freq, hs_gain, hs_freq, pf, pg, pq)."""
    if not bands:
        return low_shelf_gain_db, low_shelf_freq, high_shelf_gain_db, high_shelf_freq, peak_freq, peak_gain_db, peak_q
    for name, g in bands.items():
        if name in ("Sub", "Bass"):
            low_shelf_gain_db += g * 0.5
        elif name == "Air":
            high_shelf_gain_db += g * 0.5
        elif name == "Presence":
            peak_freq, peak_gain_db = 3500.0, peak_gain_db + g * 0.5
        elif name == "Mid":
            peak_freq, peak_gain_db = 1000.0, peak_gain_db + g * 0.5
        elif name == "Low-Mid":
            peak_freq, peak_gain_db = 350.0, peak_gain_db + g * 0.3
    return low_shelf_gain_db, low_shelf_freq, high_shelf_gain_db, high_shelf_freq, peak_freq, peak_gain_db, peak_q


def apply_eq(audio: np.ndarray, sr: int,
             bands: dict[str, float] | None = None,
             low_shelf_gain_db: float = 0.0, low_shelf_freq: float = 200.0,
             high_shelf_gain_db: float = 0.0, high_shelf_freq: float = 6000.0,
             peak_freq: float = 1000.0, peak_gain_db: float = 0.0,
             peak_q: float = 1.0,
             mode: str = "rbj") -> np.ndarray:
    """参数均衡器：low shelf + peaking + high shelf.

    mode="rbj" (default):  RBJ biquad standard filters (AEP-ACU-002).
    mode="legacy_fft":     旧 FFT sigmoid/Gaussian EQ (deprecated, 保留用于 A/B 测试).
    """
    low_shelf_gain_db, low_shelf_freq, high_shelf_gain_db, high_shelf_freq, \
        peak_freq, peak_gain_db, peak_q = _resolve_eq_params(
        bands, low_shelf_gain_db, low_shelf_freq,
        high_shelf_gain_db, high_shelf_freq, peak_freq, peak_gain_db, peak_q)

    # 零增益快速路径
    if (abs(low_shelf_gain_db) < 0.1 and abs(high_shelf_gain_db) < 0.1
            and abs(peak_gain_db) < 0.1):
        return audio.copy()

    if mode == "rbj":
        return _apply_eq_rbj(
            audio, sr,
            low_shelf_gain_db, low_shelf_freq,
            high_shelf_gain_db, high_shelf_freq,
            peak_freq, peak_gain_db, peak_q,
        )
    elif mode == "legacy_fft":
        return _apply_eq_legacy_fft(
            audio, sr,
            low_shelf_gain_db, low_shelf_freq,
            high_shelf_gain_db, high_shelf_freq,
            peak_freq, peak_gain_db, peak_q,
        )
    else:
        raise ValueError(f"Unknown EQ mode: {mode!r}. Must be 'rbj' or 'legacy_fft'.")


def _apply_eq_rbj(audio, sr,
                  ls_gain, ls_freq, hs_gain, hs_freq,
                  pk_freq, pk_gain, pk_q):
    """RBJ biquad EQ path (AEP-ACU-002)."""
    filters = []
    if abs(ls_gain) >= 0.1:
        filters.append({"type": "low_shelf", "freq_hz": ls_freq,
                         "gain_db": ls_gain, "q": 0.707})
    if abs(pk_gain) >= 0.1:
        filters.append({"type": "peaking", "freq_hz": pk_freq,
                         "gain_db": pk_gain, "q": pk_q})
    if abs(hs_gain) >= 0.1:
        filters.append({"type": "high_shelf", "freq_hz": hs_freq,
                         "gain_db": hs_gain, "q": 0.707})
    return apply_rbj_eq(audio, float(sr), filters)


def _apply_eq_legacy_fft(audio, sr,
                         ls_gain, ls_freq, hs_gain, hs_freq,
                         pk_freq, pk_gain, pk_q):
    """[DEPRECATED] 旧 FFT sigmoid/Gaussian EQ — 保留用于 A/B 测试.

    .. deprecated::
        自 AEP-ACU-002 (2026-07-03) 起废弃。
        新代码请使用 mode="rbj" (default)。
    """
    import warnings
    warnings.warn(
        "Legacy FFT EQ is deprecated. Use mode='rbj' instead.",
        DeprecationWarning, stacklevel=2,
    )
    result = audio.copy()
    is_stereo = result.ndim > 1

    block_s = 4.0
    block_len = int(block_s * sr)
    overlap = block_len // 4

    def _process_channel(signal):
        n = len(signal)
        out = np.zeros(n)
        pos = 0
        while pos < n:
            end = min(pos + block_len, n)
            chunk = signal[pos:end]
            chunk_len = len(chunk)
            X = np.fft.rfft(chunk, n=block_len * 2)
            freqs = np.fft.rfftfreq(block_len * 2, 1.0 / sr)
            response = np.ones(len(freqs))
            response = _apply_shelf_freq_legacy(response, freqs, ls_freq, ls_gain, "low")
            response = _apply_shelf_freq_legacy(response, freqs, hs_freq, hs_gain, "high")
            response = _apply_peak_freq_legacy(response, freqs, pk_freq, pk_gain, pk_q)
            Y = X * response
            y_chunk = np.fft.irfft(Y, n=block_len * 2)[:chunk_len]
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

    peak = np.max(np.abs(result))
    if peak > 0.98:
        result *= 0.98 / peak
    return result


def _apply_shelf_freq_legacy(response, freqs, freq, gain_db, stype):
    """[DEPRECATED] 在频域响应上施加 sigmoid shelf 曲线。"""
    if abs(gain_db) < 0.1:
        return response
    gain_lin = 10.0 ** (gain_db / 20.0)
    if stype == "low":
        curve = 1.0 + (gain_lin - 1.0) * (1.0 / (1.0 + np.exp((freqs - freq) / (freq * 0.3))))
    else:  # high
        curve = 1.0 + (gain_lin - 1.0) * (1.0 / (1.0 + np.exp(-(freqs - freq) / (freq * 0.3))))
    return response * curve


def _apply_peak_freq_legacy(response, freqs, freq, gain_db, q):
    """[DEPRECATED] 在频域响应上施加 Gaussian peaking 曲线。"""
    if abs(gain_db) < 0.1:
        return response
    gain_lin = 10.0 ** (gain_db / 20.0)
    bw = freq / max(q, 0.1)
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


def _schroeder_reverb_legacy(signal: np.ndarray, sr: int, rt60: float) -> np.ndarray:
    """[DEPRECATED] 旧版 Schroeder 混响器 — 非标准交叉耦合反馈 + 缺少全通级.

    .. deprecated::
        自 AEP-ACU-001 (2026-07-02) 起废弃。
        保留用于 A/B 对比和回归测试。
        新代码请使用 :func:`_schroeder_reverb`。
    """
    import warnings
    warnings.warn(
        "_schroeder_reverb_legacy is deprecated. Use _schroeder_reverb instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    comb_delays = [int(sr * d) for d in [0.0297, 0.0371, 0.0411, 0.0437]]
    comb_gains = [10.0 ** (-3.0 * d / rt60) for d in [0.0297, 0.0371, 0.0411, 0.0437]]

    output = np.zeros(len(signal) + max(comb_delays) + 2000)
    for delay, gain in zip(comb_delays, comb_gains):
        for n in range(len(signal)):
            output[n + delay] += signal[n] * gain
            if n + delay < len(output) - delay:
                output[n + delay] += output[n] * gain * 0.5

    return output[:len(signal) + 2000]


def _feedback_comb_filter(
    signal: np.ndarray, sr: int, delay_s: float, rt60: float,
) -> np.ndarray:
    """标准反馈梳状滤波器: y[n] = x[n] + g * y[n-D].

    Args:
        signal: 输入信号 (1D).
        sr: 采样率.
        delay_s: 延迟时间 (秒). 通常 30-45 ms.
        rt60: RT60 混响时间 (秒). 用于计算反馈增益.

    Returns:
        梳状滤波器输出, 长度 = len(signal) + delay_samples (含混响尾音).
    """
    delay_samples = int(sr * delay_s)
    if delay_samples < 1:
        delay_samples = 1
    # g = 10^(-3 * delay / rt60) — 确保 rt60 秒后衰减 60 dB
    gain = 10.0 ** (-3.0 * delay_s / max(rt60, 0.01))
    gain = float(np.clip(gain, 0.0, 0.999))

    n_in = len(signal)
    n_out = n_in + delay_samples
    y = np.zeros(n_out, dtype=signal.dtype)

    for n in range(n_out):
        # feedforward: x[n] (past input → 0)
        x_n = signal[n] if n < n_in else 0.0
        # feedback: g * y[n-D]
        fb = gain * y[n - delay_samples] if n >= delay_samples else 0.0
        y[n] = x_n + fb

    return y


def _allpass_filter(
    signal: np.ndarray, sr: int, delay_s: float, gain: float = 0.7,
) -> np.ndarray:
    """全通滤波器: y[n] = -g*x[n] + x[n-D] + g*y[n-D].

    幅频响应为常数 1 (理论)。改变相位和时域扩散。

    Args:
        signal: 输入信号 (1D).
        sr: 采样率.
        delay_s: 延迟时间 (秒). 通常 1-5 ms.
        gain: 反馈/前馈增益系数 (0 < g < 1). 推荐 0.5-0.7.

    Returns:
        与输入同长度的全通滤波器输出.
    """
    delay_samples = int(sr * delay_s)
    if delay_samples < 1:
        delay_samples = 1
    g = float(np.clip(gain, 0.0, 0.999))

    n_in = len(signal)
    output = np.zeros(n_in, dtype=signal.dtype)

    for n in range(n_in):
        # 前馈: -g * x[n] + x[n-D]
        feedforward = -g * signal[n]
        if n >= delay_samples:
            feedforward += signal[n - delay_samples]
        # 反馈: + g * y[n-D]
        feedback = 0.0
        if n >= delay_samples:
            feedback = g * output[n - delay_samples]
        output[n] = feedforward + feedback

    return output


def _schroeder_reverb(signal: np.ndarray, sr: int, rt60: float) -> np.ndarray:
    """Schroeder 型人工混响 — 标准反馈梳状 + 全通级 (AEP-ACU-001 合规修复).

    架构: parallel comb filters → serial all-pass stages

    参照: Schroeder, M. R. (1962). "Natural Sounding Artificial
    Reverberation." *JAES*, 10(3), 219-223.

    Args:
        signal: 输入信号 (1D).
        sr: 采样率 (Hz).
        rt60: RT60 混响时间 (秒).

    Returns:
        混响信号 (长度 = len(signal) + 约 50 ms 的尾音扩展).
    """
    # ── 4 并联反馈梳状滤波器 ──
    # 延迟长度基于质数 (避免谐波共振)
    comb_delays_s = [0.0297, 0.0371, 0.0411, 0.0437]

    # 并行处理：每个 comb 的输入都是从预延迟信号分出的同一路
    comb_outputs = []
    for d in comb_delays_s:
        comb_out = _feedback_comb_filter(signal, sr, d, rt60)
        comb_outputs.append(comb_out)

    # 求和所有 comb 输出
    max_len = max(len(co) for co in comb_outputs)
    summed = np.zeros(max_len, dtype=signal.dtype)
    for co in comb_outputs:
        summed[:len(co)] += co

    # ── 2 串联全通滤波器 ──
    ap1 = _allpass_filter(summed, sr, delay_s=0.0050, gain=0.70)
    ap2 = _allpass_filter(ap1, sr, delay_s=0.0017, gain=0.70)

    return ap2


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
#  Limiter — True-Peak 限制器 (AEP-ACU-005)
# ============================================================

def apply_limiter(audio: np.ndarray, sr: int,
                  ceiling_db: float = -1.0,
                  release_ms: float = 50.0,
                  attack_ms: float = 1.0,
                  mode: str = "true_peak") -> np.ndarray:
    """True-peak brickwall limiter with non-zero attack (AEP-ACU-005).

    mode="true_peak" (default): 4x oversampling + attack/release envelope.
    mode="legacy":             旧版零 attack sample-peak limiter (deprecated).
    """
    if mode == "legacy":
        return _apply_limiter_legacy(audio, sr, ceiling_db, release_ms)

    from moodify.processing.limiter import apply_limiter_tp
    result, _audit = apply_limiter_tp(
        audio, sr,
        ceiling_dbtp=ceiling_db,
        attack_ms=attack_ms,
        release_ms=release_ms,
    )
    return result


def _apply_limiter_legacy(audio: np.ndarray, sr: int,
                          ceiling_db: float = -1.0,
                          release_ms: float = 50.0) -> np.ndarray:
    """[DEPRECATED] Legacy zero-attack sample-peak limiter.

    Preserved for A/B testing. Use apply_limiter(mode=\"true_peak\").
    """
    import warnings
    warnings.warn(
        "Legacy limiter (zero-attack) is deprecated. Use mode='true_peak'.",
        DeprecationWarning, stacklevel=2,
    )
    result = audio.copy().astype(np.float64)
    ceiling = 10.0 ** (ceiling_db / 20.0)
    release_coeff = np.exp(-1.0 / (release_ms * sr / 1000.0))

    is_stereo = result.ndim > 1
    if is_stereo:
        env = np.max(np.abs(result), axis=1)
    else:
        env = np.abs(result)

    gain = np.ones(len(env), dtype=np.float64)
    gr_smooth = 1.0
    for n in range(len(env)):
        target_gain = min(1.0, ceiling / max(env[n], 1e-15))
        if target_gain < gr_smooth:
            gr_smooth = target_gain  # zero attack
        else:
            gr_smooth = release_coeff * gr_smooth + (1.0 - release_coeff) * target_gain
        gain[n] = gr_smooth

    if is_stereo:
        result[:, 0] *= gain
        result[:, 1] *= gain
    else:
        result *= gain

    return np.clip(result, -1.0, 1.0).astype(audio.dtype)


# ============================================================
#  算子注册表
# ============================================================

OPERATOR_REGISTRY = {
    "eq":                apply_eq,
    "eq_legacy_fft":     lambda audio, sr, **kw: apply_eq(audio, sr, mode="legacy_fft", **kw),
    "compressor":        apply_compressor,
    "reverb":            apply_reverb,
    "stereo_enhancer":   apply_stereo_enhancer,
    "limiter":           apply_limiter,
    "limiter_legacy":    lambda audio, sr, **kw: apply_limiter(audio, sr, mode="legacy", **kw),
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
