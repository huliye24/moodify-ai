#!/usr/bin/env python3
"""
Validate that Wave 02 candidate set contains no more than three candidates.
Local-only.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("json_file")
    args = ap.parse_args()
    data = json.loads(Path(args.json_file).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        print("ERROR: expected JSON list")
        return 1
    if len(data) > 3:
        print("ERROR: Wave 02 may contain at most 3 candidates")
        return 1
    for i, item in enumerate(data, 1):
        for field in ("candidate_id","problem","evidence","user_impact","main_river_impact","stop_condition"):
            if field not in item or item[field] in ("", [], None):
                print(f"ERROR: candidate {i} missing {field}")
                return 1
    print(f"OK: {len(data)} Wave 02 candidate(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
