"""Object manifest model (W01-P03).

每个重要 object 的可序列化清单，字段对齐 schemas/object_manifest.schema.json。
清单记录元数据（在 DB 中）与对象本体（在 object storage）分离；
manifest 本身可随 evidence 落盘。
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

RETENTION_CLASSES = (
    "source_long_lived",
    "stems_configurable",
    "intermediate_short",
    "render_versioned",
    "evidence_long_lived",
    "logs_operational",
    "temp_ephemeral",
)

ARTIFACT_TYPES = ("source", "stems", "analysis", "intermediate", "renders", "evidence")

HASH_ALGORITHMS = ("sha256",)


@dataclass
class ObjectManifest:
    object_id: str
    track_id: str
    artifact_type: str
    bucket: str
    object_key: str
    content_hash: str
    byte_size: int
    producer: str
    hash_algorithm: str = "sha256"
    artifact_role: str | None = None
    job_id: str | None = None
    mime_type: str | None = None
    producer_version: str | None = None
    pipeline_version: str | None = None
    source_object_id: str | None = None
    parent_object_id: str | None = None
    immutable: bool = True
    retention_class: str = "render_versioned"
    evidence_class: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        if self.artifact_type not in ARTIFACT_TYPES:
            raise ValueError(f"artifact_type must be one of {ARTIFACT_TYPES}")
        if self.hash_algorithm not in HASH_ALGORITHMS:
            raise ValueError(f"hash_algorithm must be one of {HASH_ALGORITHMS}")
        if self.retention_class not in RETENTION_CLASSES:
            raise ValueError(f"retention_class must be one of {RETENTION_CLASSES}")
        if len(self.content_hash) != 64:
            raise ValueError("content_hash must be a 64-char hex sha256")

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=indent)


def manifest_from_dict(data: dict) -> ObjectManifest:
    known = {k: v for k, v in data.items() if k in ObjectManifest.__dataclass_fields__}
    return ObjectManifest(**known)
