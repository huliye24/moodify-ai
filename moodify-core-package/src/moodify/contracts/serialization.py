"""Stable JSON interchange helpers for canonical models."""

import json
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def to_canonical_dict(model: BaseModel) -> dict[str, object]:
    return model.model_dump(mode="json", exclude_none=False)


def to_canonical_json(model: BaseModel) -> str:
    return json.dumps(
        to_canonical_dict(model),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def from_canonical_json(model_cls: type[T], data: str | bytes) -> T:
    if isinstance(data, bytes):
        data = data.decode("utf-8")
    return model_cls.model_validate_json(data)
