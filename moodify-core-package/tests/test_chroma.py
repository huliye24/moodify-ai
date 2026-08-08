import numpy as np

from moodify.features.chroma import compute_chroma, detect_key


def _chord(frequencies, sr=22050, duration=2.0):
    t = np.arange(int(sr * duration), dtype=np.float64) / sr
    return sum(np.sin(2.0 * np.pi * frequency * t) for frequency in frequencies) / len(
        frequencies
    )


def test_chroma_active_frames_are_normalized():
    result = compute_chroma(_chord([261.63, 329.63, 392.00]), 22050)
    chroma = result["chroma"]
    active = chroma.sum(axis=0) > 0.0
    assert chroma.shape[0] == 12
    assert np.allclose(chroma[:, active].sum(axis=0), 1.0, atol=1e-6)
    assert 0.0 <= result["harmony_stability"] <= 1.0


def test_c_major_scale_detects_c_major():
    sr = 22050
    phrase = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25,
              392.00, 329.63, 261.63]
    notes = [_chord([frequency], sr=sr, duration=0.35) for frequency in phrase]
    result = compute_chroma(np.concatenate(notes), sr)
    assert result["key"] == "C major"
    assert result["key_strength"] > 0.5


def test_detect_key_rejects_wrong_shape():
    try:
        detect_key(np.ones((11, 2)))
    except ValueError as exc:
        assert "12 pitch-class" in str(exc)
    else:
        raise AssertionError("detect_key should reject non-chroma input")


def test_empty_audio_has_stable_schema():
    result = compute_chroma(np.array([], dtype=np.float32), 22050)
    assert result["chroma"].shape == (12, 0)
    assert result["key"] == "unknown"
    assert result["key_strength"] == 0.0
