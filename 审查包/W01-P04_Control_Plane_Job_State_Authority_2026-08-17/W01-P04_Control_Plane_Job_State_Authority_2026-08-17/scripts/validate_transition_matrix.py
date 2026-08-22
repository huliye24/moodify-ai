#!/usr/bin/env python3
"""
Pure local transition-matrix sanity checker for W01-P04.
No network, DB, or filesystem mutation beyond reading the CSV.
"""
from __future__ import annotations
import argparse, csv
from pathlib import Path

TERMINAL = {"READY","FAILED","CANCELED"}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    args = ap.parse_args()
    rows = list(csv.DictReader(Path(args.csv_path).open(encoding="utf-8-sig")))
    errors = []
    seen = set()
    for i, r in enumerate(rows, start=2):
        tid = r.get("transition_id","").strip()
        if not tid:
            errors.append(f"line {i}: missing transition_id")
        if tid in seen:
            errors.append(f"line {i}: duplicate transition_id {tid}")
        seen.add(tid)
        f = r.get("from_state","").strip()
        t = r.get("to_state","").strip()
        cmd = r.get("command","").strip()
        if not f or not t or not cmd:
            errors.append(f"line {i}: from_state/to_state/command required")
        if f in TERMINAL and t != f:
            errors.append(f"line {i}: terminal transition {f}->{t} requires explicit replay/reset policy, not ordinary matrix")
    if errors:
        for e in errors:
            print("ERROR:", e)
        return 1
    print(f"OK: {len(rows)} transitions passed basic W01-P04 checks")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
