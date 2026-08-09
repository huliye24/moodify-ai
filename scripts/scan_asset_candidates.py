#!/usr/bin/env python3
"""Asset candidate scanner (DSK-RJWC-ASSET-REGISTRY-001).

Aggregates the repository into directory-level candidate groups with
heuristic class hints, writing asset-registry/evidence/candidates.json.
The registry records themselves are knowledge-driven and reviewed by
hand; this scanner only confirms locations exist and surfaces candidate
groups for future registration.
Usage: python scripts/scan_asset_candidates.py [repo_root]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SKIP_PARTS = {
    ".git", "node_modules", ".venv", ".venv-basic-pitch", "venv", "dist", "build",
    ".next", "coverage", "__pycache__", "asset-registry", ".claude", ".cursor",
    ".gradle", ".kotlin", ".idea", "build", "libs", ".codex-work",
}
TOP_LEVELS = ("apps", "docs", "moodify-core-package", "moodify_runtime", "schemas",
              "scripts", "tools", "artifacts", "configs", "tests")

CLASS_HINTS = {
    "DATA": ("outputs", "data", "corpus", "treatment_records", "golden"),
    "KNOWLEDGE": ("docs", "knowledge", "standards", "policies"),
    "REPRESENTATION": ("contracts", "schemas", "profiles"),
    "MODEL": ("models", "checkpoints", "weights"),
    "PRODUCTION_SYSTEM": ("runtime", "queue", "access", "evaluation", "orchestration"),
    "SOFTWARE": ("apps", "src", "api", "cli", "tools", "scripts"),
    "INFRASTRUCTURE_RESOURCE": ("deploy", "cloud", "infra"),
}


def classify(path: Path) -> str:
    lowered = str(path).lower()
    for hint_class, hints in CLASS_HINTS.items():
        if any(hint in lowered for hint in hints):
            return hint_class
    return "UNKNOWN"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    candidates: list[dict] = []
    seen: set[Path] = set()

    for level in TOP_LEVELS:
        for top in (root / level).iterdir() if (root / level).is_dir() else []:
            if not top.is_dir() or any(part in SKIP_PARTS for part in top.parts):
                continue
            if top in seen:
                continue
            seen.add(top)
            file_count = sum(1 for _ in top.rglob("*") if _.is_file() and not any(
                part in SKIP_PARTS for part in _.parts))
            candidates.append({
                "path": str(top.relative_to(root)).replace("\\", "/"),
                "class_hint": classify(top),
                "file_count": file_count,
            })

    evidence_dir = root / "asset-registry" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "scanner": "scan_asset_candidates.py",
        "candidate_count": len(candidates),
        "candidates": sorted(candidates, key=lambda c: c["path"]),
    }
    (evidence_dir / "candidates.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"ok": True, "candidate_count": len(candidates),
                      "output": "asset-registry/evidence/candidates.json"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
