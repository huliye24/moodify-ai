#!/usr/bin/env python3
"""Atomic inbox -> immutable SHA256 source store -> moodify-node enqueue.

This script is intentionally outside the auditory core. It adds operational
provenance and unattended ingestion without changing scan/intervention semantics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_EXTENSIONS = {".wav", ".flac", ".mp3", ".aiff", ".aif", ".m4a", ".ogg"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def connect_ledger(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, timeout=30)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS ingested_sources (
            source_sha256 TEXT PRIMARY KEY,
            original_path TEXT NOT NULL,
            stored_path TEXT NOT NULL,
            job_id TEXT,
            first_seen_at TEXT NOT NULL,
            enqueued_at TEXT,
            size_bytes INTEGER NOT NULL
        )
        """
    )
    return con


def is_old_enough(path: Path, min_age_seconds: int, now: float | None = None) -> bool:
    current = time.time() if now is None else now
    return current - path.stat().st_mtime >= min_age_seconds


def stable_store_path(source_store: Path, sha: str, original_name: str) -> Path:
    return source_store / "sha256" / sha[:2] / sha / original_name


def copy_atomically(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return
    fd, tmp_name = tempfile.mkstemp(prefix=".copy-", dir=str(destination.parent))
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        shutil.copy2(source, tmp)
        os.replace(tmp, destination)
    finally:
        tmp.unlink(missing_ok=True)


def enqueue(node_cli: str, stable_source: Path) -> str:
    proc = subprocess.run(
        [node_cli, "enqueue", str(stable_source)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    job_id = payload.get("job_id")
    if not job_id:
        raise RuntimeError(f"moodify-node enqueue returned no job_id: {proc.stdout!r}")
    return str(job_id)


def ingest_one(
    source: Path,
    source_store: Path,
    ledger_db: Path,
    node_cli: str,
) -> dict:
    sha = sha256_file(source)
    size = source.stat().st_size
    destination = stable_store_path(source_store, sha, source.name)

    with connect_ledger(ledger_db) as con:
        existing = con.execute(
            "SELECT * FROM ingested_sources WHERE source_sha256=?", (sha,)
        ).fetchone()
        if existing:
            return {
                "status": "duplicate",
                "sha256": sha,
                "job_id": existing["job_id"],
                "stored_path": existing["stored_path"],
            }

    copy_atomically(source, destination)

    # Verify the canonical stored copy before enqueue.
    stored_sha = sha256_file(destination)
    if stored_sha != sha:
        raise RuntimeError("stored source hash mismatch")

    job_id = enqueue(node_cli, destination)
    now = utc_now()

    with connect_ledger(ledger_db) as con:
        con.execute(
            """
            INSERT INTO ingested_sources(
                source_sha256, original_path, stored_path, job_id,
                first_seen_at, enqueued_at, size_bytes
            ) VALUES(?,?,?,?,?,?,?)
            """,
            (sha, str(source), str(destination), job_id, now, now, size),
        )

    return {
        "status": "enqueued",
        "sha256": sha,
        "job_id": job_id,
        "stored_path": str(destination),
    }


def scan_inbox(
    inbox: Path,
    source_store: Path,
    ledger_db: Path,
    node_cli: str,
    min_age_seconds: int,
    extensions: set[str],
) -> list[dict]:
    inbox.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    now = time.time()

    for source in sorted(inbox.iterdir()):
        if not source.is_file():
            continue
        if source.name.startswith("."):
            continue
        if source.suffix.lower() not in extensions:
            continue
        if not is_old_enough(source, min_age_seconds, now=now):
            continue
        try:
            results.append(ingest_one(source, source_store, ledger_db, node_cli))
        except Exception as exc:
            results.append({
                "status": "error",
                "source": str(source),
                "error": f"{type(exc).__name__}: {exc}",
            })
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inbox", type=Path, default=Path("/var/lib/moodify/inbox"))
    parser.add_argument("--source-store", type=Path, default=Path("/var/lib/moodify/sources"))
    parser.add_argument("--ledger-db", type=Path, default=Path("/var/lib/moodify/ops/ingest.sqlite3"))
    parser.add_argument("--node-cli", default="/opt/moodify/.venv/bin/moodify-node")
    parser.add_argument("--min-age-seconds", type=int, default=120)
    args = parser.parse_args()

    results = scan_inbox(
        args.inbox,
        args.source_store,
        args.ledger_db,
        args.node_cli,
        args.min_age_seconds,
        DEFAULT_EXTENSIONS,
    )
    print(json.dumps({"timestamp": utc_now(), "results": results}, indent=2))
    return 1 if any(x["status"] == "error" for x in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
