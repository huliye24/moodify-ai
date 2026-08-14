#!/usr/bin/env python3
"""Entity reconciliation — MFY_PRODUCTION_DATA_PLANE_001 (task 9).

Compares a source database against a restored/isolated database and asserts
zero drift across the six authoritative entity families plus bridge rows:
  users, creator_profiles, tracks, track_versions, creation_passports,
  evidence_bridge.
Exit 0 = zero drift; 1 = drift found (ids/hashes/counts differ).

Usage: python ops/reconcile_data.py <source.sqlite> <restored.sqlite>
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ENTITY_TABLES = {
    "users": {"id", "display_name", "status"},
    "creator_profiles": {"id", "user_id", "handle"},
    "tracks": {"id", "creator_id", "title", "status", "current_version_id", "approved_evidence_ref"},
    "track_versions": {"id", "track_id", "version_no", "audio_asset_key"},
    "creation_passports": {"id", "track_id", "origin_type"},
    "evidence_bridge": {"id", "request_key", "exchange_status", "publish_safe"},
}


def _snapshot(db_path: Path) -> dict[str, dict]:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    snap: dict[str, dict] = {}
    for table, cols in ENTITY_TABLES.items():
        try:
            rows = con.execute(f"SELECT {', '.join(sorted(cols))} FROM {table}").fetchall()
        except sqlite3.OperationalError:
            snap[table] = {"count": -1, "ids": set(), "rows": []}
            continue
        snap[table] = {
            "count": len(rows),
            "ids": {str(r["id"]) for r in rows if "id" in r.keys()},
            "rows": [tuple(r[c] for c in sorted(cols)) for r in rows],
        }
    con.close()
    return snap


def reconcile(source: Path, restored: Path) -> int:
    src = _snapshot(source)
    dst = _snapshot(restored)
    drift = 0
    print(f"== reconcile {source.name} vs {restored.name} ==")
    for table in ENTITY_TABLES:
        s, d = src[table], dst[table]
        count_ok = s["count"] == d["count"]
        ids_ok = s["ids"] == d["ids"]
        rows_ok = sorted(s["rows"]) == sorted(d["rows"])
        status = "OK" if (count_ok and ids_ok and rows_ok) else "DRIFT"
        if status == "DRIFT":
            drift += 1
        print(f"  {table:20s} src={s['count']:>3} dst={d['count']:>3} "
              f"ids={'OK' if ids_ok else 'DIFF'} rows={'OK' if rows_ok else 'DIFF'}  [{status}]")
    if drift:
        print(f"RESULT: {drift} entity family(ies) drifted — NO_GO per 58")
        return 1
    print("RESULT: zero drift across all entity families")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(reconcile(Path(sys.argv[1]), Path(sys.argv[2])))
