"""
preprocessing.py — 音频预处理流水线 (SPEC §1.4)
=================================================
标准预处理路径:
  1. 加载音频 (librosa/soundfile)
  2. 重采样至 44100 Hz (若需要)
  3. 峰值归一化至 -1 dBFS
  4. 转换为 Float32 内部表示
  5. 若单声道 → 复制为立体声
  6. STFT: n_fft=1024, hop_length=512, hann window
"""

import numpy as np
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PreprocessedAudio:
    samples: np.ndarray      # float32, shape (n_samples, 2)
    sr: int                  # 44100
    duration_s: float
    original_sr: int
    original_channels: int
    stft_mag: np.ndarray | None = None    # (n_freq_bins, n_frames) — optional
    stft_phase: np.ndarray | None = None


class Preprocessor:
    """音频预处理流水线 (SPEC §1.4)"""

    def __init__(self, target_sr: int = 44100):
        self.target_sr = target_sr

    def process(self, audio_path: str,
                compute_stft: bool = False) -> PreprocessedAudio:
        """
        完整预处理流水线

        Args:
            audio_path: 音频文件路径 (.wav / .mp3 / .flac)
            compute_stft: 是否预计算 STFT

        Returns:
            PreprocessedAudio
        """
        # 1. 加载
        y, orig_sr, orig_ch = self._load(audio_path)

        # 2. 重采样
        if orig_sr != self.target_sr:
            y = self._resample(y, orig_sr)

        # 3. 峰值归一化
        y = self._normalize_peak(y, target_db=-1.0)

        # 4. Float32
        y = y.astype(np.float32)

        # 5. 立体声保证
        if y.ndim == 1:
            y = np.stack([y, y], axis=1)

        # 6. STFT (可选)
        stft_mag, stft_phase = None, None
        if compute_stft:
            stft_mag, stft_phase = self._compute_stft(y)

        return PreprocessedAudio(
            samples=y,
            sr=self.target_sr,
            duration_s=len(y) / self.target_sr,
            original_sr=orig_sr,
            original_channels=orig_ch,
            stft_mag=stft_mag,
            stft_phase=stft_phase,
        )

    # ——— 内部 ————————————————————————

    def _load(self, path: str) -> tuple[np.ndarray, int, int]:
        """加载音频文件, 自动选择后端 (WAV/MP3/FLAC/...)"""
        from moodify.audio_io import load_audio
        data, sr = load_audio(str(path), always_2d=True)
        return data, sr, data.shape[1] if data.ndim > 1 else 1

    def _resample(self, y: np.ndarray, orig_sr: int) -> np.ndarray:
        """快速重采样: soxr > scipy resample_poly > librosa"""
        target = self.target_sr
        if orig_sr == target:
            return y

        # soxr
        try:
            import soxr
            if y.ndim > 1:
                chs = [soxr.resample(y[:, c].astype(np.float64), orig_sr, target)
                       for c in range(y.shape[1])]
                return np.stack(chs, axis=1).astype(np.float32)
            return soxr.resample(y.astype(np.float64), orig_sr, target).astype(np.float32)
        except ImportError:
            pass

        # scipy resample_poly
        try:
            from scipy.signal import resample_poly
            from math import gcd
            g = gcd(orig_sr, target)
            up = target // g
            down = orig_sr // g
            if y.ndim > 1:
                chs = [resample_poly(y[:, c].astype(np.float64), up=up, down=down)
                       for c in range(y.shape[1])]
                return np.stack(chs, axis=1).astype(np.float32)
            return resample_poly(y.astype(np.float64), up=up, down=down).astype(np.float32)
        except Exception:
            pass

        # librosa fallback
        import librosa
        if y.ndim > 1:
            chs = [librosa.resample(y[:, c], orig_sr=orig_sr, target_sr=target)
                   for c in range(y.shape[1])]
            return np.stack(chs, axis=1)
        return librosa.resample(y, orig_sr=orig_sr, target_sr=target)

    def _normalize_peak(self, y: np.ndarray, target_db: float = -1.0) -> np.ndarray:
        """峰值归一化至 target_db dBFS"""
        peak = np.max(np.abs(y))
        if peak < 1e-12:
            return y
        target_linear = 10.0 ** (target_db / 20.0)
        gain = target_linear / peak
        return y * gain

    def _compute_stft(self, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        STFT: n_fft=1024, hop_length=512, hann window (SPEC §1.4)
        使用矢量化的 sliding_window_view
        """
        mono = y.mean(axis=1).astype(np.float32)
        n_fft = 1024
        hop = n_fft // 2

        from numpy.lib.stride_tricks import sliding_window_view
        window = np.hanning(n_fft).astype(np.float32)
        frames = sliding_window_view(mono, n_fft)[::hop] * window
        X = np.fft.rfft(frames)
        return np.abs(X), np.angle(X)
