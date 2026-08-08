from __future__ import annotations

from pathlib import Path

from moodify.lyric_align.backends.base import AlignmentBackend
from moodify.lyric_align.lyrics import normalize_for_alignment, split_words
from moodify.lyric_align.models import AlignmentResult, LineTiming, WordTiming


class HeuristicBackend(AlignmentBackend):
    name = "heuristic"
    version = "0.1"

    @staticmethod
    def _flatten_active_time(
        intervals: list[tuple[float, float]],
        audio_duration: float,
    ) -> list[tuple[float, float]]:
        return intervals or [(0.0, audio_duration)]

    @staticmethod
    def _point_at_active_fraction(intervals: list[tuple[float, float]], fraction: float) -> float:
        fraction = min(1.0, max(0.0, fraction))
        lengths = [max(0.0, end - start) for start, end in intervals]
        total = sum(lengths)
        if total <= 0:
            return intervals[0][0]
        target = total * fraction
        elapsed = 0.0
        for (start, end), length in zip(intervals, lengths):
            if elapsed + length >= target:
                return start + (target - elapsed)
            elapsed += length
        return intervals[-1][1]

    def align(
        self,
        wav_path: Path,
        lyric_lines: list[str],
        language: str,
        audio_duration: float,
        active_intervals: list[tuple[float, float]],
        translations: list[str] | None = None,
    ) -> AlignmentResult:
        intervals = self._flatten_active_time(active_intervals, audio_duration)
        weights = [max(1, len(normalize_for_alignment(line, language).replace(" ", ""))) for line in lyric_lines]
        total_weight = sum(weights)
        cumulative = 0
        line_timings: list[LineTiming] = []

        for index, (line, weight) in enumerate(zip(lyric_lines, weights)):
            start_fraction = cumulative / total_weight
            cumulative += weight
            end_fraction = cumulative / total_weight
            start = self._point_at_active_fraction(intervals, start_fraction)
            end = self._point_at_active_fraction(intervals, end_fraction)
            end = max(end, start + 0.05)

            tokens = split_words(line, language)
            token_weights = [max(1, len(token)) for token in tokens]
            token_total = sum(token_weights) or 1
            token_elapsed = 0
            words: list[WordTiming] = []
            for token, token_weight in zip(tokens, token_weights):
                ws = start + (end - start) * token_elapsed / token_total
                token_elapsed += token_weight
                we = start + (end - start) * token_elapsed / token_total
                words.append(
                    WordTiming(
                        text=token,
                        normalized_text=normalize_for_alignment(token, language),
                        start=round(ws, 3),
                        end=round(max(we, ws + 0.02), 3),
                        confidence=0.20,
                    )
                )

            translation = translations[index] if translations else None
            line_timings.append(
                LineTiming(
                    index=index,
                    text=line,
                    translation=translation,
                    start=round(start, 3),
                    end=round(end, 3),
                    confidence=0.20,
                    words=tuple(words),
                )
            )

        return AlignmentResult(
            backend=self.name,
            backend_version=self.version,
            language=language,
            audio_path=str(wav_path),
            audio_duration=audio_duration,
            status="DRAFT_ONLY",
            lines=tuple(line_timings),
            warnings=(
                "Heuristic alignment is not suitable for publication.",
                "Use a known-transcript phoneme alignment backend and pass QC gates.",
            ),
            provenance={"active_intervals": active_intervals},
        )
