#!/usr/bin/env python3
"""
Validate basic W01-P09 distillation register CSV semantics.
Local-only.
"""
from __future__ import annotations
import argparse, csv
from pathlib import Path

LEVELS = {"D0","D1","D2","D3","D4","D5","D6","D7"}
DECISIONS = {
    "KEEP","REWRITE","DOWNGRADE","MERGE","DELETE_CANDIDATE",
    "AUTOMATE","HARDEN","HUMAN_DECISION_REQUIRED"
}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    args = ap.parse_args()

    rows = list(csv.DictReader(Path(args.csv_path).open(encoding="utf-8-sig")))
    errors = []
    ids = set()
    for i, r in enumerate(rows, start=2):
        did = r.get("distillation_id","").strip()
        if not did:
            errors.append(f"line {i}: missing distillation_id")
        if did in ids:
            errors.append(f"line {i}: duplicate id {did}")
        ids.add(did)
        if r.get("current_level","").strip() not in LEVELS:
            errors.append(f"line {i}: invalid current_level")
        if r.get("proposed_level","").strip() not in LEVELS:
            errors.append(f"line {i}: invalid proposed_level")
        if r.get("decision","").strip() not in DECISIONS:
            errors.append(f"line {i}: invalid decision")
        if not r.get("source_evidence","").strip():
            errors.append(f"line {i}: missing source evidence")
        if not r.get("future_cost_eliminated","").strip():
            errors.append(f"line {i}: missing future cognitive cost eliminated")
    if errors:
        for e in errors:
            print("ERROR:", e)
        return 1
    print(f"OK: {len(rows)} distillation units passed basic checks")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
