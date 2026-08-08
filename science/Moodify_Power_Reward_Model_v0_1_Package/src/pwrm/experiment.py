from __future__ import annotations

import csv
import hashlib
import json
import random
from pathlib import Path
from typing import Any

import numpy as np

from .audio import measure_array, match_loudness, read_audio, sha256_file, write_audio


def _opaque_id(experiment_id: str, filename: str) -> str:
    digest = hashlib.sha256(f"{experiment_id}|{filename}".encode()).hexdigest()[:10]
    return f"S-{digest.upper()}"


def _excerpt_starts(reference: np.ndarray, sample_rate: int, seconds: int = 30) -> dict[str, int]:
    mono = np.mean(reference, axis=1)
    block = sample_rate
    usable = len(mono) // block
    energy = np.asarray(
        [np.mean(np.square(mono[i * block : (i + 1) * block])) for i in range(usable)]
    )
    width = seconds
    if usable < width + 4:
        raise ValueError("audio is too short for two 30-second excerpts")
    rolling = np.convolve(energy, np.ones(width), mode="valid")
    margin = min(5, max(0, len(rolling) // 10))
    search = rolling[margin : len(rolling) - margin or None]
    mid = int(np.argmax(search) + margin)
    smooth = np.convolve(energy, np.ones(5) / 5, mode="same")
    rise = smooth[5:] - smooth[:-5]
    candidates = np.argsort(rise)[::-1]
    contrast = next(
        int(max(0, min(int(index) - width // 3, usable - width)))
        for index in candidates
        if abs(int(index) - mid) >= width
    )
    return {"mid": mid * sample_rate, "contrast": contrast * sample_rate}


def prepare_pilot(
    input_dir: Path,
    output_dir: Path,
    *,
    experiment_id: str = "PWRM-EXP-001",
    seed: int = 20260724,
    listener_count: int = 12,
) -> dict[str, Any]:
    files = sorted(input_dir.glob("*.wav"))
    originals = [path for path in files if "original" in path.stem.lower()]
    if len(originals) != 1 or len(files) < 2:
        raise ValueError("expected exactly one original WAV and at least one candidate WAV")
    original_path = originals[0]
    original, sample_rate = read_audio(original_path)
    reference_metrics = measure_array(original, sample_rate)
    starts = _excerpt_starts(original, sample_rate)
    excerpt_frames = sample_rate * 30

    stimuli_dir = output_dir / "02_stimuli" / "blind"
    manifest: dict[str, Any] = {
        "experiment_id": experiment_id,
        "seed": seed,
        "input_dir": str(input_dir),
        "reference_file": original_path.name,
        "excerpt_starts_seconds": {
            name: frame / sample_rate for name, frame in starts.items()
        },
        "stimuli": [],
    }
    id_by_file: dict[str, str] = {}

    for path in files:
        audio, rate = read_audio(path)
        if rate != sample_rate or audio.shape != original.shape:
            raise ValueError(f"format or duration mismatch: {path.name}")
        matched, gain_db = (
            (audio, 0.0) if path == original_path else match_loudness(original, audio, rate)
        )
        metrics = measure_array(matched, rate)
        if abs(metrics.lufs_i - reference_metrics.lufs_i) > 0.10:
            raise ValueError(f"loudness gate failed: {path.name}")
        if metrics.true_peak_dbTP > -1.0:
            raise ValueError(f"true-peak gate failed after matching: {path.name}")
        stimulus_id = _opaque_id(experiment_id, path.name)
        id_by_file[path.name] = stimulus_id
        entry = {
            "stimulus_id": stimulus_id,
            "source_filename": path.name,
            "source_sha256": sha256_file(path),
            "is_original": path == original_path,
            "loudness_match_gain_db": gain_db,
            "metrics": metrics.to_dict(),
            "clips": {},
        }
        for excerpt, start in starts.items():
            clip = matched[start : start + excerpt_frames]
            clip_path = stimuli_dir / f"{stimulus_id}_{excerpt}.wav"
            write_audio(clip_path, clip, rate)
            entry["clips"][excerpt] = {
                "path": str(clip_path),
                "sha256": sha256_file(clip_path),
            }
        manifest["stimuli"].append(entry)

    original_id = id_by_file[original_path.name]
    candidate_ids = sorted(value for value in id_by_file.values() if value != original_id)
    rng = random.Random(seed)
    schedule_rows: list[dict[str, Any]] = []
    for listener_number in range(1, listener_count + 1):
        trials: list[tuple[str, str, str, str]] = []
        for candidate in candidate_ids:
            for excerpt in ("mid", "contrast"):
                trials.append(("screen", original_id, candidate, excerpt))
        repeat_base = rng.sample(trials, 2)
        trials.extend(("repeat", a, b, excerpt) for _, a, b, excerpt in repeat_base)
        null_stimulus = rng.choice([original_id, *candidate_ids])
        trials.append(("null", null_stimulus, null_stimulus, rng.choice(["mid", "contrast"])))
        rng.shuffle(trials)
        for trial_number, (trial_type, left, right, excerpt) in enumerate(trials, start=1):
            swap = rng.random() < 0.5
            a_id, b_id = (right, left) if swap else (left, right)
            schedule_rows.append(
                {
                    "listener_id": f"L{listener_number:03d}",
                    "trial_number": trial_number,
                    "trial_type": trial_type,
                    "excerpt": excerpt,
                    "stimulus_a": a_id,
                    "stimulus_b": b_id,
                    "file_a": f"{a_id}_{excerpt}.wav",
                    "file_b": f"{b_id}_{excerpt}.wav",
                    "preference": "",
                    "confidence": "",
                    "reason_code": "",
                    "comment": "",
                }
            )

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "02_stimuli" / "stimulus_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    schedule_path = output_dir / "03_listening" / "trial_schedule.csv"
    schedule_path.parent.mkdir(parents=True, exist_ok=True)
    with schedule_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(schedule_rows[0]))
        writer.writeheader()
        writer.writerows(schedule_rows)

    private_key = {
        "warning": "JUDGE-ONLY: do not expose during listening",
        "stimulus_identity": id_by_file,
    }
    (output_dir / "02_stimuli" / "PRIVATE_identity_key.json").write_text(
        json.dumps(private_key, ensure_ascii=False, indent=2) + "\n"
    )
    return {
        "stimulus_count": len(files),
        "clip_count": len(files) * 2,
        "listener_count": listener_count,
        "trial_count": len(schedule_rows),
        "manifest": str(manifest_path),
        "schedule": str(schedule_path),
    }
