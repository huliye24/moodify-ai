"""FFmpegBackend — subprocess-based headless rendering."""
from __future__ import annotations

import json
import shutil
import subprocess
import time
from dataclasses import asdict
from pathlib import Path

from .engine_native import RenderEvidence, _hash_file


def _find_ffmpeg() -> str:
    ff = shutil.which("ffmpeg")
    return ff or "ffmpeg"


def _find_ffprobe() -> str:
    fp = shutil.which("ffprobe")
    return fp or "ffprobe"


def ffmpeg_probe() -> dict:
    exe = _find_ffmpeg()
    exists = shutil.which("ffmpeg") is not None
    return {
        "engine": "ffmpeg",
        "executable": exe,
        "available": exists,
    }


def ffmpeg_render(project, output_dir: Path) -> RenderEvidence:
    """Minimal FFmpeg render: concatenate tracks, apply gain, mix."""
    project.validate()
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence = RenderEvidence(project_id=project.project_id, engine="ffmpeg")
    t_start = time.perf_counter()
    exe = _find_ffmpeg()

    try:
        # Build filter_complex: trim + gain per track, then amix
        inputs = []
        filters = []
        for i, track in enumerate(project.tracks):
            inputs.extend(["-i", track.source.path])
            gain = track.gain_db
            filters.append(f"[{i}:a]volume={gain}dB[a{i}]")

        mix_inputs = "".join(f"[a{i}]" for i in range(len(project.tracks)))
        filters.append(f"{mix_inputs}amix=inputs={len(project.tracks)}:duration=longest[out]")

        filter_str = ";".join(filters)

        out_wav = output_dir / "render.wav"
        cmd = [
            exe, "-y", *inputs,
            "-filter_complex", filter_str,
            "-map", "[out]",
            "-ar", str(project.render.sample_rate),
            "-ac", "2",
            str(out_wav),
        ]
        evidence.command = cmd
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        evidence.exit_code = result.returncode
        if result.returncode != 0:
            evidence.errors.append(f"FFmpeg exit {result.returncode}: {result.stderr[:500]}")
        if out_wav.exists():
            evidence.output_path = str(out_wav)
            evidence.output_hash = _hash_file(out_wav)
    except Exception as exc:
        evidence.exit_code = 1
        evidence.errors.append(str(exc))

    evidence.elapsed_seconds = round(time.perf_counter() - t_start, 3)
    (output_dir / "render_evidence.json").write_text(
        json.dumps(asdict(evidence), indent=2), encoding="utf-8")
    return evidence
