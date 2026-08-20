"""Data plane ID generation (W01-P03).

全局唯一 ID，不依赖单个数据库实例解释，可在 worker/API/object store 间传递。
采用 UUIDv7（RFC 9562）：时间有序 + 随机，适合日志与跨区域迁移。
无外部依赖（标准库实现）。
"""

from __future__ import annotations

import os
import time
import uuid
from typing import Literal

_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"


def uuid7() -> uuid.UUID:
    """Generate a UUIDv7 (time-ordered, RFC 9562)."""
    ms = int(time.time() * 1000) & 0xFFFFFFFFFFFFFFFF
    rand = os.urandom(10)
    ver = (0b0111 << 12) | (int.from_bytes(rand[:2], "big") & 0x0FFF)
    variant = (0b10 << 14) | (int.from_bytes(rand[2:4], "big") & 0x3FFF)
    return uuid.UUID(
        int=(
            (ms << 80)
            | (ver << 64)
            | (variant << 48)
            | int.from_bytes(rand[4:10], "big")
        )
    )


def _slug(prefix: str, n: int = 24) -> str:
    """Deterministic suffix from a UUIDv7 (lowercase hex, no dashes)."""
    return uuid7().hex[:n]


def new_id(kind: Literal["track", "job", "object", "evidence", "version"]) -> str:
    """Prefixed, globally unique data-plane id (e.g. trk_..., job_...)."""
    prefix_map = {
        "track": "trk",
        "job": "job",
        "object": "obj",
        "evidence": "ev",
        "version": "ver",
    }
    if kind not in prefix_map:
        raise ValueError(f"unknown id kind: {kind!r}")
    return f"{prefix_map[kind]}_{_slug(kind)}"


def is_valid_id(value: str, kind: str) -> bool:
    """Validate a prefixed id for a given kind."""
    prefix_map = {"track": "trk", "job": "job", "object": "obj", "evidence": "ev", "version": "ver"}
    if kind not in prefix_map:
        return False
    prefix = prefix_map[kind]
    return value.startswith(f"{prefix}_") and len(value) == len(prefix) + 1 + 24 and all(
        c in _ALPHABET for c in value[len(prefix) + 1 :]
    )
