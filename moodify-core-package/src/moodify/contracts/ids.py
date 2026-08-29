"""Opaque, type-prefixed canonical identifiers."""

from __future__ import annotations

import re
from typing import Literal
from uuid import uuid4

IdKind = Literal["case", "meas", "evid", "rule", "finding"]

_PATTERNS = {
    kind: re.compile(rf"^{kind}_[0-9a-f]{{32}}$")
    for kind in ("case", "meas", "evid", "rule", "finding")
}


def new_id(kind: IdKind) -> str:
    if kind not in _PATTERNS:
        raise ValueError(f"unsupported canonical ID kind: {kind}")
    return f"{kind}_{uuid4().hex}"


def validate_id(value: str, kind: IdKind) -> str:
    if not _PATTERNS[kind].fullmatch(value):
        raise ValueError(f"invalid {kind} canonical ID")
    return value
