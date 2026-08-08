"""Multi-night learning store for Moodify nightly evidence.

Append-only JSONL store with stable schema, duplicate detection, and
provenance tracking. Part of ECHAIN-MOODIFY-MULTI-NIGHT-STORE-016 / MHP-904.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

STORE_DEFAULT_PATH = "data/moodify_runtime/multi_night_store.jsonl"


@dataclass
class NightRecord:
    run_id: str
    started_at: str
    night_label: str = ""
    input_dir: str = ""
    selected_count: int = 0
    success_count: int = 0
    failed_count: int = 0
    avg_eds: Optional[float] = None
    avg_elapsed_s: Optional[float] = None
    emotion: str = ""
    provenance_path: str = ""
    extra: dict[str, Any] = field(default_factory=dict)
    stored_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "NightRecord":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in d.items() if k in valid}
        return cls(**filtered)

    @classmethod
    def from_summary(cls, summary: dict[str, Any], provenance_path: str = "") -> "NightRecord":
        records = summary.get("records", [])
        successes = [r for r in records if r.get("success")]
        eds_vals = [r["eds"] for r in successes if "eds" in r]
        elapsed_vals = [r["elapsed_s"] for r in successes if "elapsed_s" in r]

        return cls(
            run_id=summary.get("run_id", ""),
            started_at=summary.get("started_at", ""),
            night_label=_derive_night_label(summary.get("started_at", "")),
            input_dir=summary.get("input_dir", ""),
            selected_count=summary.get("selected_count", 0),
            success_count=summary.get("success", 0),
            failed_count=summary.get("failed", 0),
            avg_eds=round(sum(eds_vals) / len(eds_vals), 2) if eds_vals else None,
            avg_elapsed_s=round(sum(elapsed_vals) / len(elapsed_vals), 2) if elapsed_vals else None,
            emotion=summary.get("emotion", ""),
            provenance_path=provenance_path,
            stored_at=_utc_now_iso(),
        )


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _derive_night_label(started_at: str) -> str:
    if not started_at:
        return ""
    try:
        for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S+08:00"):
            try:
                dt = datetime.strptime(started_at, fmt)
                break
            except ValueError:
                continue
        else:
            return started_at[:10]
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return started_at[:10] if len(started_at) >= 10 else started_at


def read_store(path: Path) -> list[dict[str, Any]]:
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


def store_index(path: Path) -> set[str]:
    return {r["run_id"] for r in read_store(path) if "run_id" in r}


def append_night(path: Path, record: NightRecord) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = store_index(path)
    d = record.to_dict()
    if d["run_id"] in existing:
        return {"status": "skipped", "run_id": d["run_id"], "reason": "duplicate"}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, sort_keys=True) + "\n")
    return {"status": "stored", "run_id": d["run_id"]}


def load_store(path: Path) -> list[NightRecord]:
    return [NightRecord.from_dict(r) for r in read_store(path)]


def store_summary(path: Path) -> dict[str, Any]:
    rows = read_store(path)
    if not rows:
        return {"total_nights": 0, "earliest": None, "latest": None, "store_path": str(path)}
    run_ids = [r["run_id"] for r in rows if "run_id" in r]
    nights = sorted(r.get("night_label", "") for r in rows if r.get("night_label"))
    return {
        "total_nights": len(rows),
        "earliest": nights[0] if nights else None,
        "latest": nights[-1] if nights else None,
        "run_ids": run_ids,
        "store_path": str(path),
    }
