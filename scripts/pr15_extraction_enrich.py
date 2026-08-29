#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "artifacts/pr15_extraction_001/pr15_file_inventory.csv"

DECISIONS = {
    "AUDITORY_CORE": ("EXTRACT", "moodify.auditory", "Auditory scan/compare tests; rerun with ffmpeg"),
    "WSE": ("EXTRACT", "moodify.auditory.representation", "Feature tests required before migration"),
    "MSE": ("EXTRACT", "moodify.structural", "Score-engine tests exist; external backend remains optional"),
    "PPE_RUNTIME": ("REIMPLEMENT", "moodify.production", "Competing state/runtime authority; migrate by contract"),
    "EVIDENCE_ASSET": ("EXTRACT", "moodify.contracts", "Bridge schema/serialization tests are useful source evidence"),
    "LEARNING": ("EXTRACT", "moodify.learning", "Preserve fail-closed rights and explicit human labels"),
    "APPLICATION_ANDROID": ("REIMPLEMENT", "apps/android", "Keep UI/tests; bind to canonical API contract"),
    "APPLICATION_API": ("REIMPLEMENT", "moodify.api", "API must consume canonical contracts"),
    "CLOUD": ("KEEP_AS_REFERENCE", "infrastructure", "Infrastructure concepts only; no product authority"),
    "TOOLING": ("KEEP_AS_REFERENCE", "tools", "Review individual tools when a migration needs them"),
    "TESTS": ("EXTRACT", "tests", "Tests are evidence, but fixtures/tool requirements must be made hermetic"),
    "RESEARCH_EXPERIMENTAL": ("KEEP_AS_REFERENCE", "research", "Research evidence, not production truth"),
    "DOCUMENTATION_HISTORY": ("KEEP_AS_REFERENCE", "docs/history", "Historical claims do not establish authority"),
    "GENERATED_ARTIFACT": ("DELETE_LATER", "none", "Generated evidence/output; preserve only hashes or selected records"),
    "DUPLICATE": ("DELETE_LATER", "none", "Delete only after canonical replacement lands"),
    "UNKNOWN": ("HUMAN_DECISION", "unresolved", "Requires manual classification in a scoped follow-up"),
}


def main() -> int:
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        action, target, evidence = DECISIONS[row["domain_first_pass"]]
        row["manual_action"] = action
        row["canonical_target"] = target
        row["evidence_tests"] = evidence
        row["notes"] = "First-pass decision; high-value subsystems are reviewed in companion reports."
        path = row["path"]
        if path.startswith(("night/moodify_daily_run_system/", "night/moodify_daily_run_system_v0_1.zip")):
            row["manual_action"] = "DELETE_LATER"
            row["notes"] = "Duplicate packaged runtime or archive; retain history until cleanup PR."
        elif path.startswith("moodify-core-package/src/moodify/auditory/"):
            row["manual_action"] = "EXTRACT"
            row["notes"] = "High-value WSE scan/evidence source; migrate behind minimum contracts."
        elif path == "moodify-bridge/src/moodify_bridge/schemas.py":
            row["manual_action"] = "EXTRACT"
            row["notes"] = "Best schema source, but too broad to adopt unchanged."
    with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Enriched {len(rows)} inventory rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
