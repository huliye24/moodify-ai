"""Validate a Moodify Workspace v2 acceptance-sample manifest.

Usage:
    python scripts/validate_workspace_acceptance_sample.py \
        data/workspace_v2/acceptance_samples/WSA_20260724_001.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def validate_manifest(manifest_path: Path) -> list[str]:
    errors: list[str] = []
    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    required = {
        "schema_version",
        "sample_id",
        "purpose",
        "source",
        "creative_brief_seed",
        "baseline",
        "workspace_v2_expected_results",
        "acceptance_gates",
    }
    missing = sorted(required.difference(data))
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")

    stems = data.get("source", {}).get("stems", [])
    if len(stems) != 2:
        errors.append(f"expected exactly 2 source stems, found {len(stems)}")

    roles = {stem.get("role") for stem in stems}
    if roles != {"instrumental", "vocals"}:
        errors.append(f"expected instrumental/vocals roles, found {sorted(roles)}")

    for stem in stems:
        relative_path = stem.get("path", "")
        path = PROJECT_ROOT / relative_path
        label = stem.get("role", relative_path)
        if not path.is_file():
            errors.append(f"{label}: file not found: {relative_path}")
            continue
        expected_bytes = stem.get("bytes")
        if expected_bytes != path.stat().st_size:
            errors.append(
                f"{label}: byte-size mismatch "
                f"(expected {expected_bytes}, actual {path.stat().st_size})"
            )
        expected_hash = str(stem.get("sha256", "")).upper()
        actual_hash = sha256(path)
        if expected_hash != actual_hash:
            errors.append(
                f"{label}: SHA-256 mismatch "
                f"(expected {expected_hash}, actual {actual_hash})"
            )

    gates = data.get("acceptance_gates", [])
    gate_ids = [gate.get("gate_id") for gate in gates]
    if len(gate_ids) != len(set(gate_ids)):
        errors.append("acceptance gate IDs must be unique")
    if len(gates) < 7:
        errors.append(f"expected at least 7 acceptance gates, found {len(gates)}")

    expected = data.get("workspace_v2_expected_results", {})
    if expected.get("versions", {}).get("minimum_candidate_versions", 0) < 2:
        errors.append("minimum_candidate_versions must be at least 2")
    if not expected.get("approval", {}).get("human_approval_required_for_final"):
        errors.append("human approval must be required for Final")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()

    manifest_path = args.manifest
    if not manifest_path.is_absolute():
        manifest_path = PROJECT_ROOT / manifest_path

    errors = validate_manifest(manifest_path)
    if errors:
        print(f"FAIL: {manifest_path}")
        for error in errors:
            print(f"- {error}")
        return 1

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    print(f"PASS: {data['sample_id']}")
    print(f"Manifest: {manifest_path}")
    print(f"Source stems: {len(data['source']['stems'])}")
    print(f"Acceptance gates: {len(data['acceptance_gates'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
