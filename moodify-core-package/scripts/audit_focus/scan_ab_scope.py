#!/usr/bin/env python3
from pathlib import Path
import sys, re, json

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
terms = [
    r"pairwise", r"A/B", r"ab[_ -]?test", r"comparison", r"candidate[_ -]?a",
    r"candidate[_ -]?b", r"winner", r"preference", r"judge", r"judgment",
    r"比较", r"候选", r"裁判", r"胜出", r"偏好"
]
pat = re.compile("|".join(f"(?:{x})" for x in terms), re.I)
skip = {".git","node_modules","dist","build",".next",".venv","venv","archive","archives","coverage"}
exts = {".py",".ts",".tsx",".js",".jsx",".vue",".svelte",".dart",".swift",".kt",".java",".go",".rs",".json",".yaml",".yml",".md",".sql"}

matches = []
for p in root.rglob("*"):
    if not p.is_file() or any(part in skip for part in p.parts) or p.suffix.lower() not in exts:
        continue
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    for i, line in enumerate(text.splitlines(), 1):
        if pat.search(line):
            matches.append({"file": str(p.relative_to(root)), "line": i, "text": line.strip()[:250]})

print(json.dumps({"root": str(root), "count": len(matches), "matches": matches[:1000]}, ensure_ascii=False, indent=2))
