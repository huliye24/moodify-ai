"""AEP-ACU-001: 脉冲响应与频率响应对比 — 旧 vs 新 Schroeder 混响.

生成:
  - data/ir_old_new.json  — 脉冲响应对比数据
  - data/freq_response_old_new.json — 频率响应对比数据
"""

import json
import os

import numpy as np


class _NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


SR = 44100


def generate_impulse(n_seconds=0.5):
    n = int(SR * n_seconds)
    sig = np.zeros(n, dtype=np.float32)
    sig[0] = 1.0
    return sig


def measure_ir_metrics(ir, sr, label):
    """提取脉冲响应的关键指标."""
    t_max = np.argmax(np.abs(ir))
    peak_db = 20 * np.log10(np.max(np.abs(ir)) + 1e-12)

    # RT60 估算: 从峰值衰减 -60 dB
    envelope = np.abs(ir[t_max:])
    # 平滑包络
    win = int(sr * 0.01)
    if win > 1 and len(envelope) > win:
        kernel = np.ones(win) / win
        envelope = np.convolve(envelope, kernel, mode="same")

    peak_val = envelope[0] if envelope[0] > 0 else 1e-6
    rt60_idx = None
    for i in range(1, len(envelope)):
        if envelope[i] < peak_val * 1e-3:  # -60 dB
            rt60_idx = i
            break

    rt60_est = rt60_idx / sr if rt60_idx is not None else float("nan")

    # 回声密度 (简化): 50-200 ms 内的峰值数量
    a, b = int(sr * 0.05), int(sr * 0.20)
    if b < len(ir):
        tail = np.abs(ir[a:b])
        threshold = np.mean(tail) * 2
        peaks = np.sum(
            (tail[1:-1] > tail[:-2]) & (tail[1:-1] > tail[2:])
            & (tail[1:-1] > threshold)
        )
    else:
        peaks = 0

    # RMS 能量
    rms = float(np.sqrt(np.mean(ir ** 2)))

    return {
        "label": label,
        "peak_db": round(peak_db, 2),
        "rt60_estimated_s": round(rt60_est, 4) if not np.isnan(rt60_est) else None,
        "echo_peak_count_50_200ms": int(peaks),
        "rms": round(rms, 6),
        "t_max_sample": int(t_max),
        "t_max_ms": round(t_max / sr * 1000, 2),
    }


def measure_freq_response(ir, sr, label):
    """提取频率响应指标."""
    n_fft = min(8192, len(ir))
    X = np.abs(np.fft.rfft(ir, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
    X_db = 20 * np.log10(X + 1e-12)

    # 频谱平坦度 (spectral flatness)
    geo_mean = np.exp(np.mean(np.log(X + 1e-12)))
    arith_mean = np.mean(X)
    flatness = float(geo_mean / arith_mean) if arith_mean > 0 else 0.0

    # 频谱质心
    centroid = float(np.sum(freqs * X) / np.sum(X)) if np.sum(X) > 0 else 0.0

    # 频谱峰值的数量和标准差 (梳状滤波效应的度量)
    peaks_mask = (X_db[1:-1] > X_db[:-2]) & (X_db[1:-1] > X_db[2:])
    peak_indices = np.where(peaks_mask)[0] + 1
    if len(peak_indices) > 1:
        peak_spacing_hz = np.diff(freqs[peak_indices])
        peak_spacing_std = float(np.std(peak_spacing_hz))
    else:
        peak_spacing_std = 0.0

    # 频谱标准差 (越小越平坦/越不刺耳)
    spectral_std_db = float(np.std(X_db))

    return {
        "label": label,
        "spectral_flatness": round(flatness, 6),
        "spectral_centroid_hz": round(centroid, 1),
        "spectral_std_db": round(spectral_std_db, 2),
        "peak_count": int(len(peak_indices)),
        "peak_spacing_std_hz": round(peak_spacing_std, 1),
        # 采样数据 (用于绘图)
        "sample_freqs": [round(f, 1) for f in freqs[::16].tolist()],
        "sample_magnitude_db": [round(v, 2) for v in X_db[::16].tolist()],
        "sample_ir": [float(v) for v in (ir[::64] if len(ir) > 64 else ir)],
    }


def main():
    from moodify.processing.operators import (
        _schroeder_reverb,
        _schroeder_reverb_legacy,
    )

    impulse = generate_impulse()
    rt60 = 1.5

    # 旧实现
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        ir_old = _schroeder_reverb_legacy(impulse, SR, rt60)

    # 新实现
    ir_new = _schroeder_reverb(impulse, SR, rt60)

    # 确保相同长度用于对比
    min_len = min(len(ir_old), len(ir_new))
    ir_old = ir_old[:min_len]
    ir_new = ir_new[:min_len]

    # 脉冲响应指标
    ir_data = {
        "description": f"Schroeder混响脉冲响应对比 (RT60={rt60}s)",
        "old": measure_ir_metrics(ir_old, SR, "Schroeder旧实现 (交叉耦合反馈, 无全通)"),
        "new": measure_ir_metrics(ir_new, SR, "Schroeder新实现 (标准反馈梳状 + 全通)"),
    }

    # 频率响应指标
    fr_data = {
        "description": f"Schroeder混响频率响应对比 (RT60={rt60}s)",
        "old": measure_freq_response(ir_old, SR, "旧实现"),
        "new": measure_freq_response(ir_new, SR, "新实现"),
    }

    out_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(out_dir, "data")

    with open(os.path.join(data_dir, "ir_old_new.json"), "w", encoding="utf-8") as f:
        json.dump(ir_data, f, indent=2, ensure_ascii=False, cls=_NumpyEncoder)

    with open(os.path.join(data_dir, "freq_response_old_new.json"), "w", encoding="utf-8") as f:
        json.dump(fr_data, f, indent=2, ensure_ascii=False, cls=_NumpyEncoder)

    # 打印摘要
    print("=== 脉冲响应对比 ===")
    for k in ["peak_db", "rt60_estimated_s", "echo_peak_count_50_200ms", "rms"]:
        print(f"  {k}: old={ir_data['old'][k]}, new={ir_data['new'][k]}")

    print("\n=== 频率响应对比 ===")
    for k in ["spectral_flatness", "spectral_std_db", "peak_count", "peak_spacing_std_hz"]:
        print(f"  {k}: old={fr_data['old'][k]}, new={fr_data['new'][k]}")

    print(f"\n数据已保存到 {data_dir}/")


if __name__ == "__main__":
    main()
