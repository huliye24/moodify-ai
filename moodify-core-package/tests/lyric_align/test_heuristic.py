from pathlib import Path

from moodify.lyric_align.backends.heuristic import HeuristicBackend


def test_heuristic_is_monotonic() -> None:
    result = HeuristicBackend().align(
        Path("test.wav"),
        ["one two", "three four five"],
        "en",
        10.0,
        [(1.0, 4.0), (6.0, 9.0)],
    )
    assert result.status == "DRAFT_ONLY"
    assert result.lines[0].start <= result.lines[0].end <= result.lines[1].end
    assert result.lines[0].start <= result.lines[1].start
