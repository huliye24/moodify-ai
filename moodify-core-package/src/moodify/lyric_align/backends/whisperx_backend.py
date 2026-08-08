from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from moodify.lyric_align.backends.base import AlignmentBackend
from moodify.lyric_align.backends.heuristic import HeuristicBackend
from moodify.lyric_align.models import AlignmentResult, LineTiming, WordTiming


class WhisperXBackend(AlignmentBackend):
    name = "whisperx"

    def __init__(self, device: str = "cpu") -> None:
        self.device = device
        try:
            self.version = version("whisperx")
        except PackageNotFoundError as exc:
            raise RuntimeError(
                "WhisperX backend requested but whisperx is not installed. "
                "Install with: pip install -e '.[ml]'"
            ) from exc

    def align(
        self,
        wav_path: Path,
        lyric_lines: list[str],
        language: str,
        audio_duration: float,
        active_intervals: list[tuple[float, float]],
        translations: list[str] | None = None,
    ) -> AlignmentResult:
        try:
            import whisperx
        except ImportError as exc:
            raise RuntimeError("Failed to import whisperx.") from exc

        coarse = HeuristicBackend().align(
            wav_path,
            lyric_lines,
            language,
            audio_duration,
            active_intervals,
            translations,
        )
        segments = [
            {"start": line.start, "end": line.end, "text": line.text}
            for line in coarse.lines
        ]
        audio = whisperx.load_audio(str(wav_path))
        model_a, metadata = whisperx.load_align_model(language_code=language, device=self.device)
        raw: dict[str, Any] = whisperx.align(
            segments,
            model_a,
            metadata,
            audio,
            self.device,
            return_char_alignments=True,
        )

        raw_segments = raw.get("segments", [])
        lines: list[LineTiming] = []
        warnings: list[str] = []
        for index, original in enumerate(lyric_lines):
            if index >= len(raw_segments):
                warnings.append(f"No aligned segment returned for line {index}.")
                fallback = coarse.lines[index]
                lines.append(fallback)
                continue
            segment = raw_segments[index]
            start = float(segment.get("start", coarse.lines[index].start))
            end = float(segment.get("end", coarse.lines[index].end))
            raw_words = segment.get("words") or []
            words: list[WordTiming] = []
            for word in raw_words:
                if "start" not in word or "end" not in word:
                    continue
                score = float(word.get("score", 0.0))
                words.append(
                    WordTiming(
                        text=str(word.get("word", "")).strip(),
                        start=round(float(word["start"]), 3),
                        end=round(float(word["end"]), 3),
                        confidence=max(0.0, min(1.0, score)),
                    )
                )
            confidence = sum(w.confidence for w in words) / len(words) if words else 0.0
            lines.append(
                LineTiming(
                    index=index,
                    text=original,
                    translation=translations[index] if translations else None,
                    start=round(start, 3),
                    end=round(max(end, start + 0.02), 3),
                    confidence=round(confidence, 4),
                    words=tuple(words),
                )
            )

        return AlignmentResult(
            backend=self.name,
            backend_version=self.version,
            language=language,
            audio_path=str(wav_path),
            audio_duration=audio_duration,
            status="REVIEW_REQUIRED",
            lines=tuple(lines),
            warnings=tuple(warnings),
            provenance={
                "active_intervals": active_intervals,
                "coarse_segments": segments,
                "raw_backend": "whisperx.align",
                "raw_segments": raw_segments,
            },
        )
