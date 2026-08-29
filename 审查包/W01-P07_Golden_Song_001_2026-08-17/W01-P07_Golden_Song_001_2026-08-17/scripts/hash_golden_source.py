#!/usr/bin/env python3
"""
Compute SHA-256 and basic file size for the human-selected Golden Song source.
Local-only; does not upload or modify the audio.
"""
from __future__ import annotations
import argparse, hashlib
from pathlib import Path

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("audio_file")
    args = ap.parse_args()
    p = Path(args.audio_file)
    if not p.is_file():
        print("ERROR: file not found")
        return 1
    print(f"path={p}")
    print(f"bytes={p.stat().st_size}")
    print(f"sha256={sha256_file(p)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
