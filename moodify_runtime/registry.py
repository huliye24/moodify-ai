from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import RuntimeConfig
from .utils import append_jsonl, discover_audio_files, read_jsonl, stable_sample_id, utc_now_iso


def load_registry(cfg: RuntimeConfig) -> List[Dict[str, Any]]:
    return read_jsonl(cfg.registry_path)


def registry_index(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {r["sample_id"]: r for r in rows if "sample_id" in r}


def register_inputs(
    cfg: RuntimeConfig,
    source: str = "unknown",
    genre: str = "",
    vocal_type: str = "",
    notes: str = "",
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    cfg = cfg.resolved()
    existing = registry_index(load_registry(cfg))
    files = discover_audio_files(cfg.input_dirs, cfg.audio_suffixes, cfg.recurse, cfg.max_files)

    added = 0
    skipped = 0
    entries = []
    for path in files:
        sample_id = stable_sample_id(path)
        if sample_id in existing:
            skipped += 1
            continue
        entry: Dict[str, Any] = {
            "sample_id": sample_id,
            "path": str(path),
            "filename": path.name,
            "source": source,
            "genre": genre,
            "vocal_type": vocal_type,
            "notes": notes,
            "size_bytes": path.stat().st_size,
            "suffix": path.suffix.lower(),
            "registered_at": utc_now_iso(),
            "status": "active",
            "tags": [],
            "extra": extra or {},
        }
        append_jsonl(cfg.registry_path, entry)
        entries.append(entry)
        added += 1

    return {
        "registry_path": str(cfg.registry_path),
        "discovered": len(files),
        "added": added,
        "skipped_existing": skipped,
        "entries": entries,
    }


def find_sample(cfg: RuntimeConfig, sample_id: str) -> Optional[Dict[str, Any]]:
    rows = load_registry(cfg)
    for row in rows:
        if row.get("sample_id") == sample_id:
            return row
    return None
