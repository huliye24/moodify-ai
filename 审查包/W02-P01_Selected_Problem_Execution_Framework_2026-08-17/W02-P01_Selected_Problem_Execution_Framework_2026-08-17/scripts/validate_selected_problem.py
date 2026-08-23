#!/usr/bin/env python3
"""
Validate a W02-P01 selected problem JSON.
Local-only.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

TECH_NOUNS = {"redis","gpu","ios","hardware","kubernetes","kafka","database","model"}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("json_file")
    args = ap.parse_args()
    data = json.loads(Path(args.json_file).read_text(encoding="utf-8"))

    required = ["problem_id","problem_statement","evidence","baseline_metric","success_criteria","stop_conditions","non_goals"]
    for f in required:
        if f not in data or data[f] in ("", [], None):
            print(f"ERROR: missing {f}")
            return 1

    statement = data["problem_statement"].strip().lower()
    if statement in TECH_NOUNS:
        print("ERROR: problem_statement is only a technology noun")
        return 1

    if data.get("requires_canon_change") or data.get("requires_authority_change"):
        print("WARN: human re-approval required before execution")

    print("OK: selected problem contract passed basic validation")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
