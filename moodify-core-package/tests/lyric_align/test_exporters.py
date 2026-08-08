from moodify.lyric_align.exporters import ass_timestamp, lrc_timestamp, srt_timestamp


def test_timestamps() -> None:
    assert lrc_timestamp(61.235) == "[01:01.23]"
    assert srt_timestamp(61.235) == "00:01:01,235"
    assert ass_timestamp(61.235) == "0:01:01.24"
