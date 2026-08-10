"""Deterministic reference audio suite generator (Gate 2).

Each fixture is generated with fixed parameters and a fixed RNG seed, so the
suite is reproducible bit-for-bit. Run:

    python benchmarks/reference_audio/generate_reference_suite.py

Outputs: fixtures/*.wav + REFERENCE_SUITE_MANIFEST.json (sha256 + params).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 48000
OUT = Path(__file__).parent / "fixtures"
SEED = 20260811


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name: str, samples: np.ndarray, sr: int = SR) -> None:
    path = OUT / name
    sf.write(path, samples.astype(np.float32), sr)
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    manifest = {"suite": "MFY-REFERENCE-AUDIO-SUITE-001", "seed": SEED, "sample_rate": SR,
                "fixtures": {}}

    t2 = np.arange(SR * 2) / SR  # 2 s
    t4 = np.arange(SR * 4) / SR  # 4 s

    # silence — all zeros
    silence = np.zeros(SR * 2)
    name = "silence.wav"
    write(name, silence)
    manifest["fixtures"][name] = {"purpose": "floor", "params": {"duration_s": 2.0}}

    # sine 1 kHz at -6 dBFS
    sine = 0.5 * np.sin(2 * np.pi * 1000 * t2)
    name = "sine_1khz.wav"
    write(name, sine)
    manifest["fixtures"][name] = {"purpose": "tone reference", "params": {"freq_hz": 1000, "amp": 0.5}}

    # dual tone 440 + 3000 Hz
    dual = 0.4 * np.sin(2 * np.pi * 440 * t2) + 0.2 * np.sin(2 * np.pi * 3000 * t2)
    name = "dual_tone.wav"
    write(name, dual)
    manifest["fixtures"][name] = {"purpose": "band separation", "params": {"freqs_hz": [440, 3000]}}

    # impulse — single sample
    impulse = np.zeros(SR * 2)
    impulse[0] = 1.0
    name = "impulse.wav"
    write(name, impulse)
    manifest["fixtures"][name] = {"purpose": "impulse response / peak", "params": {}}

    # clipped — sine pushed past 0 dBFS then hard-limited
    clipped = np.clip(1.2 * np.sin(2 * np.pi * 500 * t2), -1.0, 1.0)
    name = "clipped.wav"
    write(name, clipped)
    manifest["fixtures"][name] = {"purpose": "clipping detection", "params": {"over_drives_by": 1.2}}

    # mono — single channel
    mono = 0.3 * np.sin(2 * np.pi * 440 * t2)
    name = "mono.wav"
    write(name, mono)
    manifest["fixtures"][name] = {"purpose": "channel layout", "params": {"channels": 1}}

    # stereo correlated — same program both channels
    corr = 0.3 * np.sin(2 * np.pi * 440 * t2)
    name = "stereo_correlated.wav"
    write(name, np.stack([corr, corr], axis=1))
    manifest["fixtures"][name] = {"purpose": "phase integrity", "params": {"correlation": 1.0}}

    # stereo phase inverted — right channel anti-correlated
    inv = 0.3 * np.sin(2 * np.pi * 440 * t2)
    name = "stereo_phase_inverted.wav"
    write(name, np.stack([inv, -inv], axis=1))
    manifest["fixtures"][name] = {"purpose": "phase risk", "params": {"correlation": -1.0}}

    # pink noise — Voss-McCartney via RNG (deterministic seed)
    pink = np.zeros(SR * 2)
    for _ in range(8):
        pink += rng.standard_normal(SR * 2)
    pink = pink / np.max(np.abs(pink)) * 0.5
    name = "pink_noise.wav"
    write(name, pink)
    manifest["fixtures"][name] = {"purpose": "flat spectrum reference", "params": {"octaves": 8}}

    # dynamic program — loudness envelope ramps for LUFS/LRA
    env = np.linspace(0.05, 1.0, SR * 4) * np.sin(2 * np.pi * 220 * t4)
    env = env * np.abs(np.sin(2 * np.pi * 0.5 * t4) + 0.3)  # slow amplitude modulation
    name = "dynamic_program.wav"
    write(name, env)
    manifest["fixtures"][name] = {"purpose": "loudness range", "params": {"duration_s": 4.0}}

    for name in manifest["fixtures"]:
        manifest["fixtures"][name]["sha256"] = sha256_file(OUT / name)

    (Path(__file__).parent / "REFERENCE_SUITE_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"generated {len(manifest['fixtures'])} fixtures in {OUT}")


if __name__ == "__main__":
    main()
