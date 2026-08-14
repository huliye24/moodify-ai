#!/usr/bin/env python3
"""Evidence ledger auto-verifier — MFY_RELEASE_TRUTH_RECONCILIATION_001.

Every claim in the Evidence Index must resolve to a real commit and real
files. "找不到证据的声称视为未完成" (55 package). This script is the
machine check behind that rule: it parses EVIDENCE_INDEX.md, verifies each
commit hash against git, and verifies each referenced file exists on disk.

Usage: python ops/verify_evidence.py [--index artifacts/phase1_launch/EVIDENCE_INDEX.md]
Exit: 0 = all claims verified; 1 = missing claims found.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# commit claims live in ledger table cells, either as a single `| <hash> |`
# or a comma list `| h1, h2, ... |` — full-text hex would catch manifest
# sha256 prefixes and date stamps as false positives.
HEX_RE = re.compile(r"\|\s*([0-9a-f]{7,12}(?:\s*,\s*[0-9a-f]{7,12})*)\s*\|")
# file claims: backticked paths anywhere, or bare paths rooted in known
# repository directories (avoids matching prose words and table separators)
PATH_RE = re.compile(
    r"`([^`]+\.(?:md|py|tsx?|mjs|css|json|yaml|yml|kt|sh|html|png|svg|xml|txt|wav))`"
    r"|(?<![A-Za-z0-9/])((?:artifacts|docs|apps|ops|schemas)/[A-Za-z0-9_./-]+\.(?:md|py|tsx?|mjs|css|json|yaml|yml|kt|sh|html|png|svg|xml|txt|wav))",
)


def git_has(short_hash: str) -> bool:
    """Verify the hash resolves in git history (any ref)."""
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{short_hash}^{{commit}}"],
        cwd=ROOT, capture_output=True, text=True,
    )
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default="artifacts/phase1_launch/EVIDENCE_INDEX.md")
    args = parser.parse_args()
    index_path = ROOT / args.index
    if not index_path.is_file():
        print(f"FATAL: evidence index not found: {index_path}")
        return 2

    text = index_path.read_text(encoding="utf-8")
    commits = sorted({h for cell in HEX_RE.findall(text) for h in re.split(r"\s*,\s*", cell)})
    files = sorted({m.group(1) or m.group(2) for m in PATH_RE.finditer(text)})

    print(f"== Evidence ledger check: {index_path.relative_to(ROOT)} ==")
    print(f"claims parsed: {len(commits)} commits, {len(files)} file references")

    missing_commits = []
    for commit in commits:
        if not git_has(commit):
            missing_commits.append(commit)

    missing_files = []
    for ref in files:
        candidates = [
            ROOT / ref,
            *[ROOT / ref if not ref.startswith(("/", "..")) else None],
        ]
        candidates = [c for c in candidates if c is not None]
        if not any(c.is_file() for c in candidates):
            missing_files.append(ref)

    verified = len(commits) - len(missing_commits) + len(files) - len(missing_files)
    total = len(commits) + len(files)
    print(f"verified: {verified}/{total}")

    if missing_commits:
        print("\nMISSING COMMITS (hash not resolvable in git):")
        for c in missing_commits:
            print(f"  {c}")
    if missing_files:
        print("\nMISSING FILES (referenced but not on disk):")
        for f in missing_files:
            print(f"  {f}")

    if missing_commits or missing_files:
        print("\nRESULT: MISSING CLAIMS — 55 规则：找不到证据的声称视为未完成")
        return 1
    print("\nRESULT: ALL CLAIMS VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
