"""Atomic run manifests for safe local resume."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from moodify.auditory.identity import canonical_json


class RunManifest:
    def __init__(self, path: Path, run_id: str, source_sha256: str, plan_version: str):
        self.path = Path(path)
        self.data: dict[str, Any] = {
            "run_id": run_id, "source_sha256": source_sha256,
            "plan_version": plan_version, "status": "PENDING",
            "completed_nodes": [], "failed_node": None, "cache_refs": {},
        }
        if self.path.exists():
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if loaded.get("source_sha256") != source_sha256 or loaded.get("plan_version") != plan_version:
                raise ValueError("run manifest is incompatible with source or plan")
            self.data = loaded

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(self.path.suffix + ".tmp")
        temp.write_text(canonical_json(self.data), encoding="utf-8")
        os.replace(temp, self.path)

    def completed(self, node_id: str, cache_key: str) -> None:
        if node_id not in self.data["completed_nodes"]:
            self.data["completed_nodes"].append(node_id)
        self.data["cache_refs"][node_id] = cache_key
        self.data["status"] = "RUNNING"
        self.data["failed_node"] = None
        self.save()

    def failed(self, node_id: str) -> None:
        self.data["status"] = "FAILED"
        self.data["failed_node"] = node_id
        self.save()

    def finish(self) -> None:
        self.data["status"] = "COMPLETED"
        self.data["failed_node"] = None
        self.save()
