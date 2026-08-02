"""Controlled dataset export (DSK-MFY-AUDITORY-INTELLIGENCE-RECLASSIFICATION-001).

Exports are data contracts + validated bundles, NOT model training.
Only explicitly eligible records are included; ambiguous rights fail closed.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from moodify.learning.models import LearningRecord

EXPORT_SCHEMA_VERSION = "1.0"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def export_learning_records(
    records: list[LearningRecord],
    output_dir: Path,
    dataset_id: str,
) -> dict:
    """Export only ELIGIBLE records; excluded/ineligible are reported but not written."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    included: list[dict] = []
    excluded: list[dict] = []
    for rec in records:
        entry = rec.to_dict()
        if rec.training_eligibility == "ELIGIBLE":
            # no per-record export timestamp: keeps exports deterministic
            included.append(entry)
        else:
            excluded.append({
                "learning_record_id": rec.learning_record_id,
                "case_id": rec.case_id,
                "training_eligibility": rec.training_eligibility,
                "exclusion_reasons": rec.exclusion_reasons,
                "excluded_from_export": True,
            })

    data_path = output_dir / f"{dataset_id}_records.json"
    data_path.write_text(json.dumps(included, ensure_ascii=False, indent=2), encoding="utf-8")

    excluded_path = output_dir / f"{dataset_id}_excluded.json"
    excluded_path.write_text(json.dumps(excluded, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest = {
        "dataset_id": dataset_id,
        "schema_version": EXPORT_SCHEMA_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "included_count": len(included),
        "excluded_count": len(excluded),
        "records_file": data_path.name,
        "records_sha256": _sha256_file(data_path),
        "excluded_file": excluded_path.name,
        "excluded_sha256": _sha256_file(excluded_path),
        "eligibility_rule": "only ELIGIBLE; UNKNOWN/PENDING_REVIEW fail closed",
        "provenance": "moodify auditory intelligence learning export",
        "contains_personal_identifiers": False,
    }
    manifest_path = output_dir / f"{dataset_id}_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def validate_export_bundle(output_dir: Path, dataset_id: str) -> list[str]:
    """Re-hash export artifacts; return problems (empty = verified)."""
    problems: list[str] = []
    manifest_path = output_dir / f"{dataset_id}_manifest.json"
    if not manifest_path.is_file():
        return ["manifest missing"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for key in ("records_file", "excluded_file"):
        fname = manifest.get(key)
        if not fname:
            continue
        path = output_dir / fname
        if not path.is_file():
            problems.append(f"{key}: missing {fname}")
            continue
        actual = _sha256_file(path)
        if actual != manifest.get(f"{key.replace('_file', '')}_sha256"):
            problems.append(f"{key}: hash mismatch")
    return problems
