#!/usr/bin/env python3
"""Orphan media audit for Moodify Music.

Server authority: PolarDB references (via LA BFF /api/v1/music/media/references).
Media root: LA /opt/moodify/music-media/audio.

Default is DRY-RUN. --apply deletes candidates one-by-one with exact paths
and records each deletion as an audit event. Never recursive, never glob-wide.

Usage:
  python3 media_audit.py                          # dry-run
  python3 media_audit.py --apply                  # delete + audit
  python3 media_audit.py --retention-days 14 --root /opt/moodify/music-media/audio
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request

DEFAULT_ROOT = "/opt/moodify/music-media/audio"
DEFAULT_API = "https://rongjinwenchuan.xyz/api/v1/music"


def fetch_references(api: str) -> set[str]:
    url = f"{api}/media/references"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return set(data.get("references") or [])


def scan_root(root: str) -> list[tuple[str, str, float]]:
    """Return every media object using its root-relative canonical asset key."""
    found: list[tuple[str, str, float]] = []
    allowed_extensions = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac"}
    root = os.path.realpath(root)
    for directory, subdirectories, names in os.walk(root, followlinks=False):
        subdirectories[:] = [name for name in subdirectories if not name.startswith(".")]
        for name in names:
            if name.startswith(".") or os.path.splitext(name)[1].lower() not in allowed_extensions:
                continue
            path = os.path.join(directory, name)
            if os.path.islink(path) or not os.path.isfile(path):
                continue
            asset_key = os.path.relpath(path, root).replace(os.sep, "/")
            found.append((asset_key, path, os.path.getmtime(path)))
    return found


def record_audit(api: str, action: str, resource_id: str, metadata: dict) -> None:
    url = f"{api}/audit-events"
    body = json.dumps({
        "actor_type": "system",
        "action": action,
        "resource_type": "media",
        "resource_id": resource_id,
        "metadata": metadata,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30):
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=DEFAULT_ROOT)
    parser.add_argument("--api", default=DEFAULT_API)
    parser.add_argument("--retention-days", type=int, default=7)
    parser.add_argument("--apply", action="store_true", help="actually delete candidates")
    args = parser.parse_args()

    if not os.path.isdir(args.root):
        print(f"media root not found: {args.root}", file=sys.stderr)
        return 2

    references = fetch_references(args.api)
    print(f"referenced media keys: {len(references)}")

    now = time.time()
    retention = args.retention_days * 86400
    candidates: list[tuple[str, str]] = []
    for asset_key, path, mtime in scan_root(args.root):
        if asset_key in references:
            continue
        if now - mtime < retention:
            print(f"  kept (within retention): {asset_key}")
            continue
        candidates.append((asset_key, path))

    if not candidates:
        print("no orphan candidates")
        record_audit(args.api, "media.audit_dry_run", "all", {"candidates": 0})
        return 0

    print(f"\ncandidates ({'APPLY' if args.apply else 'DRY-RUN'}): {len(candidates)}")
    for asset_key, path in candidates:
        print(f"  {asset_key}  {path}")
        record_audit(args.api, "media.audit_dry_run", asset_key, {"candidate": True})
        if args.apply:
            os.remove(path)  # exact single-file removal, never recursive
            record_audit(args.api, "media.audit_applied", asset_key, {"deleted": True})
            print(f"    -> deleted + audited")

    return 0


if __name__ == "__main__":
    sys.exit(main())
