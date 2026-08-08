from moodify.lyric_align.models import AlignmentResult, LineTiming
from moodify.lyric_align.pipeline import _median_boundary_delta


def _result(lines: tuple[LineTiming, ...]) -> AlignmentResult:
    return AlignmentResult(
        backend="heuristic",
        backend_version="0.1",
        language="fr",
        audio_path="x.wav",
        audio_duration=10.0,
        status="DRAFT_ONLY",
        lines=lines,
    )


def test_median_boundary_delta_zero_for_identical() -> None:
    lines = (LineTiming(0, "a", 0.0, 1.0, 0.5), LineTiming(1, "b", 1.2, 2.0, 0.5))
    assert _median_boundary_delta(_result(lines), _result(lines)) == 0.0


def test_median_boundary_delta_measures_shift() -> None:
    first = (LineTiming(0, "a", 0.0, 1.0, 0.5),)
    second = (LineTiming(0, "a", 0.1, 1.1, 0.5),)
    assert _median_boundary_delta(_result(first), _result(second)) == 0.1
