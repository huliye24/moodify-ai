#!/usr/bin/env python3
from pathlib import Path
import sys, re, json

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
skip = {".git","node_modules","dist","build",".next",".venv","venv","archive","archives","coverage"}
exts = {".py",".ts",".tsx",".js",".jsx",".vue",".svelte",".dart",".swift",".kt",".java",".go",".rs",".json",".yaml",".yml",".md"}

corpus = []
for p in root.rglob("*"):
    if p.is_file() and not any(part in skip for part in p.parts) and p.suffix.lower() in exts:
        try:
            corpus.append(p.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            pass

blob = "\n".join(corpus)
checks = {
    "pairwise_case": [r"PairwiseAuditoryCase", r"pairwise[_ -]?case"],
    "three_way_outcome": [r"A_WINS", r"B_WINS", r"INCONCLUSIVE"],
    "human_override": [r"HumanPairwiseDecision", r"human[_ -]?override", r"override"],
    "preference_record": [r"PreferenceRecord", r"preference[_ -]?record"],
    "evidence": [r"evidence", r"证据"],
    "policy_version": [r"policy[_ -]?version"],
}
coverage = {k: all(re.search(p, blob, re.I) for p in pats) for k, pats in checks.items()}
print(json.dumps({"coverage": coverage, "aligned": all(coverage.values())}, ensure_ascii=False, indent=2))
raise SystemExit(0 if all(coverage.values()) else 3)
