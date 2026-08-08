from __future__ import annotations

import json
from pathlib import Path

from moodify.lyric_align.models import AlignmentResult
from moodify.lyric_align.quality import QualityReport


def lrc_timestamp(seconds: float) -> str:
    seconds = max(0.0, seconds)
    minutes = int(seconds // 60)
    remainder = seconds - minutes * 60
    return f"[{minutes:02d}:{remainder:05.2f}]"


def srt_timestamp(seconds: float) -> str:
    milliseconds = round(max(0.0, seconds) * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    secs, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def ass_timestamp(seconds: float) -> str:
    centiseconds = round(max(0.0, seconds) * 100)
    hours, centiseconds = divmod(centiseconds, 360_000)
    minutes, centiseconds = divmod(centiseconds, 6_000)
    secs, centiseconds = divmod(centiseconds, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"


def write_outputs(result: AlignmentResult, quality: QualityReport, output_dir: str | Path) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    payload = result.to_dict()
    payload["status"] = quality.status
    (out / "alignment.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "qc_report.json").write_text(
        json.dumps(quality.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lrc_lines = [f"{lrc_timestamp(line.start)}{line.text}" for line in result.lines]
    (out / "lyrics.lrc").write_text("\n".join(lrc_lines) + "\n", encoding="utf-8")

    enhanced: list[str] = []
    for line in result.lines:
        if line.words:
            body = " ".join(
                f"<{lrc_timestamp(word.start)[1:-1]}>{word.text}" for word in line.words
            )
        else:
            body = line.text
        enhanced.append(f"{lrc_timestamp(line.start)}{body}")
    (out / "lyrics.enhanced.lrc").write_text("\n".join(enhanced) + "\n", encoding="utf-8")

    bilingual = [
        f"{lrc_timestamp(line.start)}{line.text}\n{lrc_timestamp(line.start)}{line.translation}"
        for line in result.lines if line.translation
    ]
    if bilingual:
        (out / "lyrics_bilingual.lrc").write_text("\n".join(bilingual) + "\n", encoding="utf-8")

    srt: list[str] = []
    for i, line in enumerate(result.lines, start=1):
        text = line.text if not line.translation else f"{line.text}\n{line.translation}"
        srt.extend([str(i), f"{srt_timestamp(line.start)} --> {srt_timestamp(line.end)}", text, ""])
    (out / "lyrics.srt").write_text("\n".join(srt), encoding="utf-8")

    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,54,&H00FFFFFF,&H0000FFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2,1,2,80,80,80,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events: list[str] = []
    for line in result.lines:
        if line.words:
            karaoke = "".join(
                f"{{\\k{max(1, round((word.end - word.start) * 100))}}}{word.text} "
                for word in line.words
            ).rstrip()
        else:
            karaoke = line.text
        if line.translation:
            karaoke = f"{karaoke}\\N{line.translation}"
        events.append(
            f"Dialogue: 0,{ass_timestamp(line.start)},{ass_timestamp(line.end)},Default,,0,0,0,,{karaoke}"
        )
    (out / "lyrics.ass").write_text(ass_header + "\n".join(events) + "\n", encoding="utf-8")
