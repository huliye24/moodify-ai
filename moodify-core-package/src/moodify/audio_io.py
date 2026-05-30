"""Universal audio loader — WAV, MP3, FLAC, etc. via soundfile + librosa fallback."""
import numpy as np
import soundfile as sf


def load_audio(path: str, always_2d: bool = True) -> tuple[np.ndarray, int]:
    """Load audio file. Returns (samples, sr). Supports WAV, MP3, FLAC, AIFF, M4A.

    Uses soundfile for native formats (fast), librosa for MP3/compressed formats.
    Always returns float32, shape (samples,) or (samples, channels).
    """
    try:
        data, sr = sf.read(str(path), always_2d=always_2d)
        return data.astype(np.float32), sr
    except Exception:
        pass

    import librosa
    data, sr = librosa.load(str(path), sr=None, mono=False)
    data = data.astype(np.float32)
    if always_2d and data.ndim == 1:
        data = np.column_stack([data, data])
    elif not always_2d and data.ndim > 1:
        data = data.T  # librosa returns (channels, samples) → (samples, channels)
    return data, sr
