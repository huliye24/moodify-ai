#!/usr/bin/env python3
"""
Aggregate basic descriptive metrics from W01-P08 CASE_VERDICTS.csv.
Local-only. No network/cloud writes.
"""
from __future__ import annotations
import argparse, csv, collections
from pathlib import Path

def truthy(v: str) -> bool:
    return v.strip().lower() in {"1","true","yes","y"}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("case_verdicts_csv")
    args = ap.parse_args()
    rows = list(csv.DictReader(Path(args.case_verdicts_csv).open(encoding="utf-8-sig")))
    print(f"cases={len(rows)}")
    eng = collections.Counter(r.get("engineering_verdict","") for r in rows)
    listen = collections.Counter(r.get("listening_verdict","") for r in rows)
    first = sum(truthy(r.get("first_pass_acceptance","")) for r in rows)
    playback = sum(r.get("playback","").strip().upper() in {"PASS","TRUE","YES"} for r in rows)
    trace = collections.Counter(r.get("traceability","") for r in rows)
    print("engineering=", dict(eng))
    print("listening=", dict(listen))
    print(f"first_pass_acceptance={first}/{len(rows) if rows else 0}")
    print(f"playback_pass={playback}/{len(rows) if rows else 0}")
    print("traceability=", dict(trace))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
