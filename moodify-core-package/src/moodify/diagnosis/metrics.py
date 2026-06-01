"""
moodify_metrics.py — 共享计算模块
====================================
Moodify 系统所有诊断指标的单一计算来源。
baseline 脚本和批量分析器都引用此模块，避免两套口径。

Usage:
  from moodify_metrics import SpectrumAnalyzer, DynamicsAnalyzer, SpaceAnalyzer

每个 Analyzer 输入 (mono_audio, sr)，输出结构化 dict。
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from scipy.signal import get_window


# ============================================================
#  工具函数
# ============================================================

def amp_to_db(value: float, eps: float = 1e-12) -> float:
    return 20.0 * math.log10(max(float(value), eps))


def load_audio(path: str | Path):
    from moodify.audio_io import load_audio as _load
    data, sr = _load(str(path), always_2d=True)
    mono = data.mean(axis=1) if data.ndim > 1 and data.shape[1] > 1 else data[:, 0] if data.ndim > 1 else data
    return mono, sr, data


def frame_signal(mono: np.ndarray, sr: int,
                 frame_ms: float = 50.0, hop_ms: float = 25.0):
    frame_len = int(frame_ms * sr / 1000)
    hop_len = int(hop_ms * sr / 1000)
    if frame_len > len(mono):
        frame_len = len(mono) // 2
        hop_len = frame_len // 2
    n_frames = 1 + max(0, (len(mono) - frame_len)) // hop_len
    frames = np.zeros((n_frames, frame_len))
    times = np.zeros(n_frames)
    for m in range(n_frames):
        start = m * hop_len
        frames[m, :] = mono[start:start + frame_len]
        times[m] = (start + frame_len / 2) / sr
    return frames, times


# ============================================================
#  频段定义
# ============================================================

BANDS = {
    "Sub":      (20,   60),
    "Bass":     (60,  200),
    "Low-Mid":  (200, 500),
    "Mid":      (500, 2000),
    "Presence": (2000, 5000),
    "Air":      (8000, 16000),
}


# ============================================================
#  SpectrumAnalyzer
# ============================================================

class SpectrumAnalyzer:
    """GCS-001 第 4 节：频谱状态计算"""

    def __init__(self, n_fft: int = 2048):
        self.n_fft = n_fft                        # PHYS-002 标准: 2048
        self.hop_length = n_fft // 4              # PHYS-002 标准: hop=512

    def stft(self, mono: np.ndarray, sr: int):
        n_fft = self.n_fft
        hop = self.hop_length
        window = get_window("hann", n_fft, fftbins=True)
        n_frames = 1 + (len(mono) - n_fft) // hop
        freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
        n_bins = len(freqs)
        A = np.zeros((n_frames, n_bins))
        P = np.zeros((n_frames, n_bins))
        times = np.zeros(n_frames)
        for m in range(n_frames):
            start = m * hop
            frame = mono[start:start + n_fft].copy() * window
            X = np.fft.rfft(frame)
            A[m, :] = np.abs(X)
            P[m, :] = A[m, :] ** 2
            times[m] = start / sr
        return A, P, freqs, times

    def band_energy(self, P: np.ndarray, freqs: np.ndarray,
                    f1: float, f2: float) -> np.ndarray:
        mask = (freqs >= f1) & (freqs <= f2)
        return np.sum(P[:, mask], axis=1)

    def all_band_energies(self, P, freqs) -> dict:
        result = {}
        for name, (f1, f2) in BANDS.items():
            e_frame = self.band_energy(P, freqs, f1, f2)
            result[name] = {
                "avg": float(np.mean(e_frame)),
                "max": float(np.max(e_frame)),
                "freq_range": f"{f1}-{f2}Hz",
            }
        return result

    def spectral_centroid(self, A: np.ndarray, freqs: np.ndarray):
        num = np.sum(freqs * A, axis=1)
        den = np.sum(A, axis=1)
        den[den == 0] = 1e-12
        return num / den

    def crowding(self, band_energies: dict, P: np.ndarray):
        total = np.sum(P, axis=1)
        total[total == 0] = 1e-12
        result = {}
        for name, info in band_energies.items():
            result[name] = float(np.mean(
                self.band_energy(P, None, *self._parse_range(info["freq_range"]))
                if False else info["avg"] / np.mean(total)
            ))
        # simpler: use the stored avg values
        e_total = float(np.mean(total))
        for name, info in band_energies.items():
            result[name] = info["avg"] / e_total if e_total > 0 else 0.0
        return result

    @staticmethod
    def _parse_range(s: str):
        parts = s.replace("Hz", "").split("-")
        return float(parts[0]), float(parts[1])

    def compute_hri(self, A, P, freqs, centroid):
        """
        HRI v0.3 — 修正归一化。

        四个分量均归一化到 [0, 1]，全部使用正系数：
          HRI = (a·e_norm + b·peak_norm + c·cent_norm + d·roughness_norm) / (a+b+c+d)

        e_norm:       6-10kHz 能量 (dB) 映射到 [0,1]，范围 [0, 50] dB
        peak_norm:    6-10kHz 峰值幅度 (dB) 映射到 [0,1]，范围 [0, 45] dB
        cent_norm:    谱质心映射到 [0,1]，范围 [500, 7500] Hz
        roughness_norm: 6-10kHz 频段幅度谱标准差均值，范围 [0, 3]
        """
        mask = (freqs >= 6000) & (freqs <= 10000)
        e_6_10k = float(np.mean(np.sum(P[:, mask], axis=1)))
        peak_6_10k = float(np.mean(np.max(A[:, mask], axis=1)))
        centroid_global = float(np.mean(centroid))
        amp_slice = A[:, mask]
        roughness = float(np.mean(np.std(amp_slice, axis=1)))

        e_db    = 10 * math.log10(e_6_10k + 1e-12)
        peak_db = 20 * math.log10(peak_6_10k + 1e-12)

        # 归一化到 [0, 1] — 使用合理的声学范围
        e_norm      = min(1.0, max(0.0, e_db / 50.0))
        peak_norm   = min(1.0, max(0.0, peak_db / 45.0))
        cent_norm   = min(1.0, max(0.0, (centroid_global - 500.0) / 7000.0))
        rough_norm  = min(1.0, max(0.0, roughness / 3.0))

        # 加权平均 — 四个分量全部正系数
        a, b, c, d = 1.0, 0.5, 0.3, 0.5
        HRI = (a * e_norm + b * peak_norm + c * cent_norm + d * rough_norm) / (a + b + c + d)

        return {"HRI": round(float(HRI), 4),
                "E_6_10k_dB": round(e_db, 2),
                "Peak_6_10k_dB": round(peak_db, 2),
                "Centroid_hz": round(centroid_global, 1),
                "Roughness": round(float(roughness), 4),
                "e_norm": round(float(e_norm), 4),
                "peak_norm": round(float(peak_norm), 4),
                "cent_norm": round(float(cent_norm), 4),
                "rough_norm": round(float(rough_norm), 4)}

    def diagnose(self, mono: np.ndarray, sr: int) -> dict:
        A, P, freqs, times = self.stft(mono, sr)
        bands = self.all_band_energies(P, freqs)
        centroid = self.spectral_centroid(A, freqs)
        crow = self.crowding(bands, P)
        hri = self.compute_hri(A, P, freqs, centroid)

        return {
            "centroid_hz": round(float(np.mean(centroid)), 1),
            "centroid_std_hz": round(float(np.std(centroid)), 1),
            "bands": {n: {"avg_dB": round(amp_to_db(bands[n]["avg"]), 2),
                          "max_dB": round(amp_to_db(bands[n]["max"]), 2)}
                      for n in BANDS},
            "crowding": {n: round(crow[n], 4) for n in BANDS},
            "HRI": hri,
        }


# ============================================================
#  DynamicsAnalyzer
# ============================================================

class DynamicsAnalyzer:
    """GCS-001 第 5 节：动态状态计算"""

    def __init__(self, frame_ms: float = 50.0, hop_ms: float = 25.0):
        self.frame_ms = frame_ms
        self.hop_ms = hop_ms

    def diagnose(self, mono: np.ndarray, sr: int) -> dict:
        frames, times = frame_signal(mono, sr, self.frame_ms, self.hop_ms)
        rms_lin = np.sqrt(np.mean(frames ** 2, axis=1) + 1e-12)
        peak_lin = np.max(np.abs(frames), axis=1)
        rms_db = 20 * np.log10(rms_lin + 1e-12)
        peak_db = 20 * np.log10(peak_lin + 1e-12)
        crest_db = peak_db - rms_db

        # DR
        rms_sorted = np.sort(rms_db)
        n = len(rms_sorted)
        p10 = float(rms_sorted[int(n * 0.10)])
        p50 = float(rms_sorted[int(n * 0.50)])
        p95 = float(rms_sorted[int(n * 0.95)])
        dr = p95 - p10

        crest_mean = float(np.mean(crest_db))
        rms_median = float(np.median(rms_db))
        loud_density = float(np.sum(rms_db > rms_median) / len(rms_db))

        # DFI v0.4: 线性映射替代参考值锚定
        # 归一化声明 (SPEC-011 T7.1):
        #   f_DR:    [4, 20] dB → [0, 1], 来源: EBU 3342 典型音乐 DR 范围
        #   f_Crest: [2, 14] dB → [0, 1], 来源: 实测 crest factor 分布
        #   权重:    等权 1:1:1, 未校准
        #   线性假设: 最小-最大归一化, 差异在校准后可比较
        f_dr    = max(0.0, min(1.0, (20.0 - dr) / 16.0))
        f_crest = max(0.0, min(1.0, (14.0 - crest_mean) / 12.0))
        dfi = (f_dr + f_crest + loud_density) / 3.0

        # Section contrast
        n_sec = 4
        sec_len = len(rms_db) // n_sec
        sec_avgs = []
        for i in range(n_sec):
            s = i * sec_len
            e = (i + 1) * sec_len if i < n_sec - 1 else len(rms_db)
            sec_avgs.append(float(np.mean(rms_db[s:e])))
        section_contrast = max(sec_avgs) - min(sec_avgs)

        return {
            "RMS_mean_dB": round(float(np.mean(rms_db)), 2),
            "RMS_std_dB": round(float(np.std(rms_db)), 2),
            "Peak_max_dB": round(float(np.max(peak_db)), 2),
            "Crest_mean_dB": round(crest_mean, 2),
            "Crest_std_dB": round(float(np.std(crest_db)), 2),
            "DR_dB": round(dr, 2),
            "DR_P10_dB": round(p10, 2),
            "DR_P50_dB": round(p50, 2),
            "DR_P95_dB": round(p95, 2),
            "DFI": round(dfi, 4),
            "DFI_f_DR": round(f_dr, 4),
            "DFI_f_Crest": round(f_crest, 4),
            "DFI_LoudDensity": round(loud_density, 4),
            "SectionContrast_dB": round(section_contrast, 2),
        }


# ============================================================
#  SpaceAnalyzer
# ============================================================

class SpaceAnalyzer:
    """GCS-001 第 6 节：空间状态计算"""

    def __init__(self):
        self.sideratio_ref = 0.50
        self.corr_ref = 0.30

    def diagnose(self, left: np.ndarray, right: np.ndarray, sr: int) -> dict:
        # Corr_LR
        std_l, std_r = np.std(left), np.std(right)
        corr_global = float(np.corrcoef(left, right)[0, 1]) if std_l > 0 and std_r > 0 else 1.0

        # Mid-Side
        mid = (left + right) / 2.0
        side = (left - right) / 2.0
        e_mid = float(np.sum(mid ** 2))
        e_side = float(np.sum(side ** 2))
        side_ratio = e_side / e_mid if e_mid > 0 else 0.0

        # Frame-level Corr
        f_len = int(0.2 * sr)
        h_len = f_len // 2
        n_frames = 1 + max(0, (len(left) - f_len)) // h_len
        corr_frame = np.zeros(n_frames)
        for m in range(n_frames):
            s = m * h_len
            sl, sr_ = left[s:s+f_len], right[s:s+f_len]
            stdl, stdr = np.std(sl), np.std(sr_)
            corr_frame[m] = float(np.corrcoef(sl, sr_)[0, 1]) if stdl > 1e-12 and stdr > 1e-12 else 1.0
        corr_mean = float(np.mean(corr_frame))

        # Side stability (frame-level side ratio)
        sr_frame_mid = np.zeros(n_frames)
        sr_frame_sid = np.zeros(n_frames)
        for m in range(n_frames):
            s = m * h_len
            Lf, Rf = left[s:s+f_len], right[s:s+f_len]
            Mf = (Lf + Rf) / 2.0
            Sf = (Lf - Rf) / 2.0
            sr_frame_mid[m] = np.sum(Mf ** 2) + 1e-12
            sr_frame_sid[m] = np.sum(Sf ** 2)
        sr_frame = sr_frame_sid / sr_frame_mid
        side_stability = 1.0 / (1.0 + float(np.std(sr_frame)))

        # Center stability (vocal band 500-5000Hz in mid)
        n_fft_c = 2048           # PHYS-002 标准
        hop_c = n_fft_c // 4     # 512
        window_c = get_window("hann", n_fft_c, fftbins=True)
        freqs_c = np.fft.rfftfreq(n_fft_c, 1.0 / sr)
        mask_c = (freqs_c >= 500) & (freqs_c <= 5000)
        n_frames_c = 1 + max(0, (len(mid) - n_fft_c)) // hop_c
        energies_c = np.zeros(n_frames_c)
        for m in range(n_frames_c):
            s = m * hop_c
            frame = mid[s:s+n_fft_c].copy() * window_c
            P = np.abs(np.fft.rfft(frame)) ** 2
            energies_c[m] = np.sum(P[mask_c])
        e_mean_c = float(np.mean(energies_c))
        e_std_c = float(np.std(energies_c))
        center_stability = 1.0 / (1.0 + e_std_c / (e_mean_c + 1e-12))

        # FalseWidthRisk
        f_side = min(1.0, side_ratio / self.sideratio_ref)
        f_corr = max(0.0, 1.0 - corr_mean)
        f_center = 1.0 - center_stability
        fwr = (f_side + f_corr + f_center) / 3.0

        # Mono compatibility
        rms_mid = float(np.sqrt(np.mean(mid ** 2)))
        rms_side = float(np.sqrt(np.mean(side ** 2)))
        mono_compat = rms_mid / (rms_mid + rms_side + 1e-12)

        # Reverb estimation
        half = len(mid) // 2
        e_first = np.sum(mid[:half] ** 2) + 1e-12
        e_second = np.sum(mid[half:] ** 2) + 1e-12
        reverb_tail = float(e_second / e_first)

        return {
            "Corr_LR_global": round(corr_global, 4),
            "Corr_LR_mean": round(corr_mean, 4),
            "Corr_LR_std": round(float(np.std(corr_frame)), 4),
            "Corr_LR_min": round(float(np.min(corr_frame)), 4),
            "SideRatio": round(side_ratio, 4),
            "SideRatio_dB": round(10 * math.log10(side_ratio + 1e-12), 2),
            "SideStability": round(side_stability, 4),
            "CenterStability": round(center_stability, 4),
            "ReverbTailRatio": round(reverb_tail, 4),
            "FalseWidthRisk": round(fwr, 4),
            "FWR_f_side": round(f_side, 4),
            "FWR_f_corr": round(f_corr, 4),
            "FWR_f_center": round(f_center, 4),
            "MonoCompatibility": round(mono_compat, 4),
        }


# ============================================================
#  LayersAnalyzer (stub — 完整实现在 layers_baseline.py)
# ============================================================

class LayersAnalyzer:
    """GCS-001 第 7 节：层级状态计算 (需要 Demucs)"""

    def diagnose(self, audio_path: str) -> dict | None:
        """需要 GPU 或长时间 CPU。返回 None 表示跳过。"""
        return None  # 批量模式下默认跳过，按需开启
