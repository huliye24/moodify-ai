#!/usr/bin/env python3
"""Verify asset registry invariants (DSK-RJWC-ASSET-REGISTRY-001).

Checks: schema-required fields, asset_id pattern and uniqueness,
OWNED-without-evidence, PRODUCTION-without-version, and coverage of the
six Moodify core families. Exits 0 when no fatal errors.
Usage: python scripts/verify_asset_registry.py [repo_root]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ASSET_ID_PATTERN = re.compile(r"^(MFY|RJWC)-(DATA|KNW|REP|MDL|SFT|SYS|CIP|CTR|BRD|INF|CAP)-[0-9]{4}$")
REQUIRED_FIELDS = [
    "asset_id", "name", "asset_class", "project", "owner_entity", "ownership_status",
    "production_status", "repository_locations", "evidence_refs",
    "third_party_dependencies", "confidentiality",
]
ASSET_CLASSES = {
    "DATA", "KNOWLEDGE", "REPRESENTATION", "MODEL", "SOFTWARE", "PRODUCTION_SYSTEM",
    "CULTURAL_IP", "CONTRACTUAL", "BRAND_DOMAIN", "INFRASTRUCTURE_RESOURCE",
    "OPERATIONAL_CAPABILITY",
}
OWNERSHIP_STATUSES = {
    "OWNED", "LICENSED_EXCLUSIVE", "LICENSED_NONEXCLUSIVE", "CONTROLLED_RESOURCE",
    "THIRD_PARTY", "JOINTLY_OWNED", "UNKNOWN", "DISPUTED", "PUBLIC_DOMAIN",
    "OPEN_SOURCE_DEPENDENCY",
}
PRODUCTION_STATUSES = {
    "CONCEPT", "EXPERIMENTAL", "INTERNAL", "VALIDATED", "PRODUCTION",
    "DEPRECATED", "ARCHIVED", "LEGACY_UNVERIFIED",
}
CONFIDENTIALITY = {"PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED", "TRADE_SECRET"}

FAMILIES = {
    "Auditory Case Corpus": [r"Auditory Case", r"听觉案例", r"Case Corpus"],
    "Preference & Ranking Corpus": [r"Preference", r"Ranking Corpus", r"偏好", r"排序"],
    "Auditory Knowledge System": [r"WSE", r"MSE", r"PPE", r"Knowledge"],
    "Auditory Representation": [r"AuditoryProfile", r"Representation", r"表示", r"Contract"],
    "Models & Decision Systems": [r"Judge", r"Ranker", r"Model", r"模型"],
    "Production System": [r"Control Spine", r"Production", r"Evidence", r"Queue", r"CWC"],
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    assets_dir = root / "asset-registry" / "assets"

    errors: list[str] = []
    records: list[dict] = []
    ids: set[str] = set()

    if not assets_dir.is_dir():
        print(json.dumps({"ok": False, "errors": ["asset-registry/assets missing"]}, indent=2))
        return 4

    for path in sorted(assets_dir.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path.name}: parse error: {exc}")
            continue
        if not isinstance(record, dict):
            errors.append(f"{path.name}: record is not object")
            continue

        aid = record.get("asset_id")
        if not isinstance(aid, str) or not ASSET_ID_PATTERN.match(aid):
            errors.append(f"{path.name}: invalid asset_id {aid!r}")
        elif aid in ids:
            errors.append(f"{path.name}: duplicate asset_id {aid}")
        else:
            ids.add(aid)

        for field in REQUIRED_FIELDS:
            if field not in record:
                errors.append(f"{aid}: missing required field {field}")
        if record.get("asset_class") not in ASSET_CLASSES:
            errors.append(f"{aid}: invalid asset_class")
        if record.get("ownership_status") not in OWNERSHIP_STATUSES:
            errors.append(f"{aid}: invalid ownership_status")
        if record.get("production_status") not in PRODUCTION_STATUSES:
            errors.append(f"{aid}: invalid production_status")
        if record.get("confidentiality") not in CONFIDENTIALITY:
            errors.append(f"{aid}: invalid confidentiality")
        if record.get("ownership_status") == "OWNED" and not record.get("evidence_refs"):
            errors.append(f"{aid}: OWNED but no evidence_refs")
        if record.get("production_status") == "PRODUCTION" and not record.get("current_version"):
            errors.append(f"{aid}: PRODUCTION but no current_version")
        records.append(record)

    blob = json.dumps(records, ensure_ascii=False)
    coverage = {
        name: any(re.search(pattern, blob, re.I) for pattern in patterns)
        for name, patterns in FAMILIES.items()
    }
    result = {
        "ok": not errors,
        "record_count": len(records),
        "unique_ids": len(ids),
        "errors": errors,
        "moodify_core_family_coverage": coverage,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 3


if __name__ == "__main__":
    sys.exit(main())
