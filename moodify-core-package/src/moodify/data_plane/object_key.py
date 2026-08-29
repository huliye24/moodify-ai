"""Object key convention for Moodify object storage (W01-P03).

Key 是定位符（locator），不是业务身份（INV-02）。业务身份 = object_id（UUIDv7）。
不依赖用户原始文件名、不含 Secret、不含 PII、Windows/Linux/cloud 安全。

Convention:
    moodify/tracks/{track_id}/source/{object_id}.{ext}
    moodify/tracks/{track_id}/jobs/{job_id}/stems/{object_id}.{ext}
    moodify/tracks/{track_id}/jobs/{job_id}/analysis/{object_id}.{ext}
    moodify/tracks/{track_id}/jobs/{job_id}/intermediate/{object_id}.{ext}
    moodify/tracks/{track_id}/jobs/{job_id}/renders/{object_id}.{ext}
    moodify/tracks/{track_id}/jobs/{job_id}/evidence/{object_id}.{ext}
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

ARTIFACT_TYPES = ("source", "stems", "analysis", "intermediate", "renders", "evidence")
VALID_EXT_RE = re.compile(r"^[a-z0-9]{1,8}$")


@dataclass(frozen=True)
class ObjectKey:
    bucket: str
    key: str
    track_id: str
    job_id: str | None
    artifact_type: Literal["source", "stems", "analysis", "intermediate", "renders", "evidence"]
    object_id: str

    @property
    def full(self) -> str:
        return f"{self.bucket}/{self.key}"


def _ext_from_filename(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    if not VALID_EXT_RE.match(ext):
        return "bin"
    return ext


def build_object_key(
    *,
    track_id: str,
    object_id: str,
    artifact_type: str,
    job_id: str | None = None,
    filename: str | None = None,
    bucket: str = "moodify",
) -> ObjectKey:
    """Build an object key following the data-plane convention."""
    if artifact_type not in ARTIFACT_TYPES:
        raise ValueError(f"artifact_type must be one of {ARTIFACT_TYPES}, got {artifact_type!r}")
    ext = _ext_from_filename(filename or "")
    if artifact_type == "source":
        if job_id is not None:
            raise ValueError("source objects are not job-scoped")
        key = f"moodify/tracks/{track_id}/source/{object_id}.{ext}"
    else:
        if job_id is None:
            raise ValueError(f"{artifact_type} objects require job_id")
        key = f"moodify/tracks/{track_id}/jobs/{job_id}/{artifact_type}/{object_id}.{ext}"
    return ObjectKey(
        bucket=bucket,
        key=key,
        track_id=track_id,
        job_id=job_id,
        artifact_type=artifact_type,  # type: ignore[arg-type]
        object_id=object_id,
    )


def _parse_key(bucket: str, key: str) -> ObjectKey:
    seg = key.split("/")
    # moodify / tracks / {track_id} / source | jobs / {job_id} / {type} / {obj}.{ext}
    if len(seg) == 5 and seg[:2] == ["moodify", "tracks"] and seg[3] == "source":
        track_id, obj = seg[2], seg[4]
        return ObjectKey(bucket, key, track_id, None, "source", obj.rsplit(".", 1)[0])
    if len(seg) == 7 and seg[:2] == ["moodify", "tracks"] and seg[3] == "jobs":
        track_id, job_id, atype, obj = seg[2], seg[4], seg[5], seg[6]
        if atype not in ARTIFACT_TYPES:
            raise ValueError(f"unknown artifact_type in key: {atype!r}")
        return ObjectKey(bucket, key, track_id, job_id, atype, obj.rsplit(".", 1)[0])
    raise ValueError(f"unrecognized object key: {key!r}")


def parse_object_key(full: str) -> ObjectKey:
    """Parse a full 'bucket/key' or bare 'key' string back into an ObjectKey."""
    if full.startswith("moodify/moodify/"):
        full = full[len("moodify/"):]
    try:
        return _parse_key("moodify", full)
    except ValueError:
        pass
    parts = full.split("/", 1)
    if len(parts) == 2:
        try:
            return _parse_key(parts[0], parts[1])
        except ValueError:
            pass
    raise ValueError(f"unrecognized object key: {full!r}")
