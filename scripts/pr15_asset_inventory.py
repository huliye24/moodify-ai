#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import re
import subprocess

DOMAIN_RULES = [
    ("APPLICATION_ANDROID", r"^apps/android/"),
    ("AUDITORY_CORE", r"^moodify-core-package/src/moodify/auditory/"),
    ("MSE", r"^moodify-core-package/src/moodify/(score_engine|transcription|transcription_pipeline|lyric_align)/"),
    ("WSE", r"^moodify-core-package/src/moodify/(features|perception)/"),
    ("PPE_RUNTIME", r"^moodify-core-package/src/moodify/(app|domain|cli_v2)/"),
    ("EVIDENCE_ASSET", r"^moodify-bridge/"),
    ("LEARNING", r"^moodify-core-package/src/moodify/learning/"),
    ("PPE_RUNTIME", r"^moodify_runtime/"),
    ("CLOUD", r"^(workers|night|deploy)/"),
    ("RESEARCH_EXPERIMENTAL", r"^(science|phys-lab|docs/experiments)/"),
    ("GENERATED_ARTIFACT", r"^(outputs|reports|artifacts)/"),
    ("TOOLING", r"^(scripts|tools)/"),
    ("TESTS", r"(^tests/|/tests/)"),
    ("DOCUMENTATION_HISTORY", r"^docs/"),
    ("APPLICATION_API", r"^moodify-core-package/src/moodify/api/"),
]


def run(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", errors="replace",
    ).stdout


def classify(path: str) -> str:
    for domain, pattern in DOMAIN_RULES:
        if re.search(pattern, path):
            return domain
    return "UNKNOWN"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--base", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    out = (repo / args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    rows = []
    counts: Counter[str] = Counter()
    for raw in run(repo, "diff", "--name-status", f"{args.base}...{args.source}").splitlines():
        parts = raw.split("\t")
        if len(parts) < 2:
            continue
        path = parts[-1]
        domain = classify(path)
        rows.append({
            "status": parts[0], "path": path, "domain_first_pass": domain,
            "action_first_pass": "REVIEW", "manual_action": "",
            "canonical_target": "", "evidence_tests": "", "notes": "",
        })
        counts[domain] += 1

    with (out / "pr15_file_inventory.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    summary = [
        "# PR #15 Domain Summary", "", f"Base: `{args.base}`", f"Source: `{args.source}`",
        f"Changed paths inventoried: {len(rows)}", "", "## Automated First-Pass Counts", "",
    ]
    summary.extend(f"- {domain}: {count}" for domain, count in counts.most_common())
    summary.extend(["", "> Automated classification is not an architectural decision."])
    (out / "pr15_domain_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    (out / "inventory_meta.json").write_text(json.dumps({
        "base": args.base, "source": args.source, "changed_paths": len(rows),
        "domain_counts": dict(counts),
    }, indent=2), encoding="utf-8")
    print(f"Inventoried {len(rows)} changed paths")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
