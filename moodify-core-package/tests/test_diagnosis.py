"""Tests for diagnosis subsystem."""
import math
import numpy as np
import pytest


class TestDataTypes:
    def test_wavestate_diagnosis_to_dict(self):
        from moodify.data_types import WaveStateDiagnosis
        ws = WaveStateDiagnosis()
        d = ws.to_dict()
        assert "Spectrum" in d
        assert "Dynamics" in d
        assert "Space" in d
        assert "Layers" in d
        assert "Emotion" in d

    def test_auto_params_complete(self):
        from moodify.data_types import WaveStateDiagnosis
        ws = WaveStateDiagnosis()
        params = ws.get_auto_params()
        assert len(params) == 15  # 14 auto + SP4_as_bool in is_complete

    def test_is_complete_default(self):
        from moodify.data_types import WaveStateDiagnosis
        ws = WaveStateDiagnosis()
        # Default zeros should produce valid params
        auto = ws.get_auto_params()
        bad = [k for k, v in auto.items()
               if v is None or math.isnan(v) or math.isinf(v)]
        assert len(bad) == 0


class TestDiagnosisEngine:
    def test_engine_creates(self):
        from moodify.diagnosis import DiagnosisEngine
        engine = DiagnosisEngine()
        assert engine.sr == 44100
        assert engine.n_fft == 2048

    def test_diagnose_mock_wav(self, mock_wav):
        from moodify.diagnosis import DiagnosisEngine
        engine = DiagnosisEngine()
        ws = engine.diagnose_quick(mock_wav)
        assert ws.is_complete()
        assert 0 <= ws.Spectrum.S3_MidClarity.value <= 1

    def test_extract_spectrum(self, mock_wav):
        from moodify.diagnosis import DiagnosisEngine
        engine = DiagnosisEngine()
        ws = engine.diagnose_quick(mock_wav)
        s = ws.Spectrum
        assert not math.isnan(s.S1_SubPresence.value)
        assert not math.isnan(s.S2_BassWarmth.value)
        assert 0 <= s.S3_MidClarity.value <= 1
        assert not math.isnan(s.S4_AirBand.value)

    def test_extract_dynamics(self, mock_wav):
        from moodify.diagnosis import DiagnosisEngine
        engine = DiagnosisEngine()
        ws = engine.diagnose_quick(mock_wav)
        d = ws.Dynamics
        assert not math.isnan(d.D1_LRA.value)
        assert not math.isnan(d.D4_PLR.value)

    def test_extract_space(self, mock_wav):
        from moodify.diagnosis import DiagnosisEngine
        engine = DiagnosisEngine()
        ws = engine.diagnose_quick(mock_wav)
        sp = ws.Space
        assert -1 <= sp.SP1_Correlation.value <= 1
        assert isinstance(sp.SP4_WidthHealth, bool)


class TestDefectClassifier:
    def test_classify(self, mock_wav):
        from moodify.diagnosis import DiagnosisEngine, DefectClassifier
        engine = DiagnosisEngine()
        ws = engine.diagnose_quick(mock_wav)
        classifier = DefectClassifier()
        defects = classifier.classify(ws)
        assert isinstance(defects, list)
        for d in defects:
            assert 1 <= d.severity <= 3
            assert 1 <= d.priority <= 4

    def test_severity_levels(self):
        from moodify.diagnosis import DefectClassifier
        classifier = DefectClassifier()
        assert classifier._get_severity("S3_MidClarity", 0.2) == 3
        assert classifier._get_severity("S3_MidClarity", 0.8) == 0
        assert classifier._get_severity("D1_LRA", 1.5) == 3


class TestHealthScorer:
    def test_whs(self, mock_wav):
        from moodify.diagnosis import DiagnosisEngine, DefectClassifier, HealthScorer
        engine = DiagnosisEngine()
        ws = engine.diagnose_quick(mock_wav)
        classifier = DefectClassifier()
        defects = classifier.classify(ws)
        scorer = HealthScorer()
        whs = scorer.compute_whs(ws, defects)
        assert 0 <= whs["WHS"] <= 100
        assert "level" in whs

    def test_eds_identity(self, mock_wav):
        from moodify.diagnosis import DiagnosisEngine, HealthScorer
        engine = DiagnosisEngine()
        ws = engine.diagnose_quick(mock_wav)
        scorer = HealthScorer()
        eds = scorer.compute_eds(ws, ws, "温柔觉醒")
        assert eds == 0.0  # identical input


class TestPreprocessor:
    def test_process_mock_wav(self, mock_wav):
        from moodify.diagnosis import Preprocessor
        pp = Preprocessor(target_sr=44100)
        audio = pp.process(mock_wav)
        assert audio.sr == 44100
        assert audio.samples.dtype == np.float32
        assert audio.samples.ndim == 2
