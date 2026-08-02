"""Evidence manifests (DSK-MFY-AUDITORY-SCAN-001).

Every scan and comparison writes a manifest with hashes of all produced
artifacts, following the evidence_manifest.json pattern used by
ProductionControlService.package().
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_artifact(path: Path) -> dict:
    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
    }


def write_scan_manifest(
    out_path: Path,
    *,
    case_id: str,
    stage: str,
    input_path: Path,
    input_sha256: str,
    profile_id: str,
    profile_hash: str,
    artifacts: dict[str, Path],
    environment: dict,
    commands: list[dict],
) -> None:
    manifest = {
        "case_id": case_id,
        "stage": stage,
        "input_path": str(input_path),
        "input_sha256": input_sha256,
        "scan_profile_id": profile_id,
        "scan_profile_hash": profile_hash,
        "artifacts": {k: hash_artifact(v) for k, v in artifacts.items() if v is not None and v.exists()},
        "environment": environment,
        "commands": commands,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    out_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def write_comparison_manifest(
    out_path: Path,
    *,
    case_id: str,
    candidate_id: str,
    artifacts: dict[str, Path],
    judgment_decision: str,
) -> None:
    manifest = {
        "case_id": case_id,
        "candidate_id": candidate_id,
        "artifacts": {k: hash_artifact(v) for k, v in artifacts.items() if v is not None and v.exists()},
        "judgment_decision": judgment_decision,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    out_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def verify_manifest_hashes(manifest: dict) -> list[str]:
    """Re-hash recorded artifacts; return list of mismatches (empty = verified)."""
    problems: list[str] = []
    for key, entry in manifest.get("artifacts", {}).items():
        path = Path(entry["path"])
        if not path.is_file():
            problems.append(f"{key}: missing {path}")
            continue
        actual = sha256_file(path)
        if actual != entry["sha256"]:
            problems.append(f"{key}: hash mismatch ({entry['sha256'][:12]} != {actual[:12]})")
    return problems
