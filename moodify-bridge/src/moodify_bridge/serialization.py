from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypeVar

import yaml
from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


def canonical_json(model: BaseModel) -> str:
    return json.dumps(model.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))


def read_model(path: Path, model_type: type[ModelT]) -> ModelT:
    data: Any
    with path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream) if path.suffix.lower() in {".yaml", ".yml"} else json.load(stream)
    return model_type.model_validate(data)


def write_yaml(path: Path, model: BaseModel) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.loads(model.model_dump_json())
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
