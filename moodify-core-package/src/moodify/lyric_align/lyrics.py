from __future__ import annotations

import re
import unicodedata
from pathlib import Path

SECTION_WORDS = (
    "couplet",
    "verse",
    "pré-refrain",
    "pre-refrain",
    "prechorus",
    "refrain",
    "chorus",
    "pont",
    "bridge",
    "intro",
    "outro",
    "interlude",
    "主歌",
    "副歌",
    "预副歌",
    "桥段",
    "前奏",
    "尾奏",
    "间奏",
)

BRACKETED = re.compile(r"^\s*[\[【(（].*?[\]】)）]\s*$")
SECTION = re.compile(
    rf"^\s*(?:{'|'.join(re.escape(x) for x in SECTION_WORDS)})(?:\s*\d+)?\s*[:：-]?\s*$",
    flags=re.IGNORECASE,
)
SPACE = re.compile(r"\s+")


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8-sig")


def clean_lyrics(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        line = SPACE.sub(" ", raw.strip())
        if not line:
            continue
        if BRACKETED.match(line) or SECTION.match(line):
            continue
        lines.append(line)
    if not lines:
        raise ValueError("No lyric lines remained after cleaning.")
    return lines


def clean_lyrics_file(path: str | Path) -> list[str]:
    return clean_lyrics(read_text(path))


def normalize_for_alignment(text: str, language: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    text = text.replace("’", "'").replace("œ", "oe").replace("æ", "ae")
    if language.startswith("fr"):
        text = "".join(
            char for char in unicodedata.normalize("NFD", text)
            if unicodedata.category(char) != "Mn"
        )
    text = re.sub(r"[^\w'\-\u3400-\u9fff]+", " ", text, flags=re.UNICODE)
    return SPACE.sub(" ", text).strip()


def split_words(display_text: str, language: str) -> list[str]:
    if language.startswith(("zh", "ja")):
        return [c for c in display_text if not c.isspace() and not unicodedata.category(c).startswith("P")]
    return [token for token in SPACE.split(display_text.strip()) if token]
