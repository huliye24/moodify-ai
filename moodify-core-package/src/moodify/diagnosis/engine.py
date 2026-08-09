"""
diagnosis_engine.py — 完整 18 参数诊断引擎 (SPEC §5)
======================================================
Moodify 核心引擎的"第一触点"——将 AI 音频的波场状态量化为 18 个可计算参数。

Pattern: 每个参数独立计算, 失败时回退到默认值 (best-effort measurement)。
         except Exception 是设计选择——个别参数不可算不应中断整条诊断管线。

依赖: moodify_metrics.py (已有), pyloudnorm (新增), librosa, scipy
输出: WaveStateDiagnosis 数据类

18 参数构成:
  频谱 S: S1(SubPresence) S2(BassWarmth) S3(MidClarity) S4(AirBand) S5(SpectralTilt)
  动态 D: D1(LRA) D2(ChorusImpact) D3(MicroDynamics) D4(PLR)
  空间 SP: SP1(Correlation) SP2(ForeBackSep) SP3(RT60Consist) SP4(WidthHealth)
  层级 L: L1(VocalSNR) L2(BassClarity) L3(DrumDetect) L4(LayerCount)
  情绪 E: E1(Direction) E2(Richness) E3(FatigueRisk) E4(SectionCont)
"""

from __future__ import annotations

import logging
import math
import time

import numpy as np
from scipy.signal import butter, sosfilt
from scipy.ndimage import uniform_filter1d

from moodify.diagnosis.metrics import (
    SpectrumAnalyzer, DynamicsAnalyzer, SpaceAnalyzer, BANDS as EXISTING_BANDS, frame_signal, load_audio,
)
from moodify.data_types import (
    WaveStateDiagnosis, SpectrumDiagnosis, DynamicsDiagnosis,
    SpaceDiagnosis, LayersDiagnosis, EmotionDiagnosis,
    ParameterWithUncertainty,
)
from moodify.protocol import STFT_CONFIG_STANDARD, STFT_CONFIG_QUICK

logger = logging.getLogger(__name__)


# ============================================================
#  频段定义 (SPEC §5.1 — 调整 Bass 为 60-250Hz)
# ============================================================

DIAGNOSIS_BANDS = {
    "Sub":      (20,   60),
    "Bass":     (60,  250),   # SPEC: 60-250Hz for S2_BassWarmth
    "Low-Mid":  (250, 500),
    "Mid":      (500, 2000),
    "Presence": (2000, 5000),
    "Air":      (8000, 16000),
}


# ============================================================
#  DiagnosisEngine — 统一 18 参数提取
# ============================================================

class DiagnosisEngine:
    """完整 18 参数诊断引擎 (SPEC §4.2)"""

    def __init__(self, sr: int = 44100, n_fft: int = 2048):
        self.sr = sr
        self.n_fft = n_fft       # PHYS-002 标准: n_fft=2048
        self.hop_length = n_fft // 4  # PHYS-002 标准: hop=512
        self._fallbacks: dict[str, str] = {}  # SPEC-011 T3: 回退追踪

        # 现有权威计算器
        self._spec = SpectrumAnalyzer(n_fft=n_fft)
        self._dyn = DynamicsAnalyzer()
        self._space_analyzer = SpaceAnalyzer()

    # ——— 公共 API ————————————————————————————————

    def diagnose(self, audio_path: str,
                 target_emotion: str = "",
                 subjective: dict | None = None,
                 mode: str = "quick") -> WaveStateDiagnosis:
        """
        完整五维诊断流水线 -> 18 参数 WaveState

        Args:
            audio_path: 音频文件路径
            target_emotion: 目标情绪 (可选)
            subjective: 主观评分覆盖 {"L4": int, "E1": int, "E2": int}
            mode: "quick" (最小测量集, <5s) | "full" (全量, 含 RT60 等重型计算)
        """
        t0 = time.perf_counter()
        self._fallbacks.clear()  # SPEC-011 T3: 每次诊断前清空回退记录
        full_mode = (mode == "full")

        mono, sr, data = load_audio(audio_path)
        is_stereo = data.shape[1] >= 2
        if sr != self.sr:
            mono = self._resample_fast(mono, sr, self.sr)
            if is_stereo:
                data = np.stack([
                    self._resample_fast(data[:, 0], sr, self.sr),
                    self._resample_fast(data[:, 1], sr, self.sr),
                ], axis=1)
            sr = self.sr
        duration_s = len(mono) / sr

        # Pre-compute shared STFT for reuse (vectorized for speed)
        A, P, freqs = self._compute_stft_fast(mono, sr)

        spectrum = self._extract_spectrum_from_stft(A, P, freqs)
        dynamics = self._extract_dynamics(mono, sr, full_mode)
        space = self._extract_space(data, sr, full_mode) if is_stereo else SpaceDiagnosis()
        layers = self._extract_layers_optimized(mono, data, sr, is_stereo, A, P, freqs)
        emotion = self._extract_emotion_optimized(spectrum, dynamics, space, layers,
                                                   mono, sr, target_emotion, P, freqs, subjective)

        elapsed_ms = (time.perf_counter() - t0) * 1000
        if elapsed_ms > 5000:
            print(f"  WARN: diagnosis took {elapsed_ms:.0f}ms (target < 5000ms)")

        # SPEC-011 T3.4: 未消耗的回退标记 (说明 extract 方法遗漏了某个参数)
        if self._fallbacks:
            for k, v in self._fallbacks.items():
                print(f"  WARN: unpopped fallback [{k}]: {v}")

        stft_cfg = STFT_CONFIG_STANDARD.copy() if mode == "full" else STFT_CONFIG_QUICK.copy()
        return WaveStateDiagnosis(
            Spectrum=spectrum,
            Dynamics=dynamics,
            Space=space,
            Layers=layers,
            Emotion=emotion,
            audio_path=str(audio_path),
            duration_s=duration_s,
            sample_rate=sr,
            protocol_mode=mode,
            stft_config=stft_cfg,
        )

    @staticmethod
    def _resample_fast(signal: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Fast resampling: try soxr > scipy resample_poly > librosa"""
        if orig_sr == target_sr:
            return signal
        try:
            import soxr
            return soxr.resample(signal.astype(np.float64), orig_sr, target_sr).astype(np.float32)
        except ImportError as exc:
            logger.debug(f"[resample_fast] soxr unavailable, using scipy: {exc!r}")
        try:
            from scipy.signal import resample_poly
            from math import gcd
            g = gcd(orig_sr, target_sr)
            up = target_sr // g
            down = orig_sr // g
            return resample_poly(signal.astype(np.float64), up=up, down=down).astype(np.float32)
        except Exception as exc:
            logger.debug(f"[resample_fast] scipy resample failed, using librosa: {exc!r}")
        import librosa
        return librosa.resample(signal, orig_sr=orig_sr, target_sr=target_sr)

    @staticmethod
    def _compute_stft_fast(mono: np.ndarray, sr: int):
        """Vectorized STFT — PHYS-002 标准: N_FFT=2048, hop=512, hann."""
        n_fft = 2048
        hop = n_fft // 4  # 512
        from numpy.lib.stride_tricks import sliding_window_view
        window = np.hanning(n_fft).astype(np.float32)
        frames = sliding_window_view(mono.astype(np.float32), n_fft)[::hop] * window
        X = np.fft.rfft(frames)
        P = np.abs(X) ** 2
        A = np.abs(X)
        freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
        return A, P, freqs

    # ——— Spectrum S1-S5 (§5.1) ————————————————————

    def _extract_spectrum(self, mono: np.ndarray, sr: int) -> SpectrumDiagnosis:
        A, P, freqs, _ = self._spec.stft(mono, sr)
        return self._extract_spectrum_from_stft(A, P, freqs)

    def _extract_spectrum_from_stft(self, A: np.ndarray, P: np.ndarray,
                                    freqs: np.ndarray) -> SpectrumDiagnosis:

        full_rms = np.sqrt(np.mean(np.sum(P, axis=1)) + 1e-12)

        def band_rms_db(f1, f2):
            mask = (freqs >= f1) & (freqs <= f2)
            band_energy = np.mean(np.sum(P[:, mask], axis=1))
            return 20.0 * math.log10(np.sqrt(band_energy + 1e-12) / (full_rms + 1e-12))

        # S1: SubPresence — RMS(20-60Hz) / RMS(full) [dB] — SPEC §5.1
        S1 = band_rms_db(20, 60)

        # S2: BassWarmth — RMS(60-250Hz) / RMS(full) [dB] — SPEC §5.1
        S2 = band_rms_db(60, 250)

        # S3: MidClarity — 1 - MaskingIndex(250-5000Hz) [0-1] — SPEC §5.1
        # 用拥挤度作为掩蔽代理: clarity = 1 - mean(crowd in mid bands)
        self._spec.all_band_energies(P, freqs)  # preload band energies
        # 使用现有 BANDS 计算拥挤度
        total_energy = float(np.mean(np.sum(P, axis=1)))
        crowding = {}
        for name, (f1, f2) in EXISTING_BANDS.items():
            mask_b = (freqs >= f1) & (freqs <= f2)
            e_band = float(np.mean(np.sum(P[:, mask_b], axis=1)))
            crowding[name] = e_band / (total_energy + 1e-12)

        # 中频掩蔽: Low-Mid + Mid + Presence 的拥挤度均值
        mid_crowding = np.mean([
            crowding.get("Low-Mid", 0.15),
            crowding.get("Mid", 0.20),
            crowding.get("Presence", 0.10),
        ])
        S3 = round(1.0 - mid_crowding, 4)

        # S4: AirBand — RMS(8-16kHz) / RMS(full) [dB] — SPEC §5.1
        S4 = band_rms_db(8000, 16000)

        # S5: SpectralTilt — linear fit log(freq) vs log(amp) [dB/oct] — SPEC §5.1
        spectrum_mean = np.mean(A, axis=0)  # 时间平均的幅值谱
        valid = (freqs >= 100) & (freqs <= 15000) & (spectrum_mean > 1e-10)
        if np.sum(valid) > 5:
            slope = np.polyfit(np.log2(freqs[valid]), np.log2(spectrum_mean[valid]), 1)[0]
            # log2 斜率 → dB/oct: 1 oct = 3 dB per oct 基准
            S5 = round(float(slope * 6.0), 2)  # 幅值 → 能量: slope*2, dB/oct 近似
        else:
            S5 = 0.0

        return SpectrumDiagnosis(
            S1_SubPresence=ParameterWithUncertainty(value=round(S1, 2)),
            S2_BassWarmth=ParameterWithUncertainty(value=round(S2, 2)),
            S3_MidClarity=ParameterWithUncertainty(value=S3),
            S4_AirBand=ParameterWithUncertainty(value=round(S4, 2)),
            S5_SpectralTilt=ParameterWithUncertainty(value=S5),
        )

    # ——— 动态维度 D1-D4 (§5.2) ————————————————————

    def _extract_dynamics(self, mono: np.ndarray, sr: int,
                          full_mode: bool = False) -> DynamicsDiagnosis:
        D1 = self._compute_lra(mono, sr)
        if full_mode:
            dyn_result = self._dyn.diagnose(mono, sr)
            D2 = self._compute_chorus_impact(mono, sr)
            D3 = self._compute_micro_dynamics(mono, sr)
            peak_db = float(dyn_result.get("Peak_max_dB", -6.0))
        else:
            D2 = self._estimate_chorus_impact_quick(mono, sr)
            D3 = self._estimate_micro_dynamics_fast(mono, sr)
            peak_db = 20.0 * math.log10(np.max(np.abs(mono)) + 1e-12)
            # 快速模式使用简化算法, 标记为回退
            self._fallbacks.setdefault("D2_ChorusImpact",
                "quick mode: RMS contrast instead of LUFS")
            self._fallbacks.setdefault("D3_MicroDynamics",
                "quick mode: RMS frame diffs instead of momentary-vs-short-term LUFS")
        integrated_lufs = self._get_integrated_lufs(mono, sr)
        D4 = round(peak_db - integrated_lufs, 2)

        def _p(val, key):
            fb = key in self._fallbacks
            note = self._fallbacks.pop(key, "")
            return ParameterWithUncertainty(
                value=val, is_fallback=fb, fallback_note=note,
                confidence="low" if fb else "medium",
            )

        return DynamicsDiagnosis(
            D1_LRA=_p(round(D1, 2), "D1_LRA"),
            D2_ChorusImpact=_p(round(D2, 2), "D2_ChorusImpact"),
            D3_MicroDynamics=_p(round(D3, 3), "D3_MicroDynamics"),
            D4_PLR=_p(D4, "D4_PLR"),
        )

    def _compute_lra(self, mono: np.ndarray, sr: int) -> float:
        """EBU 3342 LRA 计算"""
        try:
            import pyloudnorm as pyln
            meter = pyln.Meter(sr)
            # 3 秒块
            block_s = 3.0
            block_len = int(block_s * sr)
            n_blocks = max(1, len(mono) // block_len)
            block_loudness = []
            for i in range(n_blocks):
                start = i * block_len
                end = min(start + block_len, len(mono))
                block = mono[start:end]
                if len(block) < sr * 0.5:  # < 0.5s 跳过
                    continue
                try:
                    loud = meter.integrated_loudness(block)
                    block_loudness.append(loud)
                except Exception:
                    continue

            if len(block_loudness) < 3:
                self._fallbacks["D1_LRA"] = (
                    f"insufficient blocks ({len(block_loudness)} < 3), using default 6.0 LU"
                )
                return 6.0

            # 排序 → 高低百分位差
            sorted_loud = sorted(block_loudness)
            n = len(sorted_loud)
            p10 = sorted_loud[int(n * 0.10)]
            p95 = sorted_loud[int(n * 0.95)]
            return p95 - p10
        except ImportError:
            self._fallbacks["D1_LRA"] = "pyloudnorm unavailable, using RMS-based LRA estimate"
            return self._estimate_lra_fallback(mono, sr)

    def _estimate_lra_fallback(self, mono: np.ndarray, sr: int) -> float:
        """无 pyloudnorm 时的 LRA 估算 (偏差估计: ±2 LU)."""
        frames, _ = frame_signal(mono, sr, frame_ms=3000, hop_ms=1500)
        rms_vals = 20 * np.log10(np.sqrt(np.mean(frames**2, axis=1) + 1e-12))
        if len(rms_vals) < 3:
            return 6.0
        sorted_rms = np.sort(rms_vals)
        n = len(sorted_rms)
        return float(sorted_rms[int(n*0.95)] - sorted_rms[int(n*0.10)])

    def _compute_chorus_impact(self, mono: np.ndarray, sr: int) -> float:
        """副歌冲击力: 4 段中最大最小响度差."""
        try:
            import pyloudnorm as pyln
            meter = pyln.Meter(sr)
        except ImportError:
            self._fallbacks["D2_ChorusImpact"] = (
                "pyloudnorm unavailable, using default 3.0 LU"
            )
            return 3.0

        # 分为 4 段
        n_sections = 4
        sec_len = len(mono) // n_sections
        sec_loudness = []
        for i in range(n_sections):
            start = i * sec_len
            end = (i + 1) * sec_len if i < n_sections - 1 else len(mono)
            block = mono[start:end]
            if len(block) < sr:
                continue
            try:
                sec_loudness.append(meter.integrated_loudness(block))
            except Exception:
                continue

        if len(sec_loudness) < 2:
            self._fallbacks["D2_ChorusImpact"] = (
                f"insufficient sections ({len(sec_loudness)} < 2), using default 3.0 LU"
            )
            return 3.0
        return max(sec_loudness) - min(sec_loudness)

    def _compute_micro_dynamics(self, mono: np.ndarray, sr: int) -> float:
        """微动态: mean(|momentary(400ms) - short_term(3s)|) [LU]."""
        try:
            import pyloudnorm as pyln
            meter = pyln.Meter(sr)
        except ImportError:
            self._fallbacks["D3_MicroDynamics"] = (
                "pyloudnorm unavailable, using default 1.0 LU"
            )
            return 1.0

        # 短时 (3s) 响度
        block_3s = int(3.0 * sr)
        n_st = max(1, len(mono) // block_3s)
        st_loudness = np.zeros(n_st)
        for i in range(n_st):
            start = i * block_3s
            end = min(start + block_3s, len(mono))
            try:
                st_loudness[i] = meter.integrated_loudness(mono[start:end])
            except Exception:
                st_loudness[i] = -23.0

        # 瞬态 (400ms) 响度
        block_400ms = int(0.4 * sr)
        n_mom = max(1, len(mono) // block_400ms)
        mom_loudness = np.zeros(n_mom)
        for i in range(n_mom):
            start = i * block_400ms
            end = min(start + block_400ms, len(mono))
            try:
                mom_loudness[i] = meter.integrated_loudness(mono[start:end])
            except Exception:
                mom_loudness[i] = -23.0

        # 将 momentary 对齐到 short-term 时间轴
        ratio = n_mom // n_st
        if ratio < 1:
            self._fallbacks["D3_MicroDynamics"] = (
                f"momentary/short-term ratio < 1 ({ratio=}), using default 1.0 LU"
            )
            return 1.0
        mom_aligned = np.array([
            np.mean(mom_loudness[i*ratio:(i+1)*ratio])
            for i in range(n_st)
        ])
        return float(np.mean(np.abs(mom_aligned - st_loudness)))

    def _get_integrated_lufs(self, mono: np.ndarray, sr: int) -> float:
        try:
            import pyloudnorm as pyln
            meter = pyln.Meter(sr)
            return meter.integrated_loudness(mono)
        except ImportError:
            self._fallbacks["D4_PLR"] = "pyloudnorm unavailable, using RMS-based LUFS estimate"
            rms_db = 20 * math.log10(np.sqrt(np.mean(mono**2) + 1e-12))
            return rms_db

    # ——— 空间维度 SP1-SP4 (§5.3) ————————————————————

    def _extract_space(self, data: np.ndarray, sr: int,
                       full_mode: bool = False) -> SpaceDiagnosis:
        left = data[:, 0]
        right = data[:, 1]
        SP2 = self._compute_fore_back_sep(left, right, sr)
        if full_mode:
            space_result = self._space_analyzer.diagnose(left, right, sr)
            SP1 = float(space_result.get("Corr_LR_mean", 0.5))
            SP3 = self._compute_rt60_consist(left, right, sr)
            SP4 = self._compute_width_health(space_result)
        else:
            SP1 = self._compute_correlation_quick(left, right)
            SP3 = 0.3
            SP4 = (SP1 > 0.0)
            self._fallbacks.setdefault("SP3_RT60Consist",
                "quick mode: hardcoded default 0.3 instead of RT60 measurement")

        def _p(val, key):
            fb = key in self._fallbacks
            note = self._fallbacks.pop(key, "")
            return ParameterWithUncertainty(
                value=val, is_fallback=fb, fallback_note=note,
                confidence="low" if fb else "medium",
            )

        return SpaceDiagnosis(
            SP1_Correlation=_p(round(SP1, 4), "SP1_Correlation"),
            SP2_ForeBackSep=_p(round(SP2, 2), "SP2_ForeBackSep"),
            SP3_RT60Consist=_p(round(SP3, 3), "SP3_RT60Consist"),
            SP4_WidthHealth=SP4,
        )

    def _compute_correlation_quick(self, left: np.ndarray, right: np.ndarray) -> float:
        """Quick global Pearson correlation"""
        std_l, std_r = np.std(left), np.std(right)
        if std_l < 1e-12 or std_r < 1e-12:
            return 1.0
        return float(np.corrcoef(left, right)[0, 1])

    def _compute_fore_back_sep(self, left: np.ndarray, right: np.ndarray,
                                sr: int) -> float:
        """M/S 中频能量比 [dB]"""
        mid = (left + right) / 2.0
        side = (left - right) / 2.0

        # 带通滤波 250-5000Hz
        sos = butter(4, [250, 5000], btype='bandpass', fs=sr, output='sos')
        mid_filtered = sosfilt(sos, mid)
        side_filtered = sosfilt(sos, side)

        e_mid = np.sum(mid_filtered**2) + 1e-12
        e_side = np.sum(side_filtered**2) + 1e-12
        return 10.0 * math.log10(e_mid / e_side)

    def _compute_rt60_consist(self, left: np.ndarray, right: np.ndarray,
                               sr: int) -> float:
        """各倍频程 RT60 标准差 [s]"""
        mono = (left + right) / 2.0
        octave_centers = [125, 250, 500, 1000, 2000, 4000, 8000]
        rt60_values = []
        for fc in octave_centers:
            try:
                rt = self._estimate_rt60_band(mono, sr, fc)
                if rt is not None and rt > 0.05:
                    rt60_values.append(rt)
            except Exception:
                continue
        if len(rt60_values) < 3:
            return 0.3
        return float(np.std(rt60_values))

    def _estimate_rt60_band(self, mono: np.ndarray, sr: int,
                             center_freq: float) -> float | None:
        """估计单个倍频程的 RT60"""
        lo = center_freq / 1.414
        hi = center_freq * 1.414
        sos = butter(2, [lo, hi], btype='bandpass', fs=sr, output='sos')
        filtered = sosfilt(sos, mono)

        # 包络检测
        envelope = np.abs(filtered)
        envelope = uniform_filter1d(envelope, int(sr * 0.05))

        # Schroeder 积分法估计衰减
        # 找峰值后的衰减
        peak_idx = np.argmax(envelope)
        tail = envelope[peak_idx:]

        if len(tail) < sr * 0.1:
            return None

        # 从 -5dB 到 -35dB 的衰减时间 × 2 = RT60 估计
        peak_val = np.max(tail)
        db_envelope = 20 * np.log10(tail / peak_val + 1e-12)

        idx_m5 = np.argmax(db_envelope <= -5)
        idx_m25 = np.argmax(db_envelope <= -25)

        if idx_m5 == 0 or idx_m25 == 0 or idx_m5 >= idx_m25:
            return None

        t20 = (idx_m25 - idx_m5) / sr
        return t20 * 3.0  # T20 → RT60

    def _compute_width_health(self, space_result: dict) -> bool:
        """SP4: WidthHealth — corr(2k-8k) > 0 AND mono compatible"""
        corr_lr = float(space_result.get("Corr_LR_mean", 0.5))
        mono_compat = float(space_result.get("MonoCompatibility", 0.8))
        # 简化为: corr 在安全区间且 mono 兼容性好
        return corr_lr > 0.0 and mono_compat > 0.6

    # ——— 层级维度 L1-L4 (§5.4) ————————————————————

    def _extract_layers(self, mono: np.ndarray, data: np.ndarray,
                         sr: int, is_stereo: bool) -> LayersDiagnosis:
        A, P, freqs, _ = self._spec.stft(mono, sr)
        return self._extract_layers_optimized(mono, data, sr, is_stereo, A, P, freqs)

    def _extract_layers_optimized(self, mono: np.ndarray, data: np.ndarray,
                                   sr: int, is_stereo: bool,
                                   A: np.ndarray, P: np.ndarray,
                                   freqs: np.ndarray) -> LayersDiagnosis:
        L1 = self._compute_vocal_snr(data, sr, is_stereo)
        L2 = self._compute_bass_clarity(P, freqs)
        L3 = self._compute_drum_detect_fast(mono, sr)
        L4 = 3  # 主观评分, 非回退

        def _p(val, key):
            fb = key in self._fallbacks
            note = self._fallbacks.pop(key, "")
            return ParameterWithUncertainty(
                value=val, is_fallback=fb, fallback_note=note,
                confidence="low" if fb else "medium",
            )

        return LayersDiagnosis(
            L1_VocalSNR=_p(round(L1, 2), "L1_VocalSNR"),
            L2_BassClarity=_p(round(L2, 4), "L2_BassClarity"),
            L3_DrumDetect=_p(round(L3, 4), "L3_DrumDetect"),
            L4_LayerCount=ParameterWithUncertainty(value=float(L4), level="L2"),
        )

    def _compute_vocal_snr(self, data: np.ndarray, sr: int,
                            is_stereo: bool) -> float:
        """人声 SNR: M/S 分解后中声道 1-4kHz vs 侧声道 1-4kHz."""
        if not is_stereo or data.shape[1] < 2:
            self._fallbacks["L1_VocalSNR"] = "mono audio, using default 6.0 dB"
            return 6.0

        mid = (data[:, 0] + data[:, 1]) / 2.0
        side = (data[:, 0] - data[:, 1]) / 2.0

        sos = butter(4, [1000, 4000], btype='bandpass', fs=sr, output='sos')
        mid_band = sosfilt(sos, mid)
        side_band = sosfilt(sos, side)

        rms_mid = np.sqrt(np.mean(mid_band**2) + 1e-12)
        rms_side = np.sqrt(np.mean(side_band**2) + 1e-12)
        return 20.0 * math.log10(rms_mid / rms_side)

    def _compute_bass_clarity(self, P: np.ndarray, freqs: np.ndarray) -> float:
        """L2: 低频段频谱集中度 — 1 - entropy [0-1]"""
        mask = (freqs >= 20) & (freqs <= 250)
        bass_spectrum = np.mean(P[:, mask], axis=0)
        bass_spectrum = bass_spectrum / (np.sum(bass_spectrum) + 1e-12)
        entropy = -np.sum(bass_spectrum * np.log2(bass_spectrum + 1e-12))
        max_entropy = np.log2(len(bass_spectrum))
        if max_entropy < 1e-12:
            return 0.5
        return round(1.0 - entropy / max_entropy, 4)

    def _compute_drum_detect(self, mono: np.ndarray, sr: int) -> float:
        """L3: transient detection rate via librosa onset_detect (full mode)."""
        try:
            import librosa
            onset_frames = librosa.onset.onset_detect(
                y=mono, sr=sr,
                hop_length=self.hop_length,
                backtrack=True,
            )
            duration_s = len(mono) / sr
            estimated_bpm = 120
            expected_events = duration_s * estimated_bpm / 60 * 4
            rate = len(onset_frames) / max(expected_events, 1)
            return min(1.0, rate)
        except Exception:
            self._fallbacks["L3_DrumDetect"] = (
                "librosa onset_detect failed, using default 0.5"
            )
            return 0.5

    def _compute_drum_detect_fast(self, mono: np.ndarray, sr: int) -> float:
        """L3 fast: frame energy peak detection instead of librosa onset."""
        frames, _ = frame_signal(mono, sr, frame_ms=23, hop_ms=11)  # ~44fps
        rms_frames = np.sqrt(np.mean(frames**2, axis=1) + 1e-12)
        if len(rms_frames) < 10:
            self._fallbacks["L3_DrumDetect"] = (
                f"insufficient frames ({len(rms_frames)} < 10), using default 0.5"
            )
            return 0.5
        # Detect peaks in RMS energy envelope
        rms_smooth = uniform_filter1d(rms_frames, 5)
        diffs = np.diff(rms_smooth)
        # Count positive-to-negative zero crossings (peaks)
        peaks = np.sum((diffs[:-1] > 0) & (diffs[1:] < 0))
        duration_s = len(mono) / sr
        expected_events = duration_s * 120 / 60 * 4
        return min(1.0, peaks / max(expected_events, 1))

    # ——— Emotion E1-E4 (§5.5) ————————————————————

    def _extract_emotion(self, spectrum: SpectrumDiagnosis,
                          dynamics: DynamicsDiagnosis,
                          space: SpaceDiagnosis,
                          layers: LayersDiagnosis,
                          mono: np.ndarray, sr: int,
                          target_emotion: str,
                          subjective: dict | None) -> EmotionDiagnosis:
        return self._extract_emotion_optimized(spectrum, dynamics, space, layers,
                                                mono, sr, target_emotion, None, None, subjective)

    def _extract_emotion_optimized(self, spectrum: SpectrumDiagnosis,
                                    dynamics: DynamicsDiagnosis,
                                    space: SpaceDiagnosis,
                                    layers: LayersDiagnosis,
                                    mono: np.ndarray, sr: int,
                                    target_emotion: str,
                                    P: np.ndarray | None,
                                    freqs: np.ndarray | None,
                                    subjective: dict | None) -> EmotionDiagnosis:
        subj = subjective or {}
        E1 = subj.get("E1", 5)
        E2 = subj.get("E2", 5)

        roughness = self._compute_roughness_fast(mono, sr)
        lufs = abs(self._get_integrated_lufs(mono, sr))
        lra = max(dynamics.D1_LRA.value, 0.1)
        E3 = round((roughness * lufs) / lra, 2)

        if P is not None:
            E4 = self._compute_section_continuity_from_stft(P)
        else:
            E4 = self._compute_section_continuity(mono, sr)

        E1_is_fallback = "E1" not in (subjective or {})
        E2_is_fallback = "E2" not in (subjective or {})
        return EmotionDiagnosis(
            E1_Direction=ParameterWithUncertainty(
                value=float(E1), level="L2",
                is_fallback=E1_is_fallback,
                fallback_note="default value, no subjective rating" if E1_is_fallback else "",
            ),
            E2_Richness=ParameterWithUncertainty(
                value=float(E2), level="L2",
                is_fallback=E2_is_fallback,
                fallback_note="default value, no subjective rating" if E2_is_fallback else "",
            ),
            E3_FatigueRisk=ParameterWithUncertainty(value=E3),
            E4_SectionCont=ParameterWithUncertainty(value=round(E4, 4)),
        )

    def _compute_roughness_fast(self, mono: np.ndarray, sr: int) -> float:
        """Fast roughness: use frame-level energy fluctuation"""
        frames, _ = frame_signal(mono, sr, frame_ms=100, hop_ms=50)
        rms_frames = np.sqrt(np.mean(frames**2, axis=1) + 1e-12)
        if len(rms_frames) < 3:
            return 0.3
        return float(np.std(rms_frames) / (np.mean(rms_frames) + 1e-12))

    def _compute_section_continuity_from_stft(self, P: np.ndarray) -> float:
        """E4 from pre-computed STFT: split spectrogram into 4 sections"""
        n_frames = P.shape[0]
        if n_frames < 8:
            return 0.7
        n_sec = 4
        frames_per_sec = n_frames // n_sec
        spectra = []
        for i in range(n_sec):
            start = i * frames_per_sec
            end = (i+1) * frames_per_sec if i < n_sec-1 else n_frames
            spectra.append(np.mean(P[start:end, :], axis=0)[:256])
        distances = []
        for i in range(len(spectra) - 1):
            a = spectra[i] / (np.linalg.norm(spectra[i]) + 1e-12)
            b = spectra[i+1] / (np.linalg.norm(spectra[i+1]) + 1e-12)
            distances.append(1.0 - float(np.dot(a, b)))
        return 1.0 - float(np.mean(distances))

    def _compute_roughness(self, mono: np.ndarray, sr: int) -> float:
        """估算粗糙度 (简化 asper 模型)"""
        # 高频 (6-10kHz) 能量波动率
        sos = butter(4, [6000, 10000], btype='bandpass', fs=sr, output='sos')
        filtered = sosfilt(sos, mono)
        envelope = np.abs(filtered)
        # 包络标准差 / 均值 → 波动率指标
        env_std = np.std(envelope)
        env_mean = np.mean(envelope) + 1e-12
        return float(env_std / env_mean)

    def _compute_section_continuity(self, mono: np.ndarray, sr: int) -> float:
        """E4: 段落频谱连续性 [0-1]"""
        n_sections = 4
        sec_len = len(mono) // n_sections
        spectra = []
        for i in range(n_sections):
            start = i * sec_len
            end = (i + 1) * sec_len if i < n_sections - 1 else len(mono)
            block = mono[start:end]
            # 使用简化的频谱
            fft = np.abs(np.fft.rfft(block * np.hanning(len(block))))
            spectra.append(fft[:512])  # 前 512 bin

        distances = []
        for i in range(len(spectra) - 1):
            a = spectra[i] / (np.linalg.norm(spectra[i]) + 1e-12)
            b = spectra[i+1] / (np.linalg.norm(spectra[i+1]) + 1e-12)
            # cosine distance = 1 - cosine_similarity
            cos_sim = np.dot(a, b)
            distances.append(1.0 - cos_sim)

        return 1.0 - float(np.mean(distances))

    def diagnose_quick(self, audio_path: str) -> WaveStateDiagnosis:
        """最小测量集 — 仅自动参数, < 5s (E1/E2/L4 使用默认值)"""
        return self.diagnose(audio_path, subjective={"E1": 5, "E2": 5, "L4": 3}, mode="quick")

    # ——— 快速估算方法 (quick mode) ——————————————————

    def _estimate_chorus_impact_quick(self, mono: np.ndarray, sr: int) -> float:
        """Quick ChorusImpact: split into 4 sections, measure RMS contrast"""
        n_sec = 4
        sec_len = len(mono) // n_sec
        rms_vals = []
        for i in range(n_sec):
            start = i * sec_len
            end = (i+1) * sec_len if i < n_sec-1 else len(mono)
            rms = 20.0 * math.log10(np.sqrt(np.mean(mono[start:end]**2) + 1e-12))
            rms_vals.append(rms)
        return max(rms_vals) - min(rms_vals)

    def _estimate_micro_dynamics_fast(self, mono: np.ndarray, sr: int) -> float:
        """快速 MicroDynamics: 用 RMS 帧间变化近似"""
        frames, _ = frame_signal(mono, sr, frame_ms=400, hop_ms=200)
        rms_vals = np.sqrt(np.mean(frames**2, axis=1) + 1e-12)
        if len(rms_vals) < 5:
            return 1.0
        # 相邻帧变化均值
        diffs = np.abs(np.diff(rms_vals)) / (np.mean(rms_vals) + 1e-12)
        return float(np.clip(np.mean(diffs) * 10.0, 0.3, 3.0))
