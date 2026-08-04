"""
spectral_chain.py — HPSS + M/S 频谱处理链 (AEP-ACU-003: Residual-Preserving)
============================================================================

替代 Demucs 深度学习源分离。利用 librosa HPSS 将音频分解为
谐波成分 (H)、打击乐成分 (P) 和残差成分 (R)，分别施加不同的
DSP 处理参数，然后重新合成。

AEP-ACU-003 (2026-07-03): 从 H+P 二分重建升级为 H+P+R 三分保留。
R = D - H - P。当 margin > 1.0 时软掩码产生非零残差，丢弃会导致
可测量的能量损失，违反 PHYS-007 守恒原则。

信号流:
  立体声输入
    → HPSS 分解 → H (延音/旋律) + P (瞬态/鼓点) + R (残差)
    → H: 频率塑形 (人声临场 EQ + 低频温暖 + 混响 + 高频搁架)
    → P: 动态塑形 (压缩 + 谐波驱动)
    → R: 保留 (默认) 或 衰减处理
    → 叠加重建 → 立体声输出
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Optional

import librosa
import numpy as np
import pedalboard

logger = logging.getLogger(__name__)


@dataclass
class HPSSComponents:
    """H/P/R 三分量容器 (AEP-ACU-003)."""
    harmonic: np.ndarray
    percussive: np.ndarray
    residual: np.ndarray
    margin: float
    n_fft: int
    hop_length: int
    residual_energy_ratio: float = 0.0
    reconstruction_error: float = 0.0


@dataclass
class HPSSAudit:
    """HPSS 处理审计指标 (AEP-ACU-003)."""
    residual_energy_ratio: float = 0.0
    reconstruction_error: float = 0.0
    rms_before_db: float = -100.0
    rms_after_db: float = -100.0
    rms_delta_db: float = 0.0
    lufs_before: float = -100.0
    lufs_after: float = -100.0
    lufs_delta: float = 0.0
    spectral_residual_ratio: float = 0.0
    residual_preserved: bool = True
    residual_mode: str = "preserve"


class SpectralDSPChain:
    """HPSS 频谱处理链 — AI 音乐后期处理的正确技术路径。

    将 15 参数工艺卡按声学意义分配到两条子链:
      - 谐波链 (H): 处理延音、旋律、人声 — P01-P05, P10-P12, P14-P15
      - 打击乐链 (P): 处理瞬态、鼓点、冲击力 — P06-P09, P13
      - 残差链 (R): 保留 (默认) — 不丢失任何信号能量 (AEP-ACU-003)
    """

    def __init__(self, n_fft: int = 2048, hop_length: int = 512,
                 margin: float = 2.0,
                 residual_mode: str = "preserve"):
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.margin = margin
        # "preserve": 保留 R 不变 (默认, AEP-ACU-003 合规)
        # "discard": 丢弃 R (旧行为, 用于 A/B 对比)
        # "attenuate": R 衰减后加回 (experimental)
        if residual_mode not in ("preserve", "discard", "attenuate"):
            raise ValueError(
                f"residual_mode must be 'preserve', 'discard', or 'attenuate', "
                f"got {residual_mode!r}"
            )
        self.residual_mode = residual_mode
        self._last_audit: Optional[HPSSAudit] = None

    @property
    def last_audit(self) -> Optional[HPSSAudit]:
        """返回最近一次 process() 的审计数据 (AEP-ACU-003)."""
        return self._last_audit

    def process(self, audio: np.ndarray, sr: int, params: dict) -> np.ndarray:
        """主入口: H/P/R 分离 → 差异处理 → H+P+R 重建 (AEP-ACU-003).

        Args:
            audio: (samples,) 或 (samples, 2)
            sr: 采样率
            params: 15-param 工艺卡字典

        Returns:
            处理后的音频, shape 与输入一致
        """
        # ── 审计: 输入 ──
        rms_before = _compute_rms_db(audio)
        self._last_audit = HPSSAudit(
            rms_before_db=rms_before,
            residual_mode=self.residual_mode,
        )

        if audio.ndim == 1 or audio.shape[1] < 2:
            result = self._process_mono(audio, sr, params)
        else:
            result = self._process_stereo(audio, sr, params)

        # ── 审计: 输出 ──
        rms_after = _compute_rms_db(result)
        self._last_audit.rms_after_db = rms_after
        self._last_audit.rms_delta_db = round(rms_after - rms_before, 2)

        return result.astype(audio.dtype)

    # ── 立体声处理 ─────────────────────────────────────────────

    def _process_stereo(self, audio: np.ndarray, sr: int,
                        params: dict) -> np.ndarray:
        """立体声: HPSS → H/P/R 分别处理 → H+P+R 重建."""
        comps, D_left, D_right = self._decompose(audio)
        original_rms = _compute_rms_db(audio)

        h_params = self._harmonic_params(params)
        p_params = self._percussive_params(params)

        H_out = self._apply_pedalboard(comps.harmonic, sr, h_params)
        P_out = self._apply_pedalboard(comps.percussive, sr, p_params)

        # ── Residual 处理 ──
        if self.residual_mode == "discard":
            R_out = np.zeros_like(comps.residual)
        elif self.residual_mode == "attenuate":
            # 低强度压缩后保留 (降低潜在的噪声突出度)
            R_out = comps.residual * 0.7
        else:  # preserve
            R_out = comps.residual

        result = H_out + P_out + R_out

        # ── 计算审计指标 ──
        self._compute_audit_metrics(comps, D_left, D_right, audio,
                                    result, original_rms, sr)

        # ── 安全限幅 ──
        peak = np.max(np.abs(result))
        if peak > 0.95:
            result *= 0.95 / peak

        return result

    # ── 单声道处理 ─────────────────────────────────────────────

    def _process_mono(self, audio: np.ndarray, sr: int,
                      params: dict) -> np.ndarray:
        """单声道: HPSS → H/P/R 分别处理 → H+P+R 重建."""
        D = librosa.stft(audio, n_fft=self.n_fft, hop_length=self.hop_length)
        H_mask, P_mask = librosa.decompose.hpss(D, margin=self.margin, mask=True)

        H = librosa.istft(D * H_mask, hop_length=self.hop_length, length=len(audio))
        P = librosa.istft(D * P_mask, hop_length=self.hop_length, length=len(audio))
        R_stft = D * (1.0 - H_mask - P_mask)
        R = librosa.istft(R_stft, hop_length=self.hop_length, length=len(audio))
        residual_ratio = _compute_energy_ratio(R_stft, D)

        h_params = self._harmonic_params(params)
        p_params = self._percussive_params(params)

        # 转为伪立体声以复用 _apply_pedalboard
        H_stereo = np.column_stack([H, H])
        P_stereo = np.column_stack([P, P])
        H_out = self._apply_pedalboard(H_stereo, sr, h_params)
        P_out = self._apply_pedalboard(P_stereo, sr, p_params)

        # Residual 处理
        if self.residual_mode == "discard":
            R_out = np.zeros(len(audio))
        elif self.residual_mode == "attenuate":
            R_out = R * 0.7
        else:
            R_out = R

        result = (H_out[:, 0] + P_out[:, 0]) * 0.5 + R_out

        # ── No-op 重建误差 ──
        reco_error = _compute_reconstruction_error(H, P, R, audio)

        # ── 审计 ──
        self._last_audit.residual_energy_ratio = residual_ratio
        self._last_audit.reconstruction_error = reco_error
        self._last_audit.residual_preserved = (self.residual_mode != "discard")

        peak = np.max(np.abs(result))
        if peak > 0.95:
            result *= 0.95 / peak
        return result

    # ── HPSS 分解 ──────────────────────────────────────────────

    def _decompose(self, audio: np.ndarray):
        """HPSS 分解: 产生 H + P + R 三个分量 (AEP-ACU-003).

        Returns:
            (HPSSComponents, D_left, D_right)
        """
        D_left = librosa.stft(audio[:, 0], n_fft=self.n_fft,
                              hop_length=self.hop_length)
        D_right = librosa.stft(audio[:, 1], n_fft=self.n_fft,
                               hop_length=self.hop_length)

        H_mask_l, P_mask_l = librosa.decompose.hpss(
            D_left, margin=self.margin, mask=True)
        H_mask_r, P_mask_r = librosa.decompose.hpss(
            D_right, margin=self.margin, mask=True)

        # ── Residual masks ──
        R_mask_l = 1.0 - H_mask_l - P_mask_l
        R_mask_r = 1.0 - H_mask_r - P_mask_r

        # ── Residual 能量比 (STFT 域) ──
        residual_ratio = _compute_energy_ratio(
            D_left * R_mask_l + D_right * R_mask_r,
            D_left + D_right,
        )

        n_samples = len(audio)
        H_left = librosa.istft(D_left * H_mask_l, hop_length=self.hop_length,
                               length=n_samples)
        H_right = librosa.istft(D_right * H_mask_r, hop_length=self.hop_length,
                                length=n_samples)
        P_left = librosa.istft(D_left * P_mask_l, hop_length=self.hop_length,
                               length=n_samples)
        P_right = librosa.istft(D_right * P_mask_r, hop_length=self.hop_length,
                                length=n_samples)
        R_left = librosa.istft(D_left * R_mask_l, hop_length=self.hop_length,
                               length=n_samples)
        R_right = librosa.istft(D_right * R_mask_r, hop_length=self.hop_length,
                                length=n_samples)

        harmonic = np.column_stack([H_left, H_right])
        percussive = np.column_stack([P_left, P_right])
        residual = np.column_stack([R_left, R_right])

        # ── No-op 重建误差 (处理前) ──
        reco_error = _compute_reconstruction_error(
            H_left + H_right, P_left + P_right,
            R_left + R_right,
            audio[:, 0] + audio[:, 1],
        )

        comps = HPSSComponents(
            harmonic=harmonic,
            percussive=percussive,
            residual=residual,
            margin=self.margin,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            residual_energy_ratio=residual_ratio,
            reconstruction_error=reco_error,
        )

        return comps, D_left, D_right

    # ── 审计指标计算 ───────────────────────────────────────────

    def _compute_audit_metrics(self, comps: HPSSComponents,
                                D_left, D_right,
                                audio_in: np.ndarray,
                                audio_out: np.ndarray,
                                original_rms: float,
                                sr: int):
        """填充审计数据到 self._last_audit."""
        audit = self._last_audit
        audit.residual_energy_ratio = comps.residual_energy_ratio
        audit.reconstruction_error = comps.reconstruction_error
        audit.residual_preserved = (self.residual_mode != "discard")

        # ── 频谱残差比 ──
        D_in = np.abs(np.concatenate([D_left.ravel(), D_right.ravel()]))
        # Recompute output STFT for comparison
        D_out_l = librosa.stft(audio_out[:, 0], n_fft=self.n_fft,
                               hop_length=self.hop_length)
        D_out_r = librosa.stft(audio_out[:, 1], n_fft=self.n_fft,
                               hop_length=self.hop_length)
        D_out_abs = np.abs(np.concatenate([D_out_l.ravel(), D_out_r.ravel()]))
        denom = np.mean(D_in) + 1e-15
        audit.spectral_residual_ratio = float(
            np.mean(np.abs(D_in - D_out_abs)) / denom
        )

        # ── LUFS 变化 (best-effort, 需要 pyloudnorm) ──
        try:
            import pyloudnorm as pyln
            meter = pyln.Meter(sr)
            mono_in = audio_in.mean(axis=1) if audio_in.ndim > 1 else audio_in
            mono_out = audio_out.mean(axis=1) if audio_out.ndim > 1 else audio_out
            audit.lufs_before = float(meter.integrated_loudness(mono_in))
            audit.lufs_after = float(meter.integrated_loudness(mono_out))
            audit.lufs_delta = round(audit.lufs_after - audit.lufs_before, 2)
        except Exception:
            audit.lufs_before = -100.0
            audit.lufs_after = -100.0
            audit.lufs_delta = 0.0

    # ── 参数分配 ────────────────────────────────────────────────

    def _harmonic_params(self, params: dict) -> dict:
        """提取作用于谐波成分的参数: EQ + 混响 + 高频."""
        keys = [
            "P01_vocal_presence_freq", "P02_vocal_presence_gain", "P03_vocal_presence_q",
            "P04_proximity_low_freq", "P05_proximity_low_gain",
            "P10_reverb_t60", "P11_reverb_dry_wet", "P12_reverb_width",
            "P14_high_shelf_freq", "P15_high_shelf_gain",
        ]
        return {k: params[k] for k in keys if k in params}

    def _percussive_params(self, params: dict) -> dict:
        """提取作用于打击乐成分的参数: 压缩 + 谐波驱动."""
        keys = [
            "P06_compression_ratio", "P07_compression_attack",
            "P08_compression_release", "P09_compression_threshold",
            "P13_harmonic_drive",
        ]
        return {k: params[k] for k in keys if k in params}

    # ── Pedalboard 处理 ─────────────────────────────────────────

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


# ═══════════════════════════════════════════════════════════════════
# 审计辅助函数 (AEP-ACU-003)
# ═══════════════════════════════════════════════════════════════════


def _compute_rms_db(signal: np.ndarray) -> float:
    """计算 RMS 电平 (dB)."""
    rms = float(np.sqrt(np.mean(np.square(signal.astype(np.float64))) + 1e-15))
    return float(20.0 * math.log10(rms))


def _compute_energy_ratio(R_stft: np.ndarray, D_stft: np.ndarray) -> float:
    """残差能量比: sum(|R|²) / sum(|D|²)."""
    r_energy = float(np.sum(np.abs(R_stft) ** 2))
    d_energy = float(np.sum(np.abs(D_stft) ** 2))
    if d_energy < 1e-15:
        return 0.0
    return round(r_energy / d_energy, 6)


def _compute_reconstruction_error(
    H_mono: np.ndarray, P_mono: np.ndarray,
    R_mono: np.ndarray, original_mono: np.ndarray,
) -> float:
    """No-op 重建相对误差: ||原信号 - (H+P+R)|| / ||原信号||."""
    recon = H_mono + P_mono + R_mono
    denom = float(np.linalg.norm(original_mono.astype(np.float64)))
    if denom < 1e-15:
        return 0.0
    err = float(np.linalg.norm(
        (original_mono - recon[:len(original_mono)]).astype(np.float64)
    ))
    return round(err / denom, 10)
