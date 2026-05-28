"""
spectral_chain.py — HPSS + M/S 频谱处理链
===========================================
替代 Demucs 深度学习源分离。利用 librosa HPSS 将音频分解为
谐波成分 (H) 和打击乐成分 (P)，分别施加不同的 DSP 处理参数，
然后重新合成。

原理: AI 生成的音乐没有真正的声部边界，Demucs 分离不仅慢
(30-60s) 还会引入伪影。HPSS 基于 FFT 中值滤波，在 <1s 内
完成分解，且不产生 DL 伪影。

信号流:
  立体声输入
    → HPSS 分解 → H (延音/旋律) + P (瞬态/鼓点)
    → H: 频率塑形 (人声临场 EQ + 低频温暖 + 混响 + 高频搁架)
    → P: 动态塑形 (压缩 + 谐波驱动)
    → 叠加重建 → 立体声输出
"""

from __future__ import annotations

import numpy as np
import librosa
import pedalboard


class SpectralDSPChain:
    """HPSS 频谱处理链 — AI 音乐后期处理的正确技术路径。

    将 15 参数工艺卡按声学意义分配到两条子链:
      - 谐波链 (H): 处理延音、旋律、人声 — P01-P05, P10-P12, P14-P15
      - 打击乐链 (P): 处理瞬态、鼓点、冲击力 — P06-P09, P13
    """

    def __init__(self, n_fft: int = 2048, hop_length: int = 512, margin: float = 2.0):
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.margin = margin  # HPSS 分离强度, >1.0 产生 H+P+R 三组分

    def process(self, audio: np.ndarray, sr: int, params: dict) -> np.ndarray:
        """主入口: 谐波/打击乐分离 → 差异处理 → 重建。

        Args:
            audio: (samples,) 或 (samples, 2)
            sr: 采样率
            params: 15-param 工艺卡字典

        Returns:
            处理后的音频, shape 与输入一致
        """
        if audio.ndim == 1 or audio.shape[1] < 2:
            return self._process_mono(audio, sr, params)

        H, P = self._decompose(audio)
        h_params = self._harmonic_params(params)
        p_params = self._percussive_params(params)

        H_out = self._apply_pedalboard(H, sr, h_params)
        P_out = self._apply_pedalboard(P, sr, p_params)

        result = H_out + P_out
        peak = np.max(np.abs(result))
        if peak > 0.95:
            result *= 0.95 / peak
        return result.astype(audio.dtype)

    # ── HPSS 分解 ──────────────────────────────────────────

    def _decompose(self, audio: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """HPSS 分解: 利用时间/频率方向的中值滤波分离谐波与打击乐。

        - 谐波 (H): 时间上平滑 → 时间方向中值滤波
        - 打击乐 (P): 频率上平滑 → 频率方向中值滤波
        """
        D_left = librosa.stft(audio[:, 0], n_fft=self.n_fft,
                              hop_length=self.hop_length)
        D_right = librosa.stft(audio[:, 1], n_fft=self.n_fft,
                               hop_length=self.hop_length)

        H_mask_l, P_mask_l = librosa.decompose.hpss(D_left, margin=self.margin, mask=True)
        H_mask_r, P_mask_r = librosa.decompose.hpss(D_right, margin=self.margin, mask=True)

        n_samples = len(audio)
        H_left = librosa.istft(D_left * H_mask_l, hop_length=self.hop_length,
                               length=n_samples)
        H_right = librosa.istft(D_right * H_mask_r, hop_length=self.hop_length,
                                length=n_samples)
        P_left = librosa.istft(D_left * P_mask_l, hop_length=self.hop_length,
                               length=n_samples)
        P_right = librosa.istft(D_right * P_mask_r, hop_length=self.hop_length,
                                length=n_samples)

        return (np.column_stack([H_left, H_right]),
                np.column_stack([P_left, P_right]))

    # ── 参数分配 ────────────────────────────────────────────

    def _harmonic_params(self, params: dict) -> dict:
        """提取作用于谐波成分的参数: EQ + 混响 + 高频。

        为什么这些参数分配给 H:
          - 人声临场 EQ (P01-P03): 人声属于延音/谐波类
          - 低频温暖 (P04-P05): 贝斯延音、和弦温暖感
          - 混响 (P10-P12): 空间感主要作用于延音,瞬态加混响会浑浊
          - 高频搁架 (P14-P15): 空气感作用于谐波频段
        """
        keys = [
            "P01_vocal_presence_freq", "P02_vocal_presence_gain", "P03_vocal_presence_q",
            "P04_proximity_low_freq", "P05_proximity_low_gain",
            "P10_reverb_t60", "P11_reverb_dry_wet", "P12_reverb_width",
            "P14_high_shelf_freq", "P15_high_shelf_gain",
        ]
        return {k: params[k] for k in keys if k in params}

    def _percussive_params(self, params: dict) -> dict:
        """提取作用于打击乐成分的参数: 压缩 + 谐波驱动。

        为什么这些参数分配给 P:
          - 压缩 (P06-P09): 主要控制瞬态/冲击力
          - 谐波驱动 (P13): 为瞬态增添能量和存在感
        """
        keys = [
            "P06_compression_ratio", "P07_compression_attack",
            "P08_compression_release", "P09_compression_threshold",
            "P13_harmonic_drive",
        ]
        return {k: params[k] for k in keys if k in params}

    # ── Pedalboard 处理 ─────────────────────────────────────

    def _apply_pedalboard(self, audio: np.ndarray, sr: int,
                          params: dict) -> np.ndarray:
        """用简化版 pedalboard 链处理单路音频。"""
        board = pedalboard.Pedalboard([])

        # Vocal presence (PeakFilter)
        f = params.get("P01_vocal_presence_freq", 0)
        g = params.get("P02_vocal_presence_gain", 0)
        q = params.get("P03_vocal_presence_q", 0.7)
        if f and abs(g) > 0.01:
            board.append(pedalboard.PeakFilter(
                cutoff_frequency_hz=float(f), gain_db=float(g), q=float(q)))

        # Low warmth (LowShelfFilter)
        lf = params.get("P04_proximity_low_freq", 0)
        lg = params.get("P05_proximity_low_gain", 0)
        if lf and abs(lg) > 0.01:
            board.append(pedalboard.LowShelfFilter(
                cutoff_frequency_hz=float(lf), gain_db=float(lg)))

        # Compressor
        ratio = params.get("P06_compression_ratio", 0)
        if ratio:
            board.append(pedalboard.Compressor(
                threshold_db=float(params.get("P09_compression_threshold", -24)),
                ratio=float(ratio),
                attack_ms=float(params.get("P07_compression_attack", 15)),
                release_ms=float(params.get("P08_compression_release", 150)),
            ))

        # Reverb
        wet = params.get("P11_reverb_dry_wet", 0)
        if wet and wet > 0.005:
            board.append(pedalboard.Reverb(
                room_size=float(wet), damping=0.5,
                wet_level=float(wet), dry_level=1.0 - float(wet),
                width=float(params.get("P12_reverb_width", 0.8)),
            ))

        # Harmonic drive
        drive = params.get("P13_harmonic_drive", 0)
        if drive and drive > 0.002:
            board.append(pedalboard.Distortion(drive_db=float(drive) * 20.0))

        # High shelf
        hf = params.get("P14_high_shelf_freq", 0)
        hg = params.get("P15_high_shelf_gain", 0)
        if hf and abs(hg) > 0.01:
            board.append(pedalboard.HighShelfFilter(
                cutoff_frequency_hz=float(hf), gain_db=float(hg)))

        board.append(pedalboard.Gain())
        board.append(pedalboard.Limiter())

        # Convert (samples, 2) → (2, samples) for pedalboard
        audio_t = audio.T.astype(np.float32).copy()
        processed = board(audio_t, sr)
        return processed.T.astype(audio.dtype)

    # ── 单声道兼容 ──────────────────────────────────────────

    def _process_mono(self, audio: np.ndarray, sr: int,
                      params: dict) -> np.ndarray:
        """单声道: 仅 HPSS, 无 M/S 处理。"""
        D = librosa.stft(audio, n_fft=self.n_fft, hop_length=self.hop_length)
        H_mask, P_mask = librosa.decompose.hpss(D, margin=self.margin, mask=True)

        H = librosa.istft(D * H_mask, hop_length=self.hop_length, length=len(audio))
        P = librosa.istft(D * P_mask, hop_length=self.hop_length, length=len(audio))

        h_params = self._harmonic_params(params)
        p_params = self._percussive_params(params)

        H_out = self._apply_pedalboard(np.column_stack([H, H]), sr, h_params)
        P_out = self._apply_pedalboard(np.column_stack([P, P]), sr, p_params)

        result = (H_out[:, 0] + P_out[:, 0]) * 0.5
        peak = np.max(np.abs(result))
        if peak > 0.95:
            result *= 0.95 / peak
        return result.astype(audio.dtype)
