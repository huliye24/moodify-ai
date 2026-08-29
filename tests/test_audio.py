"""Repository-level audio smoke tests backed by generated fixtures."""

from moodify.audio_io import load_audio
from moodify.v01_analyzer import analyze


def test_audio_load_and_basic_analysis(stereo_wav, tmp_path):
    audio, sample_rate = load_audio(str(stereo_wav), always_2d=True)
    metrics = analyze(str(stereo_wav), output_dir=str(tmp_path / "analysis"))

    assert sample_rate == 44_100
    assert audio.shape[1] == 2
    assert metrics.duration_s > 0.0
    assert metrics.channels == 2
    assert "spectrum" in metrics.to_dict()
