"""Deterministic SHA-256 helpers for canonical evidence."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def validate_sha256(value: str) -> str:
    if not SHA256_RE.fullmatch(value):
        raise ValueError("expected sha256:<64 lowercase hex chars>")
    return value


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    digest = hashlib.sha256()
    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))
