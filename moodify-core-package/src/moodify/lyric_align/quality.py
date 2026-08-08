from __future__ import annotations

from dataclasses import dataclass, replace

from moodify.lyric_align.config import QualityGate
from moodify.lyric_align.models import AlignmentResult


@dataclass(frozen=True)
class QualityReport:
    status: str
    line_count: int
    word_count: int
    temporal_inversions: int
    line_overlaps: int
    coverage: float
    mean_word_confidence: float
    minimum_line_confidence: float
    unaligned_token_ratio: float
    word_monotonicity_violations: int
    boundary_jumps: int
    active_region_agreement: float
    rerun_delta_ms: float | None
    review_regions: tuple[dict[str, object], ...]
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "line_count": self.line_count,
            "word_count": self.word_count,
            "temporal_inversions": self.temporal_inversions,
            "line_overlaps": self.line_overlaps,
            "coverage": self.coverage,
            "mean_word_confidence": self.mean_word_confidence,
            "minimum_line_confidence": self.minimum_line_confidence,
            "unaligned_token_ratio": self.unaligned_token_ratio,
            "word_monotonicity_violations": self.word_monotonicity_violations,
            "boundary_jumps": self.boundary_jumps,
            "active_region_agreement": self.active_region_agreement,
            "rerun_delta_ms": self.rerun_delta_ms,
            "review_regions": list(self.review_regions),
            "reasons": list(self.reasons),
        }


def evaluate(
    result: AlignmentResult,
    gate: QualityGate | None = None,
    active_intervals: list[tuple[float, float]] | None = None,
) -> QualityReport:
    gate = gate or QualityGate()
    inversions = 0
    overlaps = 0
    word_violations = 0
    boundary_jumps = 0
    review: list[dict[str, object]] = []
    previous_start = -1.0
    previous_end = -1.0
    last_word_end = -1.0
    aligned_words = 0
    expected_words = 0
    word_scores: list[float] = []
    line_scores: list[float] = []
    active_hits = 0
    active = active_intervals or []

    def in_active(t: float) -> bool:
        return any(start <= t <= end for start, end in active)

    for line in result.lines:
        line_scores.append(line.confidence)
        if line.start < previous_start or line.end < line.start:
            inversions += 1
        if previous_end >= 0 and line.start < previous_end - gate.max_line_overlap_seconds:
            overlaps += 1
        if previous_end >= 0 and line.start - previous_end > gate.max_boundary_jump_seconds:
            boundary_jumps += 1
        if active and not in_active(line.start):
            active_hits += 1
        for word in line.words:
            if last_word_end >= 0 and word.start < last_word_end:
                word_violations += 1
            last_word_end = max(last_word_end, word.end)
        previous_start = line.start
        previous_end = max(previous_end, line.end)
        expected_words += max(1, len(line.text.split()))
        aligned_words += len(line.words)
        word_scores.extend(word.confidence for word in line.words)
        if line.confidence < gate.min_line_confidence:
            review.append(
                {
                    "line_index": line.index,
                    "start": line.start,
                    "end": line.end,
                    "reason": "LOW_LINE_CONFIDENCE",
                }
            )

    covered = sum(max(0.0, line.end - line.start) for line in result.lines)
    coverage = min(1.0, covered / result.audio_duration) if result.audio_duration > 0 else 0.0
    mean_word = sum(word_scores) / len(word_scores) if word_scores else 0.0
    min_line = min(line_scores) if line_scores else 0.0
    unaligned_ratio = max(0.0, 1.0 - aligned_words / expected_words) if expected_words else 1.0
    agreement = 1.0 - active_hits / len(result.lines) if active and result.lines else 1.0

    reasons: list[str] = []
    status = "PUBLISHABLE"
    if result.backend == "heuristic":
        status = "DRAFT_ONLY"
        reasons.append("HEURISTIC_BACKEND")
    checks = [
        (inversions == 0, "TEMPORAL_INVERSION"),
        (overlaps == 0, "LINE_OVERLAP"),
        (coverage >= gate.min_coverage, "LOW_COVERAGE"),
        (unaligned_ratio <= gate.max_unaligned_token_ratio, "TOO_MANY_UNALIGNED_TOKENS"),
        (mean_word >= gate.min_mean_word_confidence, "LOW_MEAN_WORD_CONFIDENCE"),
        (min_line >= gate.min_line_confidence, "LOW_MINIMUM_LINE_CONFIDENCE"),
        (word_violations == 0, "WORD_MONOTONICITY"),
        (boundary_jumps == 0, "BOUNDARY_JUMP"),
    ]
    failed = [reason for passed, reason in checks if not passed]
    reasons.extend(failed)
    if result.backend != "heuristic" and failed:
        status = "REVIEW_REQUIRED"

    return QualityReport(
        status=status,
        line_count=len(result.lines),
        word_count=aligned_words,
        temporal_inversions=inversions,
        line_overlaps=overlaps,
        coverage=round(coverage, 4),
        mean_word_confidence=round(mean_word, 4),
        minimum_line_confidence=round(min_line, 4),
        unaligned_token_ratio=round(unaligned_ratio, 4),
        word_monotonicity_violations=word_violations,
        boundary_jumps=boundary_jumps,
        active_region_agreement=round(agreement, 4),
        rerun_delta_ms=None,
        review_regions=tuple(review),
        reasons=tuple(reasons),
    )


def apply_rerun_delta(
    report: QualityReport,
    delta_ms: float,
    gate: QualityGate | None = None,
) -> QualityReport:
    """Attach the deterministic-rerun delta and downgrade if the gate is exceeded."""
    gate = gate or QualityGate()
    delta = round(delta_ms, 1)
    reasons = report.reasons
    status = report.status
    if delta > gate.max_rerun_delta_ms:
        reasons = reasons + ("DETERMINISM_DELTA",)
        if status == "PUBLISHABLE":
            status = "REVIEW_REQUIRED"
    return replace(report, rerun_delta_ms=delta, reasons=reasons, status=status)
