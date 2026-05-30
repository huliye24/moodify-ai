"""T1 数据结构升级测试 (SPEC-011 批次 1).

验证 ParameterWithUncertainty 序列化/反序列化,
以及 5 个 Diagnosis dataclass 的新字段.
"""

import json
import pytest
from moodify.data_types import (
    ParameterWithUncertainty,
    SpectrumDiagnosis,
    DynamicsDiagnosis,
    SpaceDiagnosis,
    LayersDiagnosis,
    EmotionDiagnosis,
    WaveStateDiagnosis,
)


class TestParameterWithUncertainty:
    def test_default(self):
        p = ParameterWithUncertainty()
        assert p.value == 0.0
        assert p.uncertainty == 0.0
        assert p.level == "L1"
        assert p.confidence == "medium"
        assert p.is_fallback is False

    def test_to_dict_roundtrip(self):
        p = ParameterWithUncertainty(
            value=4.2, uncertainty=0.15,
            ci_lower=3.9, ci_upper=4.5,
            level="L2", confidence="high",
            provenance="experiment", protocol="pi-1.0",
            is_fallback=False,
        )
        d = p.to_dict()
        p2 = ParameterWithUncertainty.from_dict(d)
        assert p2.value == 4.2
        assert p2.uncertainty == 0.15
        assert p2.ci_lower == 3.9
        assert p2.ci_upper == 4.5
        assert p2.level == "L2"
        assert p2.confidence == "high"
        assert p2.provenance == "experiment"

    def test_fallback_flag(self):
        p = ParameterWithUncertainty(
            value=6.0, uncertainty=0.5,
            confidence="low", is_fallback=True,
            fallback_note="pyloudnorm not available",
        )
        d = p.to_dict()
        assert d["is_fallback"] is True
        assert d["fallback_note"] == "pyloudnorm not available"
        assert d["confidence"] == "low"


class TestSpectrumDiagnosis:
    def test_default_fields(self):
        s = SpectrumDiagnosis()
        assert isinstance(s.S1_SubPresence, ParameterWithUncertainty)
        assert isinstance(s.S3_MidClarity, ParameterWithUncertainty)
        assert s.S3_MidClarity.value == 0.0

    def test_to_dict(self):
        s = SpectrumDiagnosis()
        s.S1_SubPresence = ParameterWithUncertainty(value=-12.0, uncertainty=0.5)
        d = s.to_dict()
        assert d["S1_SubPresence"]["value"] == -12.0
        assert d["S1_SubPresence"]["uncertainty"] == 0.5


class TestDynamicsDiagnosis:
    def test_to_dict(self):
        d = DynamicsDiagnosis()
        d.D1_LRA = ParameterWithUncertainty(value=6.2, uncertainty=0.3)
        result = d.to_dict()
        assert result["D1_LRA"]["value"] == 6.2


class TestSpaceDiagnosis:
    def test_bool_field_preserved(self):
        sp = SpaceDiagnosis()
        assert sp.SP4_WidthHealth is True
        d = sp.to_dict()
        assert d["SP4_WidthHealth"] is True

    def test_param_fields(self):
        sp = SpaceDiagnosis()
        sp.SP1_Correlation = ParameterWithUncertainty(value=0.85, uncertainty=0.02)
        d = sp.to_dict()
        assert d["SP1_Correlation"]["value"] == 0.85


class TestLayersDiagnosis:
    def test_l4_level(self):
        l = LayersDiagnosis()
        assert l.L4_LayerCount.level == "L2"
        assert l.L4_LayerCount.value == 3.0


class TestEmotionDiagnosis:
    def test_e1_e2_level(self):
        e = EmotionDiagnosis()
        assert e.E1_Direction.level == "L2"
        assert e.E2_Richness.level == "L2"
        assert e.E1_Direction.value == 5.0


class TestWaveStateDiagnosis:
    def test_protocol_metadata(self):
        ws = WaveStateDiagnosis()
        assert ws.protocol_mode == "full"
        assert isinstance(ws.stft_config, dict)
        assert isinstance(ws.normalization_notes, list)

    def test_to_dict_includes_metadata(self):
        ws = WaveStateDiagnosis(protocol_mode="quick")
        d = ws.to_dict()
        assert d["protocol_mode"] == "quick"
        assert "stft_config" in d
        assert "normalization_notes" in d

    def test_to_dict_json_serializable(self):
        ws = WaveStateDiagnosis()
        d = ws.to_dict()
        json_str = json.dumps(d, default=str)
        assert len(json_str) > 0

    def test_get_auto_params(self):
        ws = WaveStateDiagnosis()
        ws.Spectrum.S1_SubPresence = ParameterWithUncertainty(value=-10.0)
        ws.Dynamics.D1_LRA = ParameterWithUncertainty(value=8.0)
        params = ws.get_auto_params()
        assert params["S1_SubPresence"] == -10.0
        assert params["D1_LRA"] == 8.0
        assert len(params) == 15
