#!/usr/bin/env python3
"""Validate the 10-song pilot manifest before unattended production."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def duration_seconds(path: Path) -> float | None:
    try:
        p = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(path)
            ],
            check=True, capture_output=True, text=True, timeout=30
        )
        return float(p.stdout.strip())
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()

    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    songs = payload.get("songs", [])
    errors = []
    if len(songs) != 10:
        errors.append(f"manifest must contain exactly 10 songs; got {len(songs)}")

    result = []
    for i, song in enumerate(songs, start=1):
        p = Path(song.get("path", ""))
        rights = bool(song.get("rights_ok"))
        if not rights:
            errors.append(f"song {i}: rights_ok must be true")
        if not p.is_file():
            errors.append(f"song {i}: file not found: {p}")
            dur = None
        else:
            dur = duration_seconds(p)
        result.append({
            "index": i,
            "path": str(p),
            "rights_ok": rights,
            "duration_seconds": dur,
            "full_length_signal": bool(dur and dur >= 120),
        })

    print(json.dumps({"songs": result, "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
