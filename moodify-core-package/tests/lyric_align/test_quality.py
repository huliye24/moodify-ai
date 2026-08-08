from moodify.lyric_align.models import AlignmentResult, LineTiming, WordTiming
from moodify.lyric_align.quality import evaluate


def test_heuristic_is_never_publishable() -> None:
    result = AlignmentResult(
        backend="heuristic",
        backend_version="0.1",
        language="fr",
        audio_path="x.wav",
        audio_duration=1.0,
        status="DRAFT_ONLY",
        lines=(
            LineTiming(
                index=0,
                text="bonjour",
                start=0.0,
                end=1.0,
                confidence=1.0,
                words=(WordTiming("bonjour", 0.0, 1.0, 1.0),),
            ),
        ),
    )
    assert evaluate(result).status == "DRAFT_ONLY"
