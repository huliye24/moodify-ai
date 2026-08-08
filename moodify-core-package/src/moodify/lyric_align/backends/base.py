from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from moodify.lyric_align.models import AlignmentResult


class AlignmentBackend(ABC):
    name: str
    version: str

    @abstractmethod
    def align(
        self,
        wav_path: Path,
        lyric_lines: list[str],
        language: str,
        audio_duration: float,
        active_intervals: list[tuple[float, float]],
        translations: list[str] | None = None,
    ) -> AlignmentResult:
        raise NotImplementedError
