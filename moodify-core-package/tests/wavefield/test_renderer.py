"""WaveFieldRenderer — invariants that make a render a trustworthy artifact."""

from __future__ import annotations

import numpy as np
import pytest
import soundfile as sf

from moodify.wavefield.models import FieldSpec
from moodify.wavefield.renderer import (
    ENGINE_VERSION,
    RENDERER_ID,
    SAFE_PEAK_LINEAR,
    WaveFieldRenderError,
    peak_dbfs,
    render_array,
    render_file,
    sha256_file,
)
from moodify.wavefield.search import probe_fields


def a_field() -> FieldSpec:
    return FieldSpec(
        field_id="field_A",
        parameters={"room_size": 0.5, "damping": 0.5, "wet": 0.16, "width": 0.86},
    )


# ---------------------------------------------------------------------------
# File-level contract
# ---------------------------------------------------------------------------


def test_render_preserves_sample_rate_duration_and_channels(source_wav, tmp_path):
    output = tmp_path / "out" / "A.wav"
    result = render_file(source_wav, a_field(), output)

    src_info = sf.info(str(source_wav))
    dst_info = sf.info(str(output))

    assert dst_info.samplerate == src_info.samplerate == result.sample_rate
    assert dst_info.channels == src_info.channels == result.channels == 2
    assert abs(result.duration_seconds - src_info.duration) < 0.001
    assert result.frames == int(dst_info.frames)


def test_mono_stays_mono(mono_wav, tmp_path):
    output = tmp_path / "mono_out.wav"
    result = render_file(mono_wav, a_field(), output)
    assert result.channels == 1
    assert sf.info(str(output)).channels == 1


def test_output_is_finite_and_the_source_is_untouched(source_wav, tmp_path):
    before_bytes = source_wav.read_bytes()
    before_sha = sha256_file(source_wav)

    result = render_file(source_wav, a_field(), tmp_path / "A.wav")

    assert source_wav.read_bytes() == before_bytes, "the source file was rewritten"
    assert sha256_file(source_wav) == before_sha
    assert result.source_sha256 == before_sha

    rendered, sr = sf.read(str(result.output_path), always_2d=False)
    assert np.all(np.isfinite(rendered))
    assert sr == result.sample_rate


def test_output_is_a_wav_file(source_wav, tmp_path):
    output = tmp_path / "A.wav"
    render_file(source_wav, a_field(), output)
    assert sf.info(str(output)).format == "WAV"
    assert output.suffix.lower() == ".wav"


def test_refuses_to_render_over_the_source(source_wav):
    with pytest.raises(WaveFieldRenderError) as excinfo:
        render_file(source_wav, a_field(), source_wav)
    assert excinfo.value.code == "OUTPUT_IS_SOURCE"


def test_missing_source_is_reported(tmp_path):
    with pytest.raises(WaveFieldRenderError) as excinfo:
        render_file(tmp_path / "nope.wav", a_field(), tmp_path / "A.wav")
    assert excinfo.value.code == "SOURCE_NOT_FOUND"


# ---------------------------------------------------------------------------
# The record
# ---------------------------------------------------------------------------


def test_render_record_carries_the_hashes_the_field_and_the_version(source_wav, tmp_path):
    field = a_field()
    result = render_file(source_wav, field, tmp_path / "A.wav")
    document = result.to_dict()

    assert document["schema"] == "moodify.wavefield.render/0.1"
    assert document["renderer"] == RENDERER_ID
    assert document["engine_version"] == ENGINE_VERSION
    assert document["field"] == field.to_dict()
    assert document["field_hash"] == field.field_hash()
    assert document["source_sha256"] == sha256_file(source_wav)
    assert document["output_sha256"] == sha256_file(tmp_path / "A.wav")
    assert document["engine_calibration"]["dry_unity"] == 0.5
    assert document["engine_library"]["name"] == "pedalboard"


def test_rendering_is_deterministic(source_wav, tmp_path):
    first = render_file(source_wav, a_field(), tmp_path / "one.wav")
    second = render_file(source_wav, a_field(), tmp_path / "two.wav")
    assert first.output_sha256 == second.output_sha256
    assert (tmp_path / "one.wav").read_bytes() == (tmp_path / "two.wav").read_bytes()


def test_a_different_field_gives_a_different_render(source_wav, tmp_path):
    small = probe_fields()[0]
    large = probe_fields()[2]
    first = render_file(source_wav, small, tmp_path / "small.wav")
    second = render_file(source_wav, large, tmp_path / "large.wav")
    assert first.output_sha256 != second.output_sha256


def test_safety_gain_is_recorded_and_never_clips(tmp_path):
    """A near-full-scale source must be attenuated, not clipped."""
    sr = 48000
    t = np.arange(sr * 3) / sr
    loud = np.stack([0.99 * np.sin(2 * np.pi * 200 * t), 0.99 * np.sin(2 * np.pi * 300 * t)], axis=1)
    source = tmp_path / "loud.wav"
    sf.write(str(source), loud.astype(np.float32), sr, subtype="FLOAT")

    result = render_file(source, probe_fields()[2], tmp_path / "loud_out.wav")

    rendered, _ = sf.read(str(result.output_path), always_2d=False)
    assert np.all(np.isfinite(rendered))
    assert float(np.max(np.abs(rendered))) <= SAFE_PEAK_LINEAR + 1e-6
    assert result.peak_dbfs_after_safety <= -0.09
    assert result.safety_gain_db == 0.0 or result.safety_gain_db < 0.0
    assert result.safety_gain_applied == (result.safety_gain_db != 0.0)


def test_no_safety_gain_is_applied_when_there_is_headroom(source_wav, tmp_path):
    result = render_file(source_wav, probe_fields()[0], tmp_path / "A.wav")
    assert result.safety_gain_applied is False
    assert result.safety_gain_db == 0.0


def test_dry_path_is_unity_so_a_field_does_not_inflate_level(source_wav, tmp_path):
    """Regression guard for the pedalboard dry-level convention.

    ``pedalboard.Reverb`` treats ``dry_level = 1.0`` as +6 dB.  If the renderer
    passed ``1 - wet`` straight through, every candidate would arrive several
    LU louder than the source and the search would be measuring a library gain
    rather than a field.
    """
    source, sr = sf.read(str(source_wav), always_2d=False)
    rendered, _ = render_array(np.asarray(source), sr, a_field())
    delta_db = peak_dbfs(rendered) - peak_dbfs(np.asarray(source))
    assert delta_db < 0.0, f"the field render must not raise the level (got {delta_db:+.2f} dB)"
    assert delta_db > -6.0, f"unexpected large attenuation ({delta_db:+.2f} dB)"


# ---------------------------------------------------------------------------
# Array-level guards
# ---------------------------------------------------------------------------


def test_non_finite_input_is_rejected():
    bad = np.array([0.1, np.nan, 0.2], dtype=np.float32)
    with pytest.raises(WaveFieldRenderError) as excinfo:
        render_array(bad, 48000, a_field())
    assert excinfo.value.code == "NON_FINITE_INPUT"


def test_bad_shape_and_sample_rate_are_rejected():
    with pytest.raises(WaveFieldRenderError) as shape:
        render_array(np.zeros((2, 3, 4), dtype=np.float32), 48000, a_field())
    assert shape.value.code == "UNSUPPORTED_SHAPE"

    with pytest.raises(WaveFieldRenderError) as rate:
        render_array(np.zeros(10, dtype=np.float32), 0, a_field())
    assert rate.value.code == "BAD_SAMPLE_RATE"


def test_render_array_keeps_the_input_shape():
    mono = np.zeros(4096, dtype=np.float32)
    stereo = np.zeros((4096, 2), dtype=np.float32)
    assert render_array(mono, 48000, a_field())[0].shape == (4096,)
    assert render_array(stereo, 48000, a_field())[0].shape == (4096, 2)
