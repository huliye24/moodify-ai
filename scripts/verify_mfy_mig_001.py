#!/usr/bin/env python3
"""Verify the structural and research boundaries of MFY-MIG-001."""

from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED = [
    "moodify-core-package/src/moodify/contracts/__init__.py",
    "moodify-core-package/src/moodify/contracts/base.py",
    "moodify-core-package/src/moodify/contracts/ids.py",
    "moodify-core-package/src/moodify/contracts/hashing.py",
    "moodify-core-package/src/moodify/contracts/provenance.py",
    "moodify-core-package/src/moodify/contracts/production_case.py",
    "moodify-core-package/src/moodify/contracts/measurement_record.py",
    "moodify-core-package/src/moodify/contracts/evidence_artifact.py",
    "moodify-core-package/src/moodify/contracts/rule.py",
    "moodify-core-package/src/moodify/contracts/serialization.py",
    "schemas/canonical/production_case.v1.schema.json",
    "schemas/canonical/measurement_record.v1.schema.json",
    "schemas/canonical/evidence_artifact.v1.schema.json",
    "schemas/canonical/rule.v1.schema.json",
    "docs/contracts/CANONICAL_MINIMUM_CONTRACTS_V1.md",
    "artifacts/mfy_mig_001/baseline.md",
    "artifacts/mfy_mig_001/test_results.md",
    "artifacts/mfy_mig_001/contract_decisions.md",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    errors = [f"missing: {rel}" for rel in REQUIRED if not (root / rel).exists()]

    readme = root / "README.md"
    if not readme.exists() or "The Ear of AI" not in readme.read_text(
        encoding="utf-8", errors="ignore"
    ):
        errors.append("canonical README identity missing")

    contracts_dir = root / "moodify-core-package" / "src" / "moodify" / "contracts"
    if contracts_dir.exists():
        source = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore").lower()
            for path in contracts_dir.rglob("*.py")
        )
        if "b_matrix" in source or "b-matrix" in source:
            errors.append("B-matrix leaked into canonical v1 contract package")
        for prohibited in ("moodify_runtime", "apps.android", "moodify.learning"):
            if prohibited in source:
                errors.append(f"prohibited dependency leaked into contracts: {prohibited}")

    if errors:
        print("MFY-MIG-001 VERIFICATION: FAIL")
        for error in errors:
            print(f" - {error}")
        return 1

    print("MFY-MIG-001 VERIFICATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
