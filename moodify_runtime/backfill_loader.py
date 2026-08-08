"""Historical backfill loader for the multi-night learning store.

Seeds the store from existing nightly summary.json artifacts.
Idempotent: skips run_ids already in the store.
Part of ECHAIN-MOODIFY-MULTI-NIGHT-STORE-016 / MHP-905.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .learning_store import NightRecord, append_night, store_index


def discover_summaries(dirs: list[Path]) -> list[Path]:
    found = []
    for d in dirs:
        if not d.exists():
            continue
        for summary_path in sorted(d.rglob("summary.json")):
            found.append(summary_path)
    return found


def load_summary(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def backfill(store_path: Path, summary_dirs: list[Path]) -> dict[str, Any]:
    store_path.parent.mkdir(parents=True, exist_ok=True)
    existing = store_index(store_path)
    summaries = discover_summaries(summary_dirs)

    stored = 0
    skipped = 0
    errors = 0
    details = []

    for sp in summaries:
        try:
            summary = load_summary(sp)
            run_id = summary.get("run_id", "")
            if not run_id:
                errors += 1
                details.append({"path": str(sp), "error": "missing run_id"})
                continue
            if run_id in existing:
                skipped += 1
                continue
            record = NightRecord.from_summary(summary, provenance_path=str(sp))
            result = append_night(store_path, record)
            if result["status"] == "stored":
                stored += 1
                existing.add(run_id)
            else:
                skipped += 1
        except Exception as exc:
            errors += 1
            details.append({"path": str(sp), "error": str(exc)})

    return {
        "discovered": len(summaries),
        "stored": stored,
        "skipped": skipped,
        "errors": errors,
        "details": details,
        "store_path": str(store_path),
    }
