"""Authenticated, streaming beta-media ingestion for the LA BFF."""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path

MAX_AUDIO_BYTES = 100 * 1024 * 1024
ALLOWED_MIME = {
    "audio/wav": ".wav", "audio/x-wav": ".wav", "audio/mpeg": ".mp3",
    "audio/flac": ".flac", "audio/ogg": ".ogg", "audio/mp4": ".m4a",
    "audio/aac": ".aac",
}


def media_root() -> Path:
    return Path(os.environ.get("MOODIFY_BFF_MEDIA_ROOT", "/opt/moodify/music-media/audio"))


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


def _user_media_root(user_id: str) -> Path:
    if not user_id or any(character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for character in user_id):
        raise ValueError("invalid media user id")
    return media_root() / "beta" / user_id


def allocate_upload(user_id: str) -> Path:
    incoming = _user_media_root(user_id) / ".incoming"
    incoming.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="upload-", dir=incoming)
    os.close(fd)
    return Path(temporary)


def promote_upload(user_id: str, temporary: Path, digest: str, mime: str) -> tuple[str, bool]:
    """Atomically publish one content-addressed object; return key and dedupe state."""
    relative = Path("beta") / user_id / "sha256" / digest[:2] / f"{digest}{ALLOWED_MIME[mime]}"
    final_path = media_root() / relative
    final_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(temporary, final_path)
        os.chmod(final_path, 0o644)
        deduplicated = False
    except FileExistsError:
        deduplicated = True
    return relative.as_posix(), deduplicated


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
