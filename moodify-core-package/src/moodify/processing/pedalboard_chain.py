"""pedalboard_chain.py — 15-param craft chain → pedalboard effects → processed audio.

PHYS-003 效应指纹集成 (SPEC-011 T4):
  process_with_fingerprint() 在处理音频的同时测量 THD/CR_eff/瞬态保持度.

PHYS-007 守恒约束审计 (SPEC-011 T5):
  process_with_audit() 额外执行能量守恒审计, 检测未报告的能量注入/损失.
"""

from __future__ import annotations

import math
import numpy as np
import pedalboard

from moodify.fingerprint import ProcessorFingerprint, compute_thd, estimate_cr_eff
from moodify.conservation import ConservationReport, audit_conservation


def _p(params: dict, key: str, default: float = 0.0) -> float:
    return float(params.get(key, default))


def generate_test_signal(sr: int = 44100, duration_s: float = 2.0,
                         test_freq: float = 1000.0) -> np.ndarray:
    """生成用于效应指纹测量的纯音测试信号 (PHYS-003 §6).

    Args:
        sr: 采样率 [Hz]
        duration_s: 时长 [s]
        test_freq: 测试基频 [Hz]

    Returns:
        mono float32 测试信号
    """
    t = np.linspace(0, duration_s, int(sr * duration_s), endpoint=False)
    signal = 0.8 * np.sin(2.0 * np.pi * test_freq * t)
    return signal.astype(np.float32)


class MoodifyDSPChain:
    """Builds and applies a pedalboard effect chain from craft-card parameters."""

    def __init__(self, params: dict | None = None):
        self.params = params or {}

    @staticmethod
    def build_chain(params: dict) -> pedalboard.Pedalboard:
        board = pedalboard.Pedalboard([])

        # P01-P03: Vocal presence (PeakFilter)
        g = _p(params, "P02_vocal_presence_gain")
        if abs(g) > 0.01:
            board.append(pedalboard.PeakFilter(
                cutoff_frequency_hz=_p(params, "P01_vocal_presence_freq", 3000),
                gain_db=g, q=_p(params, "P03_vocal_presence_q", 0.7)))

        # P04-P05: Low warmth (LowShelfFilter)
        g = _p(params, "P05_proximity_low_gain")
        if abs(g) > 0.01:
            board.append(pedalboard.LowShelfFilter(
                cutoff_frequency_hz=_p(params, "P04_proximity_low_freq", 200),
                gain_db=g))

        # P06-P09: Dynamics (Compressor) — always on at unity
        board.append(pedalboard.Compressor(
            threshold_db=_p(params, "P09_compression_threshold", -24),
            ratio=_p(params, "P06_compression_ratio", 2),
            attack_ms=_p(params, "P07_compression_attack", 15),
            release_ms=_p(params, "P08_compression_release", 150)))

        # P10-P12: Space (Reverb)
        w = _p(params, "P11_reverb_dry_wet", 0.2)
        if w > 0.005:
            board.append(pedalboard.Reverb(
                room_size=w, damping=0.5, wet_level=w,
                dry_level=1.0 - w, width=_p(params, "P12_reverb_width", 0.8)))

        # P13: Harmonic drive (Distortion)
        d = _p(params, "P13_harmonic_drive")
        if d > 0.002:
            board.append(pedalboard.Distortion(drive_db=d * 20.0))

        # P14-P15: Air (HighShelfFilter)
        g = _p(params, "P15_high_shelf_gain")
        if abs(g) > 0.01:
            board.append(pedalboard.HighShelfFilter(
                cutoff_frequency_hz=_p(params, "P14_high_shelf_freq", 10000),
                gain_db=g))

        # Unity output staging: pedalboard.Gain() 无参数默认 +1 dB, 必须显式 0 dB.
        # 安全上限: pedalboard.Limiter 内置 auto-makeup-gain 会把输出归一化到满幅
        # (spotify/pedalboard#282), 用 Clipping 做真正的 -1 dBFS 硬 ceiling.
        board.append(pedalboard.Gain(gain_db=0.0))
        board.append(pedalboard.Clipping(threshold_db=-1.0))
        return board

    def _run_board(self, audio: np.ndarray, sr: int,
                   params: dict | None = None) -> np.ndarray:
        """内部: 运行 pedalboard 处理链."""
        board = self.build_chain(params or self.params)
        is_stereo = audio.ndim > 1 and audio.shape[1] > 1
        x = (audio.T if is_stereo else audio.reshape(1, -1)).astype(np.float32)
        y = board(x, sr)
        return (y.T if is_stereo else y[0]).astype(audio.dtype)

    def process(self, audio: np.ndarray, sr: int,
                params: dict | None = None) -> np.ndarray:
        """处理音频 (向后兼容)."""
        return self._run_board(audio, sr, params)

    def process_with_fingerprint(self, audio: np.ndarray, sr: int,
                                 params: dict | None = None,
                                 test_freq: float = 1000.0
                                 ) -> tuple[np.ndarray, ProcessorFingerprint]:
        """处理音频并返回效应指纹 (PHYS-003 §6 审计协议).

        Args:
            audio: 输入音频
            sr: 采样率
            params: 覆盖参数
            test_freq: THD 测量参考频率 [Hz]

        Returns:
            (processed_audio, ProcessorFingerprint)
        """
        p = params or self.params
        output = self._run_board(audio, sr, p)

        # PHYS-003 效应指纹测量
        fp = compute_thd(audio, output, sr, test_freq=test_freq)

        # CR_eff 估计 (基于压缩参数)
        try:
            nominal_ratio = _p(p, "P06_compression_ratio", 1.0)
            threshold_db = _p(p, "P09_compression_threshold", -24)
            input_peak = 20.0 * np.log10(np.max(np.abs(audio)) + 1e-12)
            fp.cr_eff = estimate_cr_eff(nominal_ratio, threshold_db, input_peak)
        except Exception:
            fp.cr_eff = 1.0

        # 瞬态保持度 (PHYS-003 §3.2)
        fp.transient_preservation = _compute_transient_preservation(audio, output, sr)

        # 谱质心偏移 (PHYS-003 §4)
        fp.spectral_centroid_shift = _compute_centroid_shift(audio, output, sr)

        return output, fp

    def process_with_audit(self, audio: np.ndarray, sr: int,
                           params: dict | None = None,
                           test_freq: float = 1000.0
                           ) -> tuple[np.ndarray, ProcessorFingerprint, ConservationReport]:
        """处理音频, 返回 (output, fingerprint, conservation_report).

        PHYS-007 §5.2 守恒审计:
          ΔL_residual = L_out - L_in - ΔL_dynamics - ΔL_spectral
          若 |ΔL_residual| > 3σ → 触发警告.
        """
        p = params or self.params
        output, fp = self.process_with_fingerprint(audio, sr, p, test_freq)

        # 测量输入输出响度
        l_in = _measure_lufs(audio, sr)
        l_out = _measure_lufs(output, sr)

        # 估计动态和频谱贡献
        delta_dynamics = _estimate_dynamic_contribution(audio, output, sr)
        delta_spectral = fp.spectral_centroid_shift / 2000.0  # 粗略归一化

        # 执行守恒审计
        report = audit_conservation(
            l_in=l_in, l_out=l_out,
            l_dynamics=delta_dynamics,
            l_spectral=delta_spectral,
            sigma_noise=0.15,  # LUFS 测量噪声
        )

        return output, fp, report

    def measure_chain_fingerprint(self, sr: int = 44100,
                                  test_freq: float = 1000.0
                                  ) -> ProcessorFingerprint:
        """使用纯音测试信号测量处理链的效应指纹.

        独立于音频内容 — 用于验证处理链本身的非线性特性.

        Args:
            sr: 采样率 [Hz]
            test_freq: 测试基频 [Hz]

        Returns:
            ProcessorFingerprint (仅 THD, CR_eff, 瞬态保持度)
        """
        test_signal = generate_test_signal(sr, duration_s=2.0, test_freq=test_freq)
        _, fp = self.process_with_fingerprint(test_signal, sr, test_freq=test_freq)
        return fp


# ── 内部辅助函数 ──────────────────────────────────

def _compute_transient_preservation(audio_in: np.ndarray, audio_out: np.ndarray,
                                    sr: int) -> float:
    """PHYS-003 §3.2 定义 2: 瞬态保持度 T_p = A_transient_out / A_transient_in."""
    try:
        # 使用 onset strength 作为瞬态幅度代理
        in_mono = audio_in if audio_in.ndim == 1 else audio_in.mean(axis=1)
        out_mono = audio_out if audio_out.ndim == 1 else audio_out.mean(axis=1)

        # 简化的 onset detection: 用 RMS 包络变化率
        frame_len = int(0.01 * sr)  # 10ms
        hop = frame_len // 2
        n_frames = (min(len(in_mono), len(out_mono)) - frame_len) // hop

        if n_frames < 2:
            return 1.0

        in_env = np.array([
            np.sqrt(np.mean(in_mono[i*hop:i*hop+frame_len] ** 2))
            for i in range(n_frames)
        ])
        out_env = np.array([
            np.sqrt(np.mean(out_mono[i*hop:i*hop+frame_len] ** 2))
            for i in range(n_frames)
        ])

        # 取包络差分 > 0 的部分 (瞬态正跳变) 的均值
        in_onsets = np.diff(in_env)
        out_onsets = np.diff(out_env)
        in_transient = np.mean(in_onsets[in_onsets > 0]) if np.any(in_onsets > 0) else 1e-6
        out_transient = np.mean(out_onsets[out_onsets > 0]) if np.any(out_onsets > 0) else 1e-6

        ratio = out_transient / max(in_transient, 1e-12)
        return float(np.clip(ratio, 0.0, 2.0))
    except Exception:
        return 1.0


def _compute_centroid_shift(audio_in: np.ndarray, audio_out: np.ndarray,
                            sr: int) -> float:
    """计算处理后谱质心偏移 [Hz]."""
    try:
        in_mono = audio_in if audio_in.ndim == 1 else audio_in.mean(axis=1)
        out_mono = audio_out if audio_out.ndim == 1 else audio_out.mean(axis=1)
        n = min(len(in_mono), len(out_mono), 2 ** 14)

        spec_in = np.abs(np.fft.rfft(in_mono[:n]))
        spec_out = np.abs(np.fft.rfft(out_mono[:n]))
        freqs = np.fft.rfftfreq(n, 1.0 / sr)

        centroid_in = np.sum(freqs * spec_in) / max(np.sum(spec_in), 1e-12)
        centroid_out = np.sum(freqs * spec_out) / max(np.sum(spec_out), 1e-12)

        return float(centroid_out - centroid_in)
    except Exception:
        return 0.0


# ── 守恒审计辅助函数 (SPEC-011 T5) ──────────────────

def _measure_lufs(audio: np.ndarray, sr: int) -> float:
    """测量音频响度 [LUFS]. 优先 pyloudnorm, 回退 RMS."""
    try:
        import pyloudnorm as pyln
        meter = pyln.Meter(sr)
        return meter.integrated_loudness(audio)
    except ImportError:
        mono = audio if audio.ndim == 1 else audio.mean(axis=1)
        rms = np.sqrt(np.mean(mono ** 2) + 1e-12)
        return 20.0 * math.log10(rms)  # RMS dB 近似


def _estimate_dynamic_contribution(audio_in: np.ndarray,
                                   audio_out: np.ndarray,
                                   sr: int) -> float:
    """估计动态处理对响度变化的贡献 [LU].

    PHYS-001 定理 2: 使用 crest factor 变化作为代理.
    """
    try:
        in_mono = audio_in if audio_in.ndim == 1 else audio_in.mean(axis=1)
        out_mono = audio_out if audio_out.ndim == 1 else audio_out.mean(axis=1)

        rms_in = np.sqrt(np.mean(in_mono ** 2) + 1e-12)
        rms_out = np.sqrt(np.mean(out_mono ** 2) + 1e-12)
        peak_in = np.max(np.abs(in_mono))
        peak_out = np.max(np.abs(out_mono))

        crest_in = peak_in / max(rms_in, 1e-12)
        crest_out = peak_out / max(rms_out, 1e-12)

        # crest factor 变化映射到响度贡献 (dB 尺度)
        delta_crest_db = 20.0 * math.log10(max(crest_out, 1e-12) / max(crest_in, 1e-12))
        return round(delta_crest_db, 2)
    except Exception:
        return 0.0


def create_chain_from_code(emotion_code: str) -> MoodifyDSPChain:
    from moodify.knowledge.craft_chains import get_recommended_params
    return MoodifyDSPChain(get_recommended_params(emotion_code))
