from pathlib import Path
import math
import struct
import wave

from moodify_runtime.metrics import analyze_audio


def test_analyze_wav(tmp_path: Path):
    p = tmp_path / "a.wav"
    sr = 8000
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        data = bytearray()
        for i in range(sr):
            val = int(0.1 * math.sin(2 * math.pi * 440 * i / sr) * 32767)
            data += struct.pack("<h", val)
        wf.writeframes(bytes(data))

    m = analyze_audio(p)
    assert m["supported"] is True
    assert abs(m["duration_seconds"] - 1.0) < 1e-6
    assert m["pseudo_mrs_v001"] is not None
