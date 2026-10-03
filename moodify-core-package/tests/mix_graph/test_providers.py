"""Provider unit tests: behavior, defaults, and rejection rules."""

import numpy as np
import pytest

from moodify.mix_graph.providers import get_provider
from moodify.mix_graph.providers.base import ProviderError
from moodify.mix_graph.providers.pedalboard_providers import (
    CompressorProvider,
    EQProvider,
    LimiterProvider,
    StereoProvider,
)
from tests.mix_graph.conftest import band_rms_db

pytestmark = [pytest.mark.v01]


@pytest.fixture
def audio_and_sr():
    sr = 44100
    t = np.arange(sr * 2) / sr
    left = 0.35 * np.sin(2 * np.pi * 440 * t) + 0.05 * np.sin(2 * np.pi * 12000 * t)
    right = 0.30 * np.sin(2 * np.pi * 554 * t) + 0.05 * np.sin(2 * np.pi * 12000 * t)
    return np.column_stack([left, right]).astype(np.float32), sr


class TestEQ:
    def test_highshelf_raises_air_band(self, audio_and_sr):
        audio, sr = audio_and_sr
        provider = EQProvider()
        out = provider.render(audio, sr, {"bands": [
            {"type": "highshelf", "freq_hz": 10000.0, "gain_db": 6.0}]})
        before = band_rms_db(audio, sr, 10000, 16000)
        after = band_rms_db(out, sr, 10000, 16000)
        assert after > before + 3.0
        assert audio.shape == out.shape

    def test_partial_parameters_rejected(self):
        with pytest.raises(ProviderError, match="bands"):
            EQProvider().validate_parameters({})
        with pytest.raises(ProviderError, match="type"):
            EQProvider().validate_parameters({"bands": [{"freq_hz": 1000}]})
        with pytest.raises(ProviderError, match="freq_hz"):
            EQProvider().validate_parameters({"bands": [
                {"type": "peak", "freq_hz": 1.0, "gain_db": 1.0}]})
        too_many = [{"type": "peak", "freq_hz": 1000.0, "gain_db": 0.1}] * 9
        with pytest.raises(ProviderError, match="1..8"):
            EQProvider().validate_parameters({"bands": too_many})

    def test_default_q_applied(self):
        params = EQProvider().validate_parameters({"bands": [
            {"type": "peak", "freq_hz": 3000.0, "gain_db": 2.0}]})
        assert params["bands"][0]["q"] == 0.7


class TestCompressor:
    def test_reduces_crest_factor(self, audio_and_sr):
        audio, sr = audio_and_sr
        envelope = 0.5 + 0.5 * np.sin(2 * np.pi * 1.5 * np.arange(audio.shape[0]) / sr)
        audio = (audio * envelope[:, None]).astype(np.float32)
        out = CompressorProvider().render(
            audio, sr, {"threshold_db": -18.0, "ratio": 4.0,
                        "attack_ms": 5.0, "release_ms": 100.0})
        crest_in = np.max(np.abs(audio)) / np.sqrt(np.mean(audio ** 2))
        crest_out = np.max(np.abs(out)) / np.sqrt(np.mean(out ** 2))
        assert crest_out < crest_in

    def test_defaults_and_range_rejection(self):
        params = CompressorProvider().validate_parameters({})
        assert params == {"threshold_db": -12.0, "ratio": 1.2,
                          "attack_ms": 25.0, "release_ms": 250.0}
        with pytest.raises(ProviderError, match="ratio"):
            CompressorProvider().validate_parameters({"ratio": 100.0})


class TestStereo:
    def test_width_two_increases_side_energy(self, audio_and_sr):
        audio, sr = audio_and_sr
        out = StereoProvider().render(audio, sr, {"width": 2.0})
        side_in = np.std(audio[:, 0] - audio[:, 1])
        side_out = np.std(out[:, 0] - out[:, 1])
        assert side_out > side_in * 1.5

    def test_width_one_is_bitwise_identity(self, audio_and_sr):
        audio, sr = audio_and_sr
        out = StereoProvider().render(audio, sr, {"width": 1.0})
        assert np.array_equal(out, audio)

    def test_width_zero_collapses_to_mono_sum(self, audio_and_sr):
        audio, sr = audio_and_sr
        out = StereoProvider().render(audio, sr, {"width": 0.0})
        assert np.allclose(out[:, 0], out[:, 1])

    def test_mono_input_passthrough(self):
        sr = 44100
        mono = (0.3 * np.sin(2 * np.pi * 440 * np.arange(sr) / sr)).astype(np.float32)
        assert np.array_equal(StereoProvider().render(mono, sr, {"width": 2.0}), mono)


class TestLimiter:
    def test_caps_peak_at_ceiling(self, audio_and_sr):
        audio, sr = audio_and_sr
        audio = (audio * 2.5).astype(np.float32)  # push well past -1 dBFS
        out = LimiterProvider().render(audio, sr, {"ceiling_db": -1.0})
        peak_db = 20 * np.log10(np.max(np.abs(out)))
        assert peak_db <= -1.0 + 0.01

    def test_partial_parameters_use_defaults(self, audio_and_sr):
        audio, sr = audio_and_sr
        out = LimiterProvider().render(audio, sr, {"ceiling_db": -1.0})
        assert out.shape == audio.shape  # input_gain_db default applied

    def test_input_gain_and_unknown_key(self, audio_and_sr):
        audio, sr = audio_and_sr
        out = LimiterProvider().render(audio, sr, {"ceiling_db": -1.0, "input_gain_db": 12.0})
        ceiling_amplitude = 10 ** (-1.0 / 20)  # -1 dBFS
        peak = float(np.max(np.abs(out)))
        assert abs(peak - ceiling_amplitude) <= 0.02  # hard-clipped at the ceiling
        with pytest.raises(ProviderError, match="unknown keys"):
            LimiterProvider().validate_parameters({"makeup": 1.0})


def test_registry_rejects_unknown_type():
    with pytest.raises(ProviderError, match="unknown node type"):
        get_provider("reverb")


def test_describe_is_deterministic():
    provider = LimiterProvider()
    a = provider.describe({"ceiling_db": -1.0})
    b = provider.describe({"ceiling_db": -1.0})
    assert a == b
    assert a["node_type"] == "limiter"
