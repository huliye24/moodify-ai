#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

ALLOWED_PREFIXES = (
    "artifacts/pr15_extraction_001/", "scripts/pr15_asset_inventory.py",
    "scripts/verify_pr15_extraction.py", "scripts/pr15_extraction_",
)
REQUIRED_OUTPUTS = [
    "baseline.md", "pr15_file_inventory.csv", "pr15_domain_summary.md",
    "AUDITORY_CORE_EXTRACTION.md", "PRODUCTION_AUTHORITY_MAP.md",
    "EVIDENCE_CONTRACT_MAP.md", "CANONICAL_MINIMUM_CONTRACT.md",
    "LEARNING_MRS_EVIDENCE_REVIEW.md", "ANDROID_ASSET_EXTRACTION.md",
    "RUNTIME_DUPLICATION_MAP.md", "MIGRATION_BACKLOG.md", "PR15_FINAL_DISPOSITION.md",
]


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, encoding="utf-8", errors="replace")
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout


def allowed(path: str) -> bool:
    return any(path == prefix or path.startswith(prefix) for prefix in ALLOWED_PREFIXES)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    errors: list[str] = []
    for name in REQUIRED_OUTPUTS:
        if not (repo / "artifacts/pr15_extraction_001" / name).exists():
            errors.append(f"missing required output: {name}")
    for rel, token in [("README.md", "The Ear of AI"), ("AGENTS.md", "Auditory Intelligence")]:
        path = repo / rel
        if not path.exists() or token not in path.read_text(encoding="utf-8", errors="ignore"):
            errors.append(f"canonical baseline invalid: {rel}")
    changed: set[str] = set()
    for command in [("diff", "--name-only"), ("diff", "--cached", "--name-only"),
                    ("ls-files", "--others", "--exclude-standard")]:
        changed.update(line for line in git(repo, *command).splitlines() if line)
    bad = sorted(path for path in changed if not allowed(path))
    if bad:
        errors.append("non-analysis changes detected:\n  " + "\n  ".join(bad))
    if errors:
        print("PR15 EXTRACTION VERIFICATION: FAIL")
        for error in errors:
            print(" -", error)
        return 1
    print("PR15 EXTRACTION VERIFICATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
