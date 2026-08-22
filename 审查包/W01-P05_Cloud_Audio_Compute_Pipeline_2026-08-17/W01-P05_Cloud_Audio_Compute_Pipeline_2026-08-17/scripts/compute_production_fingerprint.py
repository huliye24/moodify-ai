#!/usr/bin/env python3
"""
Compute a deterministic SHA-256 production fingerprint from a JSON document.
Local-only. No network or cloud writes.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def canonical_bytes(obj) -> bytes:
    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":")
    ).encode("utf-8")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("json_file")
    args = ap.parse_args()
    data = json.loads(Path(args.json_file).read_text(encoding="utf-8"))
    print(hashlib.sha256(canonical_bytes(data)).hexdigest())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
