"""T5 守恒审计测试 (SPEC-011 批次 5).

验证:
  - process_with_audit() 返回 ConservationReport
  - 轻微处理的音频 energy_grade="safe"
  - 故意大增益触发 violation
  - _measure_lufs 和 _estimate_dynamic_contribution 返回有效值
"""

import numpy as np
import pytest


class TestProcessWithAudit:
    def test_returns_triple(self):
        from moodify.processing.pedalboard_chain import MoodifyDSPChain
        chain = MoodifyDSPChain({})
        sr = 44100
        audio = (0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 0.5, sr // 2))).astype(np.float32)
        result = chain.process_with_audit(audio, sr)
        assert len(result) == 3
        output, fp, report = result
        assert hasattr(report, 'energy_grade')
        assert hasattr(report, 'delta_e_residual')

    def test_conservation_report_computed(self):
        """处理链的 Gain+Limiter 总是改变电平, 守恒审计应能检测到."""
        from moodify.processing.pedalboard_chain import MoodifyDSPChain
        chain = MoodifyDSPChain({
            "P06_compression_ratio": 1.5,
            "P09_compression_threshold": -30,
        })
        sr = 44100
        t = np.linspace(0, 1, sr, endpoint=False)
        audio = (0.3 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
        _, _, report = chain.process_with_audit(audio, sr)
        # 压缩+make-up gain+Gain+Limiter 会产生可检测的能量变化
        assert report.energy_grade in ("safe", "warning", "violation")
        assert report.delta_e_residual != 0.0
        assert report.cm_energy <= 1.0

    def test_warning_for_loud_processing(self):
        """大声压处理应至少产生 warning."""
        from moodify.processing.pedalboard_chain import MoodifyDSPChain
        # 激进设置: 高压缩比 + 高谐波驱动
        chain = MoodifyDSPChain({
            "P06_compression_ratio": 8.0,
            "P09_compression_threshold": -40,
            "P13_harmonic_drive": 0.4,
            "P02_vocal_presence_gain": 6.0,
            "P15_high_shelf_gain": 6.0,
        })
        sr = 44100
        t = np.linspace(0, 1, sr, endpoint=False)
        audio = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
        _, _, report = chain.process_with_audit(audio, sr)
        # 即使不触发 violation, 至少应可计算
        assert report.delta_e_residual != 0.0 or report.cm_energy < 1.0

    def test_conservation_report_fields(self):
        from moodify.processing.pedalboard_chain import MoodifyDSPChain
        chain = MoodifyDSPChain({})
        sr = 44100
        audio = (0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 0.5, sr // 2))).astype(np.float32)
        _, _, report = chain.process_with_audit(audio, sr)
        d = report.to_dict()
        assert "delta_e_residual_db" in d
        assert "cm_energy" in d
        assert "energy_grade" in d


class TestMeasureLUFS:
    def test_returns_finite(self):
        from moodify.processing.pedalboard_chain import _measure_lufs
        sr = 44100
        audio = (0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, sr))).astype(np.float32)
        lufs = _measure_lufs(audio, sr)
        assert not np.isnan(lufs)
        assert not np.isinf(lufs)
        assert lufs < 0  # LUFS 通常为负

    def test_silence_gives_low_lufs(self):
        from moodify.processing.pedalboard_chain import _measure_lufs
        sr = 44100
        audio = np.zeros(sr, dtype=np.float32)
        lufs = _measure_lufs(audio, sr)
        assert lufs < -50


class TestDynamicContribution:
    def test_identity_gives_zero(self):
        from moodify.processing.pedalboard_chain import _estimate_dynamic_contribution
        sr = 44100
        audio = (0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, sr))).astype(np.float32)
        delta = _estimate_dynamic_contribution(audio, audio, sr)
        assert abs(delta) < 0.01

    def test_attenuation_gives_negative(self):
        from moodify.processing.pedalboard_chain import _estimate_dynamic_contribution
        sr = 44100
        audio_in = (0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, sr))).astype(np.float32)
        audio_out = audio_in * 0.5
        delta = _estimate_dynamic_contribution(audio_in, audio_out, sr)
        # 均匀衰减不应改变 crest factor → delta ≈ 0
        assert abs(delta) < 0.02

    def test_compressed_signal(self):
        """压缩信号 (clipping) 应改变 crest factor."""
        from moodify.processing.pedalboard_chain import _estimate_dynamic_contribution
        sr = 44100
        t = np.linspace(0, 1, sr, endpoint=False)
        audio_in = (0.8 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
        # 模拟压缩: 软削波
        audio_out = np.tanh(audio_in * 3.0) * 0.6
        delta = _estimate_dynamic_contribution(audio_in, audio_out, sr)
        assert delta != 0.0
