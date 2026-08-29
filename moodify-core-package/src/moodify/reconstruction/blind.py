"""Blind listening kit (MFY-CR-P06 §10-§13).

Randomized X1-X4 labels, level-matched listening copies, mapping hidden until
finalize. Listening copies are NOT canonical candidates — the originals are
always preserved and level matching never alters them.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.auditory.loudness import integrated_loudness_lufs

_BLIND_VERSION = "blind-kit-v0.1"


@dataclass
class BlindKit:
    listening_dir: Path
    mapping: dict[str, str]            # X1..X4 -> candidate_id
    level_target_lufs: float
    level_method: str = "linear-gain-to-source-lufs"
    finalized: bool = False

    def to_dict(self) -> dict[str, str | float | bool]:
        return {
            "version": _BLIND_VERSION,
            "listening_dir": str(self.listening_dir),
            "mapping": dict(self.mapping),
            "level_target_lufs": self.level_target_lufs,
            "level_method": self.level_method,
            "finalized": self.finalized,
        }


def level_match(candidate_wav: Path, target_lufs: float) -> np.ndarray:
    """Return the level-matched audio (linear gain to target LUFS)."""
    audio, sr = sf.read(str(candidate_wav), dtype="float32")
    lufs = integrated_loudness_lufs(audio, sr)
    if lufs is None or not np.isfinite(lufs):
        gain = 1.0
    else:
        gain = float(10 ** ((target_lufs - lufs) / 20.0))
    return audio * gain


def make_blind_kit(
    source_wav: Path,
    candidate_wavs: dict[str, Path],
    out_dir: Path,
    *,
    seed: int = 20260817,
) -> BlindKit:
    """Build X1..X4 listening copies (SOURCE + A/B/C) with hidden mapping."""
    out_dir = Path(out_dir)
    listening = out_dir / "listening"
    listening.mkdir(parents=True, exist_ok=True)

    source_lufs = integrated_loudness_lufs(*_read(source_wav))
    if source_lufs is None:
        source_lufs = -14.0

    entries = [("SOURCE", source_wav)] + [(k, v) for k, v in candidate_wavs.items()]
    rng = random.Random(seed)
    labels = [f"X{i}" for i in range(1, len(entries) + 1)]
    rng.shuffle(labels)
    mapping: dict[str, str] = {}

    for (candidate_id, wav), label in zip(entries, labels):
        audio = level_match(wav, source_lufs)
        out = listening / f"{label}.wav"
        sf.write(str(out), audio, 48000, subtype="PCM_16")
        mapping[label] = candidate_id

    kit = BlindKit(listening_dir=listening, mapping=mapping, level_target_lufs=source_lufs)
    (out_dir / "blind_mapping.json").write_text(
        json.dumps(kit.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return kit


def _read(path: Path) -> tuple[np.ndarray, int]:
    audio, sr = sf.read(str(path), dtype="float32")
    if audio.ndim == 1:
        audio = audio[:, None]
    return audio, int(sr)


def finalize_blind_mapping(out_dir: Path, scores: dict[str, dict]) -> dict:
    """Record listening scores and mark the mapping finalized (unlocked)."""
    kit_path = Path(out_dir) / "blind_mapping.json"
    payload = json.loads(kit_path.read_text(encoding="utf-8"))
    payload["finalized"] = True
    payload["scores"] = scores
    kit_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload
