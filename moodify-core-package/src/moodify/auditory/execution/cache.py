"""Hash-verified filesystem cache; local only and fail-safe on corruption."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from moodify.auditory.identity import canonical_json


class CacheCorruptionError(ValueError):
    pass


class LocalCache:
    SCHEMA_VERSION = "local-cache-v1"

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _dir(self, source_sha256: str, key: str) -> Path:
        return self.root / source_sha256 / "nodes" / key

    def put(self, source_sha256: str, key: str, value: Any,
            node_id: str, node_version: str,
            dependency_hashes: dict[str, str]) -> tuple[str, int]:
        target = self._dir(source_sha256, key)
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = Path(tempfile.mkdtemp(prefix=f".{key}-", dir=target.parent))
        try:
            arrays: dict[str, np.ndarray] = {}
            encoded = _encode(value, arrays)
            payload = canonical_json(encoded).encode("utf-8")
            (temp / "payload.json").write_bytes(payload)
            if arrays:
                np.savez_compressed(temp / "arrays.npz", **arrays)
            content_hash = _directory_content_hash(temp)
            byte_size = sum(p.stat().st_size for p in temp.iterdir())
            manifest = {
                "schema_version": self.SCHEMA_VERSION,
                "key": key,
                "node_id": node_id,
                "node_version": node_version,
                "source_sha256": source_sha256,
                "dependency_hashes": dependency_hashes,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "logical_content_hash": content_hash,
                "byte_size": byte_size,
            }
            (temp / "manifest.json").write_text(canonical_json(manifest), encoding="utf-8")
            if target.exists():
                shutil.rmtree(target)
            os.replace(temp, target)
            return content_hash, byte_size
        finally:
            if temp.exists():
                shutil.rmtree(temp)

    def get(self, source_sha256: str, key: str,
            dependency_hashes: dict[str, str]) -> tuple[Any, str, int] | None:
        target = self._dir(source_sha256, key)
        if not target.exists():
            return None
        try:
            manifest = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
            if manifest["schema_version"] != self.SCHEMA_VERSION:
                return None
            if manifest["source_sha256"] != source_sha256:
                return None
            if manifest["dependency_hashes"] != dependency_hashes:
                return None
            actual = _directory_content_hash(target, exclude={"manifest.json"})
            if actual != manifest["logical_content_hash"]:
                raise CacheCorruptionError(f"cache hash mismatch: {key}")
            encoded = json.loads((target / "payload.json").read_text(encoding="utf-8"))
            arrays_path = target / "arrays.npz"
            arrays = np.load(arrays_path, allow_pickle=False) if arrays_path.exists() else {}
            try:
                value = _decode(encoded, arrays)
            finally:
                if hasattr(arrays, "close"):
                    arrays.close()
            return value, actual, int(manifest["byte_size"])
        except CacheCorruptionError:
            raise
        except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
            raise CacheCorruptionError(f"unreadable cache entry: {key}") from exc

    def remove_entry(self, source_sha256: str, key: str) -> None:
        target = self._dir(source_sha256, key)
        if target.exists():
            shutil.rmtree(target)

    def clear_source(self, source_sha256: str) -> None:
        target = self.root / source_sha256
        if target.exists():
            shutil.rmtree(target)

    def clear_all(self) -> None:
        for child in self.root.iterdir():
            if child.is_dir():
                shutil.rmtree(child)

    def size_bytes(self) -> int:
        return sum(p.stat().st_size for p in self.root.rglob("*") if p.is_file())


def _encode(value: Any, arrays: dict[str, np.ndarray]) -> Any:
    if isinstance(value, np.ndarray):
        name = f"array_{len(arrays)}"
        arrays[name] = value
        return {"__ndarray__": name}
    if isinstance(value, dict):
        return {str(k): _encode(v, arrays) for k, v in value.items()}
    if isinstance(value, tuple):
        return {"__tuple__": [_encode(v, arrays) for v in value]}
    if isinstance(value, list):
        return [_encode(v, arrays) for v in value]
    if isinstance(value, np.generic):
        return value.item()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "to_dict"):
        return {"__object_dict__": _encode(value.to_dict(), arrays)}
    raise TypeError(f"unsupported cache value: {type(value).__name__}")


def _decode(value: Any, arrays: Any) -> Any:
    if isinstance(value, list):
        return [_decode(v, arrays) for v in value]
    if isinstance(value, dict):
        if "__ndarray__" in value:
            return np.asarray(arrays[value["__ndarray__"]])
        if "__tuple__" in value:
            return tuple(_decode(v, arrays) for v in value["__tuple__"])
        if "__object_dict__" in value:
            return _decode(value["__object_dict__"], arrays)
        return {k: _decode(v, arrays) for k, v in value.items()}
    return value


def _directory_content_hash(path: Path, exclude: set[str] | None = None) -> str:
    digest = hashlib.sha256()
    for item in sorted(path.iterdir(), key=lambda p: p.name):
        if not item.is_file() or item.name in (exclude or set()):
            continue
        digest.update(item.name.encode("utf-8"))
        digest.update(item.read_bytes())
    return digest.hexdigest()
