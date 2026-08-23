#!/usr/bin/env python3
"""
Local-only validator for W01-P03 object manifests.
No network calls. No database writes. No OSS writes.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")

REQUIRED = {
    "object_id","track_id","artifact_type","bucket","object_key",
    "content_hash","hash_algorithm","byte_size","created_at","producer"
}

ALLOWED_TYPES = {"source","stem","analysis","intermediate","render","evidence","report","other"}

def validate(data: dict) -> list[str]:
    errors = []
    missing = sorted(REQUIRED - data.keys())
    if missing:
        errors.append(f"missing required fields: {missing}")
    if data.get("hash_algorithm") != "sha256":
        errors.append("hash_algorithm must be sha256")
    h = data.get("content_hash","")
    if not HEX64.match(h):
        errors.append("content_hash must be 64 hex chars")
    if data.get("artifact_type") not in ALLOWED_TYPES:
        errors.append(f"artifact_type must be one of {sorted(ALLOWED_TYPES)}")
    if not isinstance(data.get("byte_size"), int) or data.get("byte_size", -1) < 0:
        errors.append("byte_size must be a non-negative integer")
    key = str(data.get("object_key",""))
    if key.startswith("/") or "\\" in key:
        errors.append("object_key must be relative and use '/' separators")
    if ".." in key.split("/"):
        errors.append("object_key may not contain '..' path segments")
    return errors

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    args = ap.parse_args()
    path = Path(args.manifest)
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1
    print("OK: manifest passes local W01-P03 checks")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
