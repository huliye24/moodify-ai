"""Strategic mainline registry for Moodify handoff packs.

Append-only JSONL registry tracking handoff packs, gate reports, and reusable
metadata. No coupling to nightly audio data.

Part of ECHAIN-MOODIFY-DEEPSEEK-API-015 / MHP-901.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

DEFAULT_REGISTRY_PATH = Path("reports/aep_worker/mainline_registry.jsonl")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_registry(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def append_registry(path: Path, entry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")


def register_pack(
    registry_path: Path,
    pack_id: str,
    e_chain: str,
    nem: str,
    pack_dir: str,
    task_count: int,
    xclp_scores: Optional[dict[str, float]] = None,
    extra: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "pack_id": pack_id,
        "e_chain": e_chain,
        "nem": nem,
        "pack_dir": pack_dir,
        "task_count": task_count,
        "registered_at": _utc_now_iso(),
        "xclp_scores": xclp_scores or {},
        "extra": extra or {},
    }
    append_registry(registry_path, entry)
    return entry


def register_gate_report(
    registry_path: Path,
    module_name: str,
    e_chain: str,
    L_code: float,
    level: str,
    gate: str,
    passed: bool,
    report_path: str,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "type": "gate_report",
        "module_name": module_name,
        "e_chain": e_chain,
        "L_code": L_code,
        "level": level,
        "gate": gate,
        "passed": passed,
        "report_path": report_path,
        "registered_at": _utc_now_iso(),
    }
    append_registry(registry_path, entry)
    return entry


def list_packs(registry_path: Path) -> list[dict[str, Any]]:
    return [r for r in read_registry(registry_path) if r.get("pack_id")]


def list_gate_reports(registry_path: Path) -> list[dict[str, Any]]:
    return [r for r in read_registry(registry_path) if r.get("type") == "gate_report"]


def latest_pack(registry_path: Path) -> Optional[dict[str, Any]]:
    packs = list_packs(registry_path)
    return packs[-1] if packs else None


def pack_summary(registry_path: Path) -> dict[str, Any]:
    packs = list_packs(registry_path)
    reports = list_gate_reports(registry_path)
    return {
        "total_packs": len(packs),
        "total_gate_reports": len(reports),
        "latest_pack": packs[-1]["pack_id"] if packs else None,
        "latest_pack_at": packs[-1]["registered_at"] if packs else None,
        "registry_path": str(registry_path),
    }
