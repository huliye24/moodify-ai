#!/usr/bin/env python3
"""Create a compact daily metadata backup without duplicating heavy audio assets."""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import tarfile
from datetime import datetime
from pathlib import Path

ALLOWED_SUFFIXES = {
    ".json", ".jsonl", ".md", ".txt", ".yaml", ".yml", ".toml", ".csv"
}


def sqlite_backup(source: Path, destination: Path) -> bool:
    if not source.exists():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    src = sqlite3.connect(source)
    dst = sqlite3.connect(destination)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    return True


def add_metadata_tree(tar: tarfile.TarFile, root: Path, arc_prefix: str) -> int:
    count = 0
    if not root.exists():
        return count
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            continue
        rel = path.relative_to(root)
        tar.add(path, arcname=str(Path(arc_prefix) / rel), recursive=False)
        count += 1
    return count


def prune_old(root: Path, keep: int) -> None:
    dirs = sorted([p for p in root.iterdir() if p.is_dir()], reverse=True) if root.exists() else []
    for old in dirs[keep:]:
        shutil.rmtree(old)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-db", type=Path, default=Path("/var/lib/moodify/node.sqlite3"))
    parser.add_argument("--ingest-db", type=Path, default=Path("/var/lib/moodify/ops/ingest.sqlite3"))
    parser.add_argument("--cases-root", type=Path, default=Path("/var/lib/moodify/data_factory"))
    parser.add_argument("--reports-root", type=Path, default=Path("/var/lib/moodify/reports"))
    parser.add_argument("--backup-root", type=Path, default=Path("/var/backups/moodify"))
    parser.add_argument("--keep", type=int, default=7)
    args = parser.parse_args()

    stamp = datetime.now().strftime("%Y-%m-%d")
    dest = args.backup_root / stamp
    dest.mkdir(parents=True, exist_ok=True)

    db_dir = dest / "db"
    node_ok = sqlite_backup(args.state_db, db_dir / "node.sqlite3")
    ingest_ok = sqlite_backup(args.ingest_db, db_dir / "ingest.sqlite3")

    archive = dest / "metadata.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        case_count = add_metadata_tree(tar, args.cases_root, "data_factory")
        report_count = add_metadata_tree(tar, args.reports_root, "reports")

    manifest = {
        "created_at": datetime.now().astimezone().isoformat(),
        "node_db_backed_up": node_ok,
        "ingest_db_backed_up": ingest_ok,
        "metadata_archive": str(archive),
        "case_metadata_files": case_count,
        "report_metadata_files": report_count,
        "excluded_heavy_suffixes": [".wav", ".flac", ".mp3", ".png", ".npz"],
        "retention_sets": args.keep,
    }
    (dest / "backup_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )

    prune_old(args.backup_root, args.keep)
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
