"""Lyric alignment case service — orchestration layer (DSK-MFY-LYRIC-TEMPORAL-ALIGNMENT-001).

The input audio and lyric files are never modified. All outputs are written
into the per-case evidence directory `<case_root>/05_lyric_align/` following the
evidence-manifest pattern used by the auditory subsystem.
"""

from __future__ import annotations

from pathlib import Path

from moodify.lyric_align.pipeline import run_alignment


def run_lyric_alignment(
    case_id: str,
    case_root: Path,
    audio_path: Path,
    lyrics_path: Path,
    language: str,
    translation_path: Path | None = None,
    backend_name: str = "heuristic",
    separate_vocals: str = "auto",
    device: str = "cpu",
    granularity: str | None = None,
) -> dict[str, object]:
    align_dir = case_root / "05_lyric_align"
    align_dir.mkdir(parents=True, exist_ok=True)
    return run_alignment(
        audio_path=audio_path,
        lyrics_path=lyrics_path,
        translation_path=translation_path,
        output_dir=align_dir,
        language=language,
        backend_name=backend_name,
        separate_vocals=separate_vocals,
        device=device,
        granularity=granularity,
    )
