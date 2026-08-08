from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable
import hashlib
import json
import subprocess


DEFAULT_UPSTREAM_PATHS = (
    "ocean.py",
    "modules/classifier.py",
    "modules/dynamics.py",
    "modules/harmonic_filter.py",
    "modules/per_stem_notes.py",
    "modules/structure.py",
    "modules/stems.py",
    "modules/voice.py",
    "modules/report.py",
    "requirements.txt",
    "requirements-deep.txt",
    "LICENSE",
    "NOTICES",
)


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def git_head(repo_root: str | Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


def capture_module_manifest(
    repo_root: str | Path,
    relative_paths: Iterable[str] = DEFAULT_UPSTREAM_PATHS,
) -> dict[str, Any]:
    root = Path(repo_root)
    files: list[dict[str, Any]] = []
    for relative in relative_paths:
        path = root / relative
        if path.is_file():
            files.append(
                {
                    "path": relative.replace("\\", "/"),
                    "sha256": sha256_file(path),
                    "size_bytes": path.stat().st_size,
                }
            )
    return {
        "git_commit": git_head(root),
        "files": files,
        "manifest_sha256": canonical_json_hash(files),
    }
