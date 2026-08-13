"""Authenticated, streaming beta-media ingestion for the LA BFF."""

from __future__ import annotations

import hashlib
import os
import re
import tempfile
import uuid
from pathlib import Path

MAX_AUDIO_BYTES = 100 * 1024 * 1024
ALLOWED_MIME = {
    "audio/wav": ".wav", "audio/x-wav": ".wav", "audio/mpeg": ".mp3",
    "audio/flac": ".flac", "audio/ogg": ".ogg", "audio/mp4": ".m4a",
    "audio/aac": ".aac",
}


def media_root() -> Path:
    return Path(os.environ.get("MOODIFY_BFF_MEDIA_ROOT", "/opt/moodify/music-media/audio"))


def safe_filename(value: str, mime: str) -> str:
    stem = Path(value).stem[:80]
    stem = re.sub(r"[^a-zA-Z0-9._-]+", "-", stem).strip("-.") or "audio"
    return stem + ALLOWED_MIME[mime]


def looks_like_audio(head: bytes, mime: str) -> bool:
    if mime in {"audio/wav", "audio/x-wav"}:
        return len(head) >= 12 and head[:4] == b"RIFF" and head[8:12] == b"WAVE"
    if mime == "audio/flac":
        return head.startswith(b"fLaC")
    if mime == "audio/ogg":
        return head.startswith(b"OggS")
    if mime == "audio/mpeg":
        return head.startswith(b"ID3") or (len(head) >= 2 and head[0] == 0xFF and head[1] & 0xE0 == 0xE0)
    if mime == "audio/mp4":
        return len(head) >= 12 and head[4:8] == b"ftyp"
    if mime == "audio/aac":
        return len(head) >= 2 and head[0] == 0xFF and head[1] & 0xF6 == 0xF0
    return False


def allocate_upload(user_id: str, filename: str, mime: str) -> tuple[str, Path, Path]:
    relative = Path("beta") / user_id / uuid.uuid4().hex / safe_filename(filename, mime)
    final_path = media_root() / relative
    final_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".upload-", dir=final_path.parent)
    os.close(fd)
    return relative.as_posix(), Path(temporary), final_path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
