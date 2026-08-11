"""T3 静默回退验证测试 (SPEC-011 批次 3).

验证 engine.py 和 metrics.py 的回退标记是否正确:
  - pyloudnorm 不可用时 D1_LRA/D2/D3/D4 标记为 fallback
  - quick mode D2/D3/SP3 标记为 fallback
  - mono 音频 L1_VocalSNR 标记为 fallback
"""

import numpy as np


class TestFallbackMarking:
    """验证 ParameterWithUncertainty.is_fallback 在各种场景下的正确性."""

    def test_quick_mode_marks_d2_d3_fallback(self, mock_wav):
        """快速模式: D2/D3 使用简化算法, 应标记为 fallback."""
        from moodify.diagnosis import DiagnosisEngine
        engine = DiagnosisEngine()
        ws = engine.diagnose_quick(mock_wav)

        # D2/D3 在 quick mode 应标记为 fallback
        assert ws.Dynamics.D2_ChorusImpact.is_fallback is True, \
            f"D2 should be fallback in quick mode, got {ws.Dynamics.D2_ChorusImpact.fallback_note}"
        assert ws.Dynamics.D3_MicroDynamics.is_fallback is True, \
            f"D3 should be fallback in quick mode, got {ws.Dynamics.D3_MicroDynamics.fallback_note}"

    def test_quick_mode_sp3_hardcoded_fallback(self, mock_wav):
        """快速模式: SP3 硬编码 0.3, 应标记为 fallback."""
        from moodify.diagnosis import DiagnosisEngine
        engine = DiagnosisEngine()
        ws = engine.diagnose_quick(mock_wav)
        assert ws.Space.SP3_RT60Consist.is_fallback is True
        assert "quick mode" in ws.Space.SP3_RT60Consist.fallback_note.lower()

    def test_e1_e2_default_fallback(self, mock_wav):
        """E1/E2 未提供主观评分时使用默认值 5, 应标记为 fallback."""
        from moodify.diagnosis import DiagnosisEngine
        engine = DiagnosisEngine()
        ws = engine.diagnose(mock_wav, subjective={}, mode="quick")
        assert ws.Emotion.E1_Direction.is_fallback is True
        assert ws.Emotion.E2_Richness.is_fallback is True

    def test_e1_e2_no_fallback_when_provided(self, mock_wav):
        """E1/E2 提供了主观评分时不应标记为 fallback."""
        from moodify.diagnosis import DiagnosisEngine
        engine = DiagnosisEngine()
        ws = engine.diagnose(mock_wav, subjective={"E1": 7, "E2": 6}, mode="quick")
        assert ws.Emotion.E1_Direction.is_fallback is False
        assert ws.Emotion.E2_Richness.is_fallback is False

    def test_mono_audio_l1_fallback(self):
        """单声道音频 L1_VocalSNR 应标记为 fallback."""
        from moodify.diagnosis import DiagnosisEngine
        import soundfile as sf
        import tempfile
        import os

        engine = DiagnosisEngine()
        # Generate mono sine
        sr = 44100
        mono = (0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 2, sr * 2))).astype(np.float32)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            sf.write(f.name, mono, sr)
            tmp = f.name

        try:
            ws = engine.diagnose_quick(tmp)
            assert ws.Layers.L1_VocalSNR.is_fallback is True
            assert "mono" in ws.Layers.L1_VocalSNR.fallback_note.lower()
        finally:
            os.unlink(tmp)

    def test_fallback_confidence_level(self, mock_wav):
        """回退参数的 confidence 应为 'low'."""
        from moodify.diagnosis import DiagnosisEngine
        engine = DiagnosisEngine()
        ws = engine.diagnose_quick(mock_wav)

        fb_params = [
            ws.Dynamics.D2_ChorusImpact,
            ws.Dynamics.D3_MicroDynamics,
            ws.Space.SP3_RT60Consist,
        ]
        for p in fb_params:
            assert p.confidence == "low", \
                f"fallback param should have confidence='low', got '{p.confidence}'"

    def test_no_unpopped_fallbacks(self, mock_wav, capsys):
        """诊断完成后不应有未消耗的回退标记."""
        from moodify.diagnosis import DiagnosisEngine
        engine = DiagnosisEngine()
        engine.diagnose_quick(mock_wav)
        captured = capsys.readouterr()
        assert "unpopped fallback" not in captured.out.lower()


class TestFallbackContent:
    """验证回退注释包含有用信息."""

    def test_notes_are_descriptive(self, mock_wav):
        from moodify.diagnosis import DiagnosisEngine
        engine = DiagnosisEngine()
        ws = engine.diagnose_quick(mock_wav)

        # D2 fallback note 应说明使用了什么替代算法
        assert len(ws.Dynamics.D2_ChorusImpact.fallback_note) > 10
        # SP3 fallback note 应提到 quick mode
        assert "quick" in ws.Space.SP3_RT60Consist.fallback_note.lower()
