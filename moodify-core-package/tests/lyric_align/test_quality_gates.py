from moodify.lyric_align.config import QualityGate
from moodify.lyric_align.models import AlignmentResult, LineTiming, WordTiming
from moodify.lyric_align.quality import apply_rerun_delta, evaluate


def _result(
    lines: tuple[LineTiming, ...],
    backend: str = "whisperx",
    duration: float = 10.0,
) -> AlignmentResult:
    return AlignmentResult(
        backend=backend,
        backend_version="test",
        language="fr",
        audio_path="x.wav",
        audio_duration=duration,
        status="REVIEW_REQUIRED",
        lines=lines,
    )


def _line(
    index: int,
    start: float,
    end: float,
    words: tuple[WordTiming, ...] = (),
    confidence: float = 0.9,
) -> LineTiming:
    return LineTiming(index=index, text="ligne", start=start, end=end, confidence=confidence, words=words)


def test_word_monotonicity_violation_detected() -> None:
    line = _line(
        0, 0.0, 2.0,
        words=(WordTiming("a", 0.0, 1.0, 0.9), WordTiming("b", 0.5, 1.2, 0.9)),
    )
    report = evaluate(_result((line,)))
    assert report.word_monotonicity_violations == 1
    assert "WORD_MONOTONICITY" in report.reasons


def test_boundary_jump_detected() -> None:
    report = evaluate(_result((_line(0, 0.0, 1.0), _line(1, 5.0, 6.0))))
    assert report.boundary_jumps == 1
    assert "BOUNDARY_JUMP" in report.reasons


def test_active_region_agreement() -> None:
    intervals = [(0.0, 10.0)]
    report = evaluate(
        _result((_line(0, 0.0, 2.0), _line(1, 3.0, 5.0))),
        active_intervals=intervals,
    )
    assert report.active_region_agreement == 1.0

    report = evaluate(
        _result((_line(0, 0.0, 2.0), _line(1, 12.0, 14.0))),
        active_intervals=intervals,
    )
    assert report.active_region_agreement == 0.5


def test_gate_override_changes_verdict() -> None:
    line = _line(0, 0.0, 1.0, confidence=0.6)
    strict = QualityGate(min_line_confidence=0.7)
    report = evaluate(_result((line,)), gate=strict)
    assert "LOW_MINIMUM_LINE_CONFIDENCE" in report.reasons


def test_rerun_delta_within_gate_keeps_status() -> None:
    line = _line(0, 0.0, 1.0)
    report = evaluate(_result((line,)))
    report = apply_rerun_delta(report, 40.0)
    assert report.rerun_delta_ms == 40.0
    assert "DETERMINISM_DELTA" not in report.reasons


def test_rerun_delta_exceeding_gate_downgrades() -> None:
    line = _line(0, 0.0, 1.0)
    report = evaluate(_result((line,)))
    report = apply_rerun_delta(report, 150.0)
    assert report.rerun_delta_ms == 150.0
    assert "DETERMINISM_DELTA" in report.reasons
    assert report.status == "REVIEW_REQUIRED"
