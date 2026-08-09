#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build",
    ".pytest_cache", ".mypy_cache", ".ruff_cache",
}
TEXT_EXTS = {
    ".md", ".txt", ".py", ".toml", ".yaml", ".yml", ".json", ".ts", ".tsx",
    ".js", ".jsx", ".go", ".rs", ".sh", ".ps1",
}
PATTERNS = {
    "legacy_postprocessing_identity": [
        r"AI.?音乐.*后处理", r"AI.?音乐.*二次处理", r"自动母带",
        r"post-processing system", r"post processing system",
    ],
    "canonical_identity": [r"AI 的耳朵", r"The Ear of AI", r"Auditory Intelligence", r"听觉智能"],
    "auditory_loop": [r"Listen.*Represent.*Judge.*Intervene.*Verify.*Learn"],
    "disciplines": [r"\bWSE\b", r"\bMSE\b", r"\bPPE\b"],
}


def iter_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_EXTS or path.stat().st_size > 2_000_000:
            continue
        yield path


def classify_path(rel: str) -> str:
    value = rel.lower()
    if "moodify-core-package/src/" in value:
        return "core_or_runtime"
    if value.startswith("docs/") or "/docs/" in value:
        return "documentation"
    if "test" in value:
        return "tests"
    if any(token in value for token in ["experiment", "research", "phys", "benchmark", "lab"]):
        return "research_or_experimental"
    if any(token in value for token in ["frontend", "desktop", "electron", "app"]):
        return "application"
    if any(token in value for token in ["legacy", "archive", "histor"]):
        return "legacy_or_historical"
    return "unclassified"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--out", default="artifacts/reconstitution_001/audit")
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    out = root / args.out
    out.mkdir(parents=True, exist_ok=True)

    matches: list[dict[str, object]] = []
    counts: Counter[str] = Counter()
    categories: Counter[str] = Counter()
    for path in iter_text_files(root):
        rel = path.relative_to(root).as_posix()
        categories[classify_path(rel)] += 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        for group, patterns in PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, flags=re.I | re.S):
                    matches.append({
                        "group": group,
                        "path": rel,
                        "line": text.count("\n", 0, match.start()) + 1,
                        "match": text[match.start():match.end()].replace("\n", " ")[:220],
                        "pattern": pattern,
                    })
                    counts[group] += 1

    (out / "positioning_matches.json").write_text(
        json.dumps(matches, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote audit to: {out}")
    print("File categories:", dict(categories))
    print("Positioning counts:", dict(counts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
