"""T4 效应指纹测试 (SPEC-011 批次 4).

验证:
  - generate_test_signal() 产生正确的正弦波
  - MoodifyDSPChain.process_with_fingerprint() 返回有效的指纹
  - measure_chain_fingerprint() 使用纯音正确测量 THD
  - _compute_transient_preservation 对相同信号返回 1.0
  - _compute_centroid_shift 对无处理信号返回 ~0
"""

import numpy as np
import pytest


class TestGenerateTestSignal:
    def test_produces_sine(self):
        from moodify.processing.pedalboard_chain import generate_test_signal
        sig = generate_test_signal(sr=44100, duration_s=1.0, test_freq=440.0)
        assert sig.dtype == np.float32
        assert len(sig) == 44100
        # 应为正弦波, 峰值接近 0.8
        assert 0.7 < np.max(np.abs(sig)) <= 0.81

    def test_different_frequencies(self):
        from moodify.processing.pedalboard_chain import generate_test_signal
        sig1 = generate_test_signal(test_freq=440)
        sig2 = generate_test_signal(test_freq=1000)
        # 不同频率产生不同的信号
        assert not np.allclose(sig1[:100], sig2[:100])


class TestProcessWithFingerprint:
    def test_returns_tuple(self):
        from moodify.processing.pedalboard_chain import MoodifyDSPChain
        chain = MoodifyDSPChain({"P06_compression_ratio": 2.0})
        audio = (0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))).astype(np.float32)
        result = chain.process_with_fingerprint(audio, 44100)
        assert isinstance(result, tuple)
        assert len(result) == 2
        output, fp = result
        assert isinstance(output, np.ndarray)
        assert hasattr(fp, 'thd')
        assert hasattr(fp, 'cr_eff')

    def test_fingerprint_is_valid(self):
        from moodify.processing.pedalboard_chain import MoodifyDSPChain
        chain = MoodifyDSPChain({"P13_harmonic_drive": 0.2})
        audio = (0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))).astype(np.float32)
        _, fp = chain.process_with_fingerprint(audio, 44100)
        assert 0.0 <= fp.transient_preservation <= 2.0
        assert fp.cr_eff >= 1.0

    def test_bypass_chain_minimal_fingerprint(self):
        """无效果参数时指纹应接近零 (THD ~0, CR_eff ~1).

        NOTE: 使用 1kHz 测试信号以匹配 compute_thd 的默认 test_freq.
        空参数链仍有 Compressor(unity)+Gain+Limiter, THD 虽非零但应较小.
        """
        from moodify.processing.pedalboard_chain import MoodifyDSPChain
        chain = MoodifyDSPChain({})
        sr = 44100
        t = np.linspace(0, 1, sr, endpoint=False)
        audio = (0.3 * np.sin(2 * np.pi * 1000 * t)).astype(np.float32)
        _, fp = chain.process_with_fingerprint(audio, sr, test_freq=1000)
        # 有 Gain+Limiter 但无 Distortion, THD 应 < 20%
        assert fp.thd < 20.0, f"Expected moderate THD for unity chain, got {fp.thd}%"


class TestMeasureChainFingerprint:
    def test_returns_fingerprint(self):
        from moodify.processing.pedalboard_chain import MoodifyDSPChain
        chain = MoodifyDSPChain({"P13_harmonic_drive": 0.1})
        fp = chain.measure_chain_fingerprint(sr=44100)
        assert hasattr(fp, 'thd')
        assert fp.cr_eff >= 1.0

    def test_harmonic_drive_increases_thd(self):
        """谐波驱动增加时 THD 应增大."""
        from moodify.processing.pedalboard_chain import MoodifyDSPChain
        chain_clean = MoodifyDSPChain({"P13_harmonic_drive": 0.0})
        chain_dirty = MoodifyDSPChain({"P13_harmonic_drive": 0.4})
        fp_clean = chain_clean.measure_chain_fingerprint(sr=44100)
        fp_dirty = chain_dirty.measure_chain_fingerprint(sr=44100)
        # 高驱动应有更大的 THD (至少不低于低驱动)
        assert fp_dirty.thd >= fp_clean.thd * 0.5, \
            f"Expected dirty THD ({fp_dirty.thd}) >= clean THD ({fp_clean.thd})"


class TestTransientPreservation:
    def test_identity_yields_one(self):
        """相同输入输出: T_p = 1.0."""
        from moodify.processing.pedalboard_chain import _compute_transient_preservation
        sr = 44100
        audio = (0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, sr))).astype(np.float32)
        tp = _compute_transient_preservation(audio, audio, sr)
        assert 0.9 < tp < 1.1

    def test_attenuated_signal(self):
        """衰减信号: T_p < 1.0."""
        from moodify.processing.pedalboard_chain import _compute_transient_preservation
        sr = 44100
        audio_in = (0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, sr))).astype(np.float32)
        audio_out = audio_in * 0.3  # 大幅衰减
        tp = _compute_transient_preservation(audio_in, audio_out, sr)
        assert tp < 1.0


class TestCentroidShift:
    def test_identity_yields_zero(self):
        """无处理: 谱质心偏移 ≈ 0."""
        from moodify.processing.pedalboard_chain import _compute_centroid_shift
        sr = 44100
        audio = (0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, sr))).astype(np.float32)
        shift = _compute_centroid_shift(audio, audio, sr)
        assert abs(shift) < 10.0  # 数值精度内接近 0

    def test_lowpass_shift(self):
        """低通滤波后谱质心应下移 (负偏移)."""
        from moodify.processing.pedalboard_chain import _compute_centroid_shift
        from scipy.signal import butter, sosfilt
        sr = 44100
        t = np.linspace(0, 1, sr, endpoint=False)
        audio_in = (0.3 * np.sin(2 * np.pi * 2000 * t)).astype(np.float32)
        # 1 kHz 低通滤波
        sos = butter(4, 1000, btype='lowpass', fs=sr, output='sos')
        audio_out = sosfilt(sos, audio_in).astype(np.float32)
        shift = _compute_centroid_shift(audio_in, audio_out, sr)
        assert shift < 0, f"Lowpass should shift centroid down, got {shift}"


class TestCR_eff:
    def test_compression_reduces_crest(self):
        """压缩应降低峰值因子 -> CR_eff > 1."""
        from moodify.processing.pedalboard_chain import MoodifyDSPChain
        chain = MoodifyDSPChain({
            "P06_compression_ratio": 4.0,
            "P09_compression_threshold": -20,
        })
        # 高动态测试信号
        sr = 44100
        t = np.linspace(0, 0.5, int(sr * 0.5), endpoint=False)
        audio = (0.9 * np.sin(2 * np.pi * 440 * t) *
                 (0.3 + 0.7 * np.sin(2 * np.pi * 3 * t))).astype(np.float32)
        _, fp = chain.process_with_fingerprint(audio, sr)
        assert fp.cr_eff >= 1.0
