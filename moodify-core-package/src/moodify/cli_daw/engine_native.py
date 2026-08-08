"""NativeDSPBackend — reuses moodify.processing.* for EQ/compressor/limiter/gain/fade."""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import soundfile as sf

from .project import CLIDAWProject


@dataclass
class RenderEvidence:
    project_id: str = ""
    engine: str = "native"
    command: list[str] = field(default_factory=list)
    exit_code: int = -1
    output_path: str = ""
    output_hash: str = ""
    output_duration_s: float = 0.0
    output_sample_rate: int = 0
    output_channels: int = 0
    output_peak_db: float = 0.0
    elapsed_seconds: float = 0.0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _hash_file(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_audio(path: str, sr: int) -> np.ndarray:
    y, orig_sr = sf.read(path, dtype="float64")
    if y.ndim == 1:
        y = np.column_stack([y, y])
    if y.shape[1] == 1:
        y = np.column_stack([y[:, 0], y[:, 0]])
    # Resample if needed
    if orig_sr != sr and len(y) > 0:
        from scipy.signal import resample
        new_len = int(len(y) * sr / orig_sr)
        y = resample(y, new_len)
    return y


def native_render(project: CLIDAWProject, output_dir: Path) -> RenderEvidence:
    """Render a CLIDAWProject using NativeDSP."""

    project.validate()
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence = RenderEvidence(project_id=project.project_id)
    t_start = time.perf_counter()

    try:
        sr = project.sample_rate
        track_audio: dict[str, np.ndarray] = {}

        for track in project.tracks:
            y = _load_audio(track.source.path, sr)
            nodes = project.processing.get(track.track_id, [])

            for node in sorted(nodes, key=lambda n: n.order):
                y = _apply_processing(y, sr, node)

            # Apply track-level gain
            y = y * (10.0 ** (track.gain_db / 20.0))
            track_audio[track.track_id] = y

        # Mix tracks (simple sum)
        if not track_audio:
            raise RuntimeError("No tracks to mix")

        max_len = max(y.shape[0] for y in track_audio.values())
        mixed = np.zeros((max_len, 2), dtype=np.float64)
        n_tracks = len(track_audio)
        for y in track_audio.values():
            if y.shape[0] < max_len:
                y = np.pad(y, ((0, max_len - y.shape[0]), (0, 0)))
            mixed += y / n_tracks

        # Master processing
        for node in sorted(project.master.processing, key=lambda n: n.order):
            mixed = _apply_processing(mixed, sr, node)

        # Write
        out_wav = output_dir / "render.wav"
        sf.write(str(out_wav), mixed, sr, subtype=f"PCM_{project.render.bit_depth}")
        evidence.output_path = str(out_wav)
        evidence.output_hash = _hash_file(out_wav)
        info = sf.info(str(out_wav))
        evidence.output_duration_s = round(info.duration, 3)
        evidence.output_sample_rate = info.samplerate
        evidence.output_channels = info.channels
        peak = float(np.max(np.abs(mixed)))
        evidence.output_peak_db = round(20.0 * np.log10(max(peak, 1e-12)), 2)
        evidence.exit_code = 0
    except Exception as exc:
        evidence.exit_code = 1
        evidence.errors.append(str(exc))

    evidence.elapsed_seconds = round(time.perf_counter() - t_start, 3)

    (output_dir / "render_evidence.json").write_text(
        json.dumps(asdict(evidence), indent=2), encoding="utf-8")
    return evidence


def _apply_processing(y: np.ndarray, sr: int, node) -> np.ndarray:
    t = node.type
    p = node.params
    if t == "gain":
        db = float(p.get("gain_db", 0))
        return y * (10.0 ** (db / 20.0))
    elif t == "fade_in":
        dur = float(p.get("duration_s", 0.1))
        n = min(int(dur * sr), y.shape[0])
        env = np.ones(y.shape[0])
        env[:n] = np.linspace(0, 1, n)
        return (y.T * env).T
    elif t == "fade_out":
        dur = float(p.get("duration_s", 0.1))
        n = min(int(dur * sr), y.shape[0])
        env = np.ones(y.shape[0])
        env[-n:] = np.linspace(1, 0, n)
        return (y.T * env).T
    elif t == "eq":
        from moodify.processing import apply_rbj_eq
        return apply_rbj_eq(y, sr, p)
    elif t == "compressor":
        from moodify.processing import apply_compressor
        return apply_compressor(y, sr, p)
    elif t == "limiter":
        from moodify.processing import apply_limiter
        return apply_limiter(y, sr, p)
    else:
        raise ValueError(f"Unsupported processing type: {t}")
