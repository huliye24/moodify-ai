"""Object storage adapter (W01-P03).

接口抽象对象存储；当前提供 LocalFileAdapter（测试/本地 dry-run），
OSS 凭据/开通前保持 OSSAdapter 占位（OSS_WRITE_BLOCKED）。
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from pathlib import Path


class ObjectStoreAdapter(ABC):
    """Minimal object storage contract used by the data plane."""

    @abstractmethod
    def put(self, bucket: str, key: str, data: bytes) -> str:
        """Store bytes at key; returns content sha256."""

    @abstractmethod
    def get(self, bucket: str, key: str) -> bytes:
        """Read bytes at key; raises FileNotFoundError-style error if missing."""

    @abstractmethod
    def head(self, bucket: str, key: str) -> int | None:
        """Return byte size if object exists, else None."""

    @abstractmethod
    def list_prefix(self, bucket: str, prefix: str) -> list[str]:
        """List object keys under prefix."""

    @abstractmethod
    def delete(self, bucket: str, key: str) -> bool:
        """Delete object; returns True if existed."""


class LocalFileAdapter(ObjectStoreAdapter):
    """Filesystem-backed adapter (dry-run / tests). Root must be a real dir."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, bucket: str, key: str) -> Path:
        # bucket is a top-level dir under root; key uses '/' separators
        return self.root / bucket / Path(*key.split("/"))

    def put(self, bucket: str, key: str, data: bytes) -> str:
        p = self._path(bucket, key)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return hashlib.sha256(data).hexdigest()

    def get(self, bucket: str, key: str) -> bytes:
        return self._path(bucket, key).read_bytes()

    def head(self, bucket: str, key: str) -> int | None:
        p = self._path(bucket, key)
        return p.stat().st_size if p.exists() else None

    def list_prefix(self, bucket: str, prefix: str) -> list[str]:
        base = self.root / bucket
        if not base.exists():
            return []
        out: list[str] = []
        for p in sorted(base.rglob("*")):
            if p.is_file():
                rel = str(p.relative_to(base)).replace("\\", "/")
                if rel.startswith(prefix):
                    out.append(rel)
        return out

    def delete(self, bucket: str, key: str) -> bool:
        p = self._path(bucket, key)
        if p.exists():
            p.unlink()
            return True
        return False


class OSSAdapter(ObjectStoreAdapter):
    """Aliyun OSS adapter — PLANNED (W01-P03).

    OSS is NOT_PROVISIONED (P00 TT-036); credentials absent.
    Real uploads stay blocked until OSS_WRITE_GATE passes (W01-P03 §6).
    """

    def __init__(self, *, endpoint: str, bucket: str) -> None:
        self.endpoint = endpoint
        self.bucket = bucket

    def put(self, bucket: str, key: str, data: bytes) -> str:
        raise NotImplementedError("OSS not provisioned (OSS_WRITE_BLOCKED)")

    def get(self, bucket: str, key: str) -> bytes:
        raise NotImplementedError("OSS not provisioned (OSS_WRITE_BLOCKED)")

    def head(self, bucket: str, key: str) -> int | None:
        raise NotImplementedError("OSS not provisioned (OSS_WRITE_BLOCKED)")

    def list_prefix(self, bucket: str, prefix: str) -> list[str]:
        raise NotImplementedError("OSS not provisioned (OSS_WRITE_BLOCKED)")

    def delete(self, bucket: str, key: str) -> bool:
        raise NotImplementedError("OSS not provisioned (OSS_WRITE_BLOCKED)")
