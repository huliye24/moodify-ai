#!/usr/bin/env python3
"""Generate or verify deterministic JSON Schemas for canonical contracts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_SRC = ROOT / "moodify-core-package" / "src"
sys.path.insert(0, str(CORE_SRC))


def load_models():
    from moodify.contracts import EvidenceArtifact, MachineFinding, MeasurementRecord, ProductionCase, Rule

    return {
        "production_case.v1.schema.json": ProductionCase,
        "measurement_record.v1.schema.json": MeasurementRecord,
        "evidence_artifact.v1.schema.json": EvidenceArtifact,
        "rule.v1.schema.json": Rule,
        "machine_finding.v1.schema.json": MachineFinding,
    }


def normalized_schema(model) -> str:
    return json.dumps(
        model.model_json_schema(),
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
    ) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "schemas" / "canonical")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    failures = []
    for filename, model in load_models().items():
        expected = normalized_schema(model)
        path = args.out / filename
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                failures.append(path)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)}")

    if failures:
        print("schema mismatch:")
        for path in failures:
            print(f" - {path}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
