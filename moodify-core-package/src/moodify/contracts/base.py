"""Shared validation primitives for Moodify's canonical v1 contracts."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, field_validator

SchemaVersion = Literal["1.0"]


class FrozenDict(dict):
    """A JSON-compatible mapping that blocks mutation after construction."""

    def _immutable(self, *args: Any, **kwargs: Any) -> None:
        raise TypeError("canonical JSON mappings are immutable")

    __delitem__ = _immutable
    __setitem__ = _immutable
    clear = _immutable
    pop = _immutable
    popitem = _immutable
    setdefault = _immutable
    update = _immutable


class CanonicalModel(BaseModel):
    """Immutable base shared by every canonical contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: SchemaVersion = "1.0"
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def require_aware_datetime(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")
        return value.astimezone(timezone.utc)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def ensure_json_safe(value: Any, path: str = "$") -> None:
    """Reject values that cannot be represented by canonical JSON."""
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{path}: NaN/Infinity are not canonical JSON values")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            ensure_json_safe(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{path}: JSON object keys must be strings")
            ensure_json_safe(item, f"{path}.{key}")
        return
    raise ValueError(f"{path}: unsupported non-JSON-safe value {type(value)!r}")


def freeze_json_value(value: Any) -> Any:
    """Recursively freeze an already validated JSON-safe value."""
    if isinstance(value, dict):
        return FrozenDict({key: freeze_json_value(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(freeze_json_value(item) for item in value)
    return value
