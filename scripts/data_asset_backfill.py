"""DSK-MFY-DATA-ASSET-001 — data-asset backfill.

Walks every registered source location, ingests all parseable structured
outputs into the unified data store at data/data_asset/, and writes the
source->record_id manifest. Idempotent: re-running never duplicates records.

Usage:
    python scripts/data_asset_backfill.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from moodify_runtime.data_asset import DataAssetStore, ingest_sources  # noqa: E402

STORE_ROOT = REPO_ROOT / "data" / "data_asset"


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill the unified job data store")
    parser.add_argument("--dry-run", action="store_true",
                        help="collect and validate without writing")
    args = parser.parse_args()

    if args.dry_run:
        from moodify_runtime.data_asset import SOURCE_REGISTRY, validate_record
        for record_type, relative_dir, pattern, collector in SOURCE_REGISTRY:
            base = REPO_ROOT / relative_dir
            files = sorted(base.glob(pattern)) if base.exists() else []
            valid = invalid = 0
            for source in files:
                try:
                    records = collector(source)
                    if isinstance(records, dict):
                        records = [records]
                    for record in records:
                        if validate_record(record):
                            invalid += 1
                        else:
                            valid += 1
                except Exception:
                    invalid += 1
            print(f"{record_type:>18}: {len(files)} files, {valid} valid records, {invalid} invalid")
        return 0

    store = DataAssetStore(STORE_ROOT)
    stats = ingest_sources(store, REPO_ROOT)
    for record_type, row in stats.items():
        print(f"{record_type:>18}: {row['files']} files, {row['records']} ingested, {row['errors']} errors")
    total = sum(row["records"] for row in stats.values())
    print(f"{'total':>18}: {total} records in {store.records_dir}")
    store_stats = store.stats()
    print(f"store stats: {json.dumps(store_stats, sort_keys=True)}")
    by_type = store_stats["by_type"]
    failed = {k for k, row in stats.items() if row["files"] > 0 and by_type.get(k, 0) == 0}
    if failed:
        print(f"WARNING: source types with files but no records in store: {sorted(failed)}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
