#!/usr/bin/env python3
from __future__ import annotations

import math
import struct
import wave
from pathlib import Path


def generate_sine(path: Path, seconds: float = 3.0, sr: int = 44100, freq: float = 440.0):
    path.parent.mkdir(parents=True, exist_ok=True)
    n = int(seconds * sr)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        frames = bytearray()
        for i in range(n):
            t = i / sr
            # 简单包络，避免爆音
            env = min(1.0, i / (0.05 * sr), (n - i) / (0.05 * sr))
            val = int(0.15 * env * math.sin(2 * math.pi * freq * t) * 32767)
            frames += struct.pack("<hh", val, val)
        wf.writeframes(bytes(frames))


if __name__ == "__main__":
    generate_sine(Path("data/night_inputs/test_sine_440.wav"))
    print("generated data/night_inputs/test_sine_440.wav")
