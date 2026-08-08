"""AEP-ACU-001 单元测试 — Schroeder 混响合规修复.

验证:
  - _feedback_comb_filter: 稳定性, 无 NaN, 长度, 增益边界, 零输入
  - _allpass_filter: 稳定性, 无 NaN, 长度, 幅频平坦性, 增益边界
  - _schroeder_reverb: 端到端, mono/stereo 兼容, 旧版废弃警告
  - _schroeder_reverb_legacy: 废弃警告
"""

import numpy as np
import pytest


# ── Fixtures ──────────────────────────────────────────────

@pytest.fixture
def sr():
    return 44100


@pytest.fixture
def short_signal(sr):
    """0.5 秒 440 Hz 正弦波."""
    t = np.linspace(0, 0.5, int(sr * 0.5), endpoint=False)
    return (0.3 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)


@pytest.fixture
def impulse(sr):
    """单位脉冲信号 (dirac delta)."""
    sig = np.zeros(int(sr * 0.5), dtype=np.float32)
    sig[0] = 1.0
    return sig


@pytest.fixture
def white_noise(sr):
    """白噪声信号 — 用于幅频响应测试."""
    rng = np.random.RandomState(42)
    return rng.randn(int(sr * 0.5)).astype(np.float32) * 0.1


@pytest.fixture
def silence(sr):
    """静音信号."""
    return np.zeros(int(sr * 0.3), dtype=np.float32)


# ── _feedback_comb_filter 测试 ──────────────────────────

class TestFeedbackCombFilter:
    """标准反馈梳状滤波器: y[n] = x[n] + g * y[n-D]."""

    def test_output_no_nan(self, short_signal, sr):
        from moodify.processing.operators import _feedback_comb_filter
        out = _feedback_comb_filter(short_signal, sr, delay_s=0.03, rt60=1.5)
        assert not np.any(np.isnan(out))
        assert not np.any(np.isinf(out))

    def test_output_length(self, short_signal, sr):
        from moodify.processing.operators import _feedback_comb_filter
        delay_s = 0.03
        out = _feedback_comb_filter(short_signal, sr, delay_s=delay_s, rt60=1.5)
        # 输出长度 = 输入长度 + delay_samples (含混响尾音)
        assert len(out) == len(short_signal) + int(sr * delay_s)

    def test_zero_input_produces_zero_output(self, silence, sr):
        from moodify.processing.operators import _feedback_comb_filter
        out = _feedback_comb_filter(silence, sr, delay_s=0.03, rt60=1.5)
        assert np.allclose(out, 0.0, atol=1e-7)

    def test_impulse_has_feedback_tail(self, impulse, sr):
        """脉冲输入应产生指数衰减的反馈尾音."""
        from moodify.processing.operators import _feedback_comb_filter
        out = _feedback_comb_filter(impulse, sr, delay_s=0.03, rt60=1.5)
        # 脉冲后应有非零能量 (反馈尾音)
        tail_start = int(sr * 0.05)  # 50 ms 后
        assert np.max(np.abs(out[tail_start:])) > 0.0

    def test_gain_clamped_to_stable_range(self, short_signal, sr):
        """增益应始终 < 1.0 以保证稳定性."""
        from moodify.processing.operators import _feedback_comb_filter
        # 极短 RT60 → 极高增益，但应被 clamp 到 < 1
        out = _feedback_comb_filter(short_signal, sr, delay_s=0.03, rt60=0.01)
        assert not np.any(np.isnan(out))
        # 对极短 rt60，输出应仍有限
        assert np.max(np.abs(out)) < 1e3

    def test_various_delays(self, short_signal, sr):
        """不同延迟长度不应崩溃."""
        from moodify.processing.operators import _feedback_comb_filter
        for d in [0.01, 0.02, 0.03, 0.04, 0.05]:
            out = _feedback_comb_filter(short_signal, sr, delay_s=d, rt60=2.0)
            assert len(out) == len(short_signal) + int(sr * d)
            assert not np.any(np.isnan(out))

    def test_various_rt60(self, short_signal, sr):
        """不同 RT60 不应崩溃 — 更长 RT60 产生更强的混响尾音能量."""
        from moodify.processing.operators import _feedback_comb_filter
        energy_short = np.sum(
            _feedback_comb_filter(short_signal, sr, delay_s=0.03, rt60=0.5) ** 2
        )
        energy_long = np.sum(
            _feedback_comb_filter(short_signal, sr, delay_s=0.03, rt60=3.0) ** 2
        )
        # 更长 RT60 → 更少衰减 → 更多总能量
        assert energy_long > energy_short

    def test_mono_float64_compatible(self, sr):
        """float64 输入也应正确工作."""
        from moodify.processing.operators import _feedback_comb_filter
        sig = (0.3 * np.sin(2 * np.pi * 440 * np.linspace(0, 0.5, sr // 2))).astype(np.float64)
        out = _feedback_comb_filter(sig, sr, delay_s=0.03, rt60=1.5)
        assert out.dtype == np.float64
        assert not np.any(np.isnan(out))


# ── _allpass_filter 测试 ─────────────────────────────────

class TestAllpassFilter:
    """全通滤波器: y[n] = -g*x[n] + x[n-D] + g*y[n-D]."""

    def test_output_no_nan(self, short_signal, sr):
        from moodify.processing.operators import _allpass_filter
        out = _allpass_filter(short_signal, sr, delay_s=0.005, gain=0.7)
        assert not np.any(np.isnan(out))
        assert not np.any(np.isinf(out))

    def test_output_length(self, short_signal, sr):
        from moodify.processing.operators import _allpass_filter
        out = _allpass_filter(short_signal, sr, delay_s=0.005, gain=0.7)
        assert len(out) == len(short_signal)

    def test_zero_input_produces_zero_output(self, silence, sr):
        from moodify.processing.operators import _allpass_filter
        out = _allpass_filter(silence, sr, delay_s=0.005, gain=0.7)
        assert np.allclose(out, 0.0, atol=1e-7)

    def test_amplitude_approximately_preserved_white_noise(self, white_noise, sr):
        """全通滤波器应保持信号的总 RMS 能量大致不变 (< 3 dB 偏差)."""
        from moodify.processing.operators import _allpass_filter
        out = _allpass_filter(white_noise, sr, delay_s=0.005, gain=0.7)
        rms_in = np.sqrt(np.mean(white_noise ** 2))
        rms_out = np.sqrt(np.mean(out ** 2))
        ratio_db = 20 * np.log10(max(rms_out, 1e-12) / max(rms_in, 1e-12))
        # 对宽带信号，全通 RMS 比应在 ±3 dB 内
        assert -3.0 < ratio_db < 3.0, f"RMS ratio = {ratio_db:.2f} dB"

    def test_gain_zero_is_pure_delay(self, short_signal, sr):
        """g=0 时，全通退化为纯延迟: y[n] = x[n-D]."""
        from moodify.processing.operators import _allpass_filter
        delay_s = 0.005
        delay_samples = int(sr * delay_s)
        out = _allpass_filter(short_signal, sr, delay_s=delay_s, gain=0.0)
        # y[n] = x[n-D] for n >= D, 0 otherwise
        for n in range(delay_samples, len(short_signal)):
            assert np.isclose(out[n], short_signal[n - delay_samples], atol=1e-6)

    def test_gain_edge_cases(self, short_signal, sr):
        """边界增益值不应崩溃 (g=0.0, g=0.5, g=0.9, g=0.999)."""
        from moodify.processing.operators import _allpass_filter
        for g in [0.0, 0.5, 0.7, 0.9, 0.999]:
            out = _allpass_filter(short_signal, sr, delay_s=0.005, gain=g)
            assert len(out) == len(short_signal)
            assert not np.any(np.isnan(out))

    def test_gain_clamped(self, short_signal, sr):
        """非法增益值自动 clamp 到 [0, 0.999]."""
        from moodify.processing.operators import _allpass_filter
        # g=1.5 → clamp 到 0.999
        out = _allpass_filter(short_signal, sr, delay_s=0.005, gain=1.5)
        assert not np.any(np.isnan(out))
        # g=-0.5 → clamp 到 0.0
        out2 = _allpass_filter(short_signal, sr, delay_s=0.005, gain=-0.5)
        assert not np.any(np.isnan(out2))

    def test_allpass_stability_long_signal(self, sr):
        """长信号上不应发散."""
        from moodify.processing.operators import _allpass_filter
        sig = (0.3 * np.sin(2 * np.pi * 440 * np.linspace(0, 3.0, sr * 3))).astype(np.float32)
        out = _allpass_filter(sig, sr, delay_s=0.005, gain=0.7)
        assert not np.any(np.isnan(out))
        # 输出不应发散
        assert np.max(np.abs(out)) < 10.0


# ── _schroeder_reverb 集成测试 ───────────────────────────

class TestSchroederReverb:
    """新版 Schroeder 混响器 — parallel comb + serial all-pass."""

    def test_output_no_nan(self, short_signal, sr):
        from moodify.processing.operators import _schroeder_reverb
        out = _schroeder_reverb(short_signal, sr, rt60=1.5)
        assert not np.any(np.isnan(out))
        assert not np.any(np.isinf(out))

    def test_output_longer_than_input_tail(self, short_signal, sr):
        """混响输出应包含尾音扩展 (输出 > 输入)."""
        from moodify.processing.operators import _schroeder_reverb
        out = _schroeder_reverb(short_signal, sr, rt60=1.5)
        assert len(out) > len(short_signal)

    def test_zero_input_produces_zero_output(self, silence, sr):
        from moodify.processing.operators import _schroeder_reverb
        out = _schroeder_reverb(silence, sr, rt60=1.5)
        assert np.allclose(out, 0.0, atol=1e-7)

    def test_impulse_response_smooth_decay(self, impulse, sr):
        """脉冲响应衰减应比旧实现更平滑 — 新/旧峰值比对比."""
        from moodify.processing.operators import (
            _schroeder_reverb,
            _schroeder_reverb_legacy,
        )
        import warnings

        def _peak_ratio_in_tail(ir, sr, t_start=0.05, t_end=0.20):
            """测量 IR 尾部 (t_start-t_end 秒) 的峰值比."""
            a = int(sr * t_start)
            b = int(sr * t_end)
            if b >= len(ir) or b - a < 100:
                return float("nan")
            tail = np.abs(ir[a:b])
            window = max(len(tail) // 20, 10)
            local_means = np.convolve(tail, np.ones(window) / window, mode="same")
            peak_idx = np.argmax(tail)
            if local_means[peak_idx] > 0:
                return float(tail[peak_idx] / local_means[peak_idx])
            return float("inf")

        out_new = _schroeder_reverb(impulse, sr, rt60=1.5)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            out_old = _schroeder_reverb_legacy(impulse, sr, rt60=1.5)

        ratio_new = _peak_ratio_in_tail(out_new, sr)
        ratio_old = _peak_ratio_in_tail(out_old, sr)

        # 新实现的峰值比应低于旧实现 (更平滑)
        assert not np.isnan(ratio_new)
        assert not np.isnan(ratio_old)
        assert ratio_new < ratio_old, (
            f"New peak ratio ({ratio_new:.1f}) should be lower "
            f"than old ({ratio_old:.1f}) — new reverb should be smoother"
        )

    def test_various_rt60_stable(self, short_signal, sr):
        """不同 RT60 值不应崩溃."""
        from moodify.processing.operators import _schroeder_reverb
        for rt60 in [0.3, 0.5, 1.0, 1.5, 2.0, 3.0]:
            out = _schroeder_reverb(short_signal, sr, rt60=rt60)
            assert not np.any(np.isnan(out))

    def test_longer_rt60_more_energy(self, impulse, sr):
        """更长 RT60 → 更多混响尾音能量."""
        from moodify.processing.operators import _schroeder_reverb
        e_short = np.sum(_schroeder_reverb(impulse, sr, rt60=0.5) ** 2)
        e_long = np.sum(_schroeder_reverb(impulse, sr, rt60=2.0) ** 2)
        assert e_long > e_short

    def test_new_vs_legacy_both_run(self, short_signal, sr):
        """新旧实现都能运行，新实现输出有限."""
        from moodify.processing.operators import (
            _schroeder_reverb,
            _schroeder_reverb_legacy,
        )
        import warnings
        new_out = _schroeder_reverb(short_signal, sr, rt60=1.5)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            old_out = _schroeder_reverb_legacy(short_signal, sr, rt60=1.5)
        assert not np.any(np.isnan(new_out))
        assert not np.any(np.isnan(old_out))
        # 两者都应该产生非零输出
        assert np.max(np.abs(new_out)) > 0
        assert np.max(np.abs(old_out)) > 0

    def test_mono_float64_compatible(self, sr):
        """float64 输入也应正确工作."""
        from moodify.processing.operators import _schroeder_reverb
        sig = (0.3 * np.sin(2 * np.pi * 440 * np.linspace(0, 0.5, sr // 2))).astype(np.float64)
        out = _schroeder_reverb(sig, sr, rt60=1.5)
        assert not np.any(np.isnan(out))


# ── 旧版废弃测试 ─────────────────────────────────────────

class TestLegacyDeprecation:
    """旧版 _schroeder_reverb_legacy 的废弃标记."""

    def test_legacy_emits_deprecation_warning(self, short_signal, sr):
        """调用旧版应触发 DeprecationWarning."""
        from moodify.processing.operators import _schroeder_reverb_legacy
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = _schroeder_reverb_legacy(short_signal, sr, rt60=1.5)
            deprecation_warnings = [
                x for x in w if issubclass(x.category, DeprecationWarning)
            ]
            assert len(deprecation_warnings) >= 1

    def test_legacy_still_produces_valid_output(self, short_signal, sr):
        """旧版仍应产生有效输出 (向后兼容)."""
        from moodify.processing.operators import _schroeder_reverb_legacy
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            out = _schroeder_reverb_legacy(short_signal, sr, rt60=1.5)
        assert not np.any(np.isnan(out))
        assert len(out) > 0


# ── apply_reverb 兼容性测试 ──────────────────────────────

class TestApplyReverbCompatibility:
    """apply_reverb() 使用新版 _schroeder_reverb 后的兼容性."""

    def test_apply_reverb_mono(self, short_signal, sr):
        from moodify.processing.operators import apply_reverb
        out = apply_reverb(short_signal, sr, rt60_s=1.5, dry_wet=0.3)
        assert not np.any(np.isnan(out))
        assert len(out) == len(short_signal)  # apply_reverb 保持长度

    def test_apply_reverb_stereo(self, sr):
        from moodify.processing.operators import apply_reverb
        t = np.linspace(0, 1, sr, endpoint=False)
        left = (0.3 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
        right = (0.3 * np.sin(2 * np.pi * 554 * t)).astype(np.float32)
        stereo = np.column_stack([left, right])
        out = apply_reverb(stereo, sr, rt60_s=1.5, dry_wet=0.3)
        assert out.ndim == 2
        assert out.shape == stereo.shape
        assert not np.any(np.isnan(out))

    def test_apply_reverb_no_clipping(self, short_signal, sr):
        """输出不应超过安全电平 (peak < 0.98)."""
        from moodify.processing.operators import apply_reverb
        out = apply_reverb(short_signal, sr, rt60_s=2.0, dry_wet=0.5)
        assert np.max(np.abs(out)) <= 0.98

    def test_apply_reverb_dry_wet_zero_is_dry(self, short_signal, sr):
        """dry_wet=0 → 输出 ≈ 输入 (仅干信号)."""
        from moodify.processing.operators import apply_reverb
        out = apply_reverb(short_signal, sr, rt60_s=1.5, dry_wet=0.0)
        # 应接近 dry 信号 (mono path: result.mean(axis=1) then dry * mono)
        # 对于 mono 输入，dry_wet=0 输出应接近原信号
        assert np.allclose(out, short_signal, atol=0.02)
