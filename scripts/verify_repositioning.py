#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED = [
    "README.md",
    "AGENTS.md",
    "moodify-core-package/README.md",
    "docs/AUDITORY_INTELLIGENCE_ARCHITECTURE.md",
    "docs/ASSET_MODEL.md",
    "docs/LEGACY_AND_EXPERIMENTAL_POLICY.md",
    "docs/REPOSITORY_STATUS.md",
]


def must_contain(path: Path, tokens: list[str], errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing: {path}")
        return
    text = path.read_text(encoding="utf-8", errors="ignore")
    for token in tokens:
        if token not in text:
            errors.append(f"{path}: missing token {token!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    root = Path(args.repo).resolve()

    errors: list[str] = []
    for rel in REQUIRED:
        if not (root / rel).exists():
            errors.append(f"missing required file: {rel}")

    must_contain(
        root / "README.md",
        [
            "The Ear of AI",
            "Auditory Intelligence",
            "Listen",
            "Represent",
            "Judge",
            "Intervene",
            "Verify",
            "Learn",
            "WSE",
            "MSE",
            "PPE",
            "Auditory Intervention Laboratory",
        ],
        errors,
    )
    must_contain(
        root / "AGENTS.md",
        ["The Ear of AI", "Production Case", "Evidence Artifact"],
        errors,
    )

    pyproject = root / "moodify-core-package" / "pyproject.toml"
    if not pyproject.exists():
        errors.append("missing pyproject.toml")
    elif "auditory intelligence" not in pyproject.read_text(encoding="utf-8", errors="ignore").lower():
        errors.append("pyproject description does not mention auditory intelligence")

    if errors:
        print("REPOSITIONING VERIFICATION: FAIL")
        for error in errors:
            print(" -", error)
        return 1

    print("REPOSITIONING VERIFICATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
