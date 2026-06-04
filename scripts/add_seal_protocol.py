#!/usr/bin/env python3
"""Add AEP Seal Protocol sections to all MHP plan files.

- planned/proposed MHPs (incomplete): append full SEAL_PROTOCOL placeholder
- completed MHPs (missing seal): append SEAL_BACKFILL_NEEDED marker

Protocol: AEP_NEM_Seal_Protocol_v0.1
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

PLAN_DIR = Path("/home/ubuntu/moodify-mainline/docs/plan")
TIMESTAMP = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ── Seal section template for planned/proposed MHPs ──

SEAL_SECTION_PLANNED = """

## Seal Protocol (AEP Industrial Seal v0.1)

> ⚠️ **Pending** — this MHP has not been executed yet.
> The seal fields below will be populated when the MHP reaches FUNCTION_COMPLETE.
> Do NOT mark INDUSTRIAL_DONE until all six evidence layers are complete.

```yaml
# ── Identity ──
seal_id: {seal_id}
aep_id: {aep_id}
nem_id: {nem_id}
e_chain_id: {e_chain_id}
project: Moodify
version: v0.1
created_at: {timestamp}
executor: pending
reviewer: pending

# ── Status ──
seal_status: PLANNED     # PLANNED | FUNCTION_COMPLETE | EVIDENCE_PENDING | SEAL_REVIEW | SEAL_COMPLETE | INDUSTRIAL_DONE
function_complete: false

# ── PoEW Reference ──
poew_id: pending
poew_file: pending
poew_hash: pending
execution_timestamp: pending
execution_duration_s: pending
environment: pending

# ── Gate Reference ──
gate_id: pending
gate_file: pending
gate_result: pending
must_pass_total: 0
must_pass_passed: 0
must_stop_triggered: false

# ── Evidence Bundle ──
functional_evidence: []
execution_evidence: []
quality_evidence: []
integrity_evidence: []
risk_evidence: []
downstream_evidence: []

# ── Test Summary ──
tests_total: 0
tests_passed: 0
tests_failed: 0
tests_skipped: 0
success_rate: 0.0
critical_failures: 0

# ── Artifact Summary ──
artifacts: []

# ── Risk Summary ──
risks: []

# ── Downstream ──
downstream_dependency_note: pending
reopen_criteria: []

# ── Decision ──
seal_decision:
  decision: PLANNED
  decision_reason: MHP not yet executed
  approved_by: pending
  approved_at: pending
  next_status: FUNCTION_COMPLETE
```

### Minimal Seal Checklist (pre-execution)

- [ ] MHP execution started
- [ ] Function output exists
- [ ] PoEW record created
- [ ] Gate result recorded
- [ ] Test evidence collected
- [ ] Artifact hashes recorded
- [ ] Regression impact checked
- [ ] Known risks documented
- [ ] Downstream dependency documented
- [ ] Reopen criteria defined
- [ ] Reviewer recorded
- [ ] Final seal decision recorded
"""

# ── Seal backfill marker for completed MHPs ──

SEAL_BACKFILL_MARKER = """

<!--
══════════════════════════════════════════════════
SEAL_BACKFILL_NEEDED

This MHP is marked **Status: completed** but was closed
before the AEP Industrial Seal Protocol (v0.1) existed.

Fields to backfill:
  - seal_id, aep_id, nem_id, e_chain_id
  - poew_reference (PoEW file + hash)
  - gate_reference (gate file + result)
  - evidence_bundle (6 layers)
  - test_summary, artifact_summary
  - risk_summary, downstream_dependency_note
  - reopen_criteria, seal_decision, reviewer, timestamp

See: /home/ubuntu/AEP-NEM/AEP_NEM_Seal_Protocol_v0_1/specs/SEAL_PROTOCOL.md
══════════════════════════════════════════════════
-->
"""


def extract_ids(content: str) -> dict[str, str]:
    """Extract E-Chain and NEM IDs from MHP Direction field."""
    e_chain_id = "unknown"
    nem_id = "unknown"

    m = re.search(r'ECHAIN-MOODIFY-[\w-]+', content)
    if m:
        e_chain_id = m.group(0)

    m = re.search(r'NEM-MOODIFY-[\w-]+', content)
    if m:
        nem_id = m.group(0)

    return {"e_chain_id": e_chain_id, "nem_id": nem_id}


def get_mhp_number(filename: str) -> int:
    m = re.match(r'MHP-(\d+)', filename)
    return int(m.group(1)) if m else 0


def make_seal_section(filename: str, content: str) -> str:
    """Build the seal section string for a planned MHP."""
    num = get_mhp_number(filename)
    ids = extract_ids(content)

    # Derive aep_id from filename
    slug = filename.replace(".md", "").replace("MHP-", "").lower()
    # Take first word group
    parts = slug.split("_")
    short = "_".join(parts[:4]) if len(parts) > 4 else slug
    aep_id = f"AEP-MOODIFY-MHP{num:03d}"

    seal_id = f"SEAL-MOODIFY-MHP{num:03d}"

    return SEAL_SECTION_PLANNED.format(
        seal_id=seal_id,
        aep_id=aep_id,
        nem_id=ids["nem_id"],
        e_chain_id=ids["e_chain_id"],
        timestamp=TIMESTAMP,
    )


def process_file(filepath: Path) -> dict:
    """Add seal section to a single MHP file. Returns {status: ...}."""
    content = filepath.read_text(encoding="utf-8")
    filename = filepath.name

    # Skip if already has seal section
    if "Seal Protocol" in content or "SEAL_BACKFILL_NEEDED" in content:
        return {"file": filename, "action": "skip", "reason": "already has seal section"}

    is_completed = "**Status**: completed" in content or "**Status**:" in content and "completed" in content.split("**Status**:")[-1].split("\n")[0] if "**Status**:" in content else False

    # More reliable detection
    status_line = ""
    for line in content.split("\n"):
        if line.strip().startswith("**Status**"):
            status_line = line.strip()
            break

    if "completed" in status_line:
        # Add backfill marker
        new_content = content.rstrip() + SEAL_BACKFILL_MARKER + "\n"
        filepath.write_text(new_content, encoding="utf-8")
        return {"file": filename, "action": "marked_backfill", "status": "completed"}
    elif "planned" in status_line or "proposed" in status_line:
        # Add full seal section
        seal_section = make_seal_section(filename, content)
        new_content = content.rstrip() + seal_section + "\n"
        filepath.write_text(new_content, encoding="utf-8")
        return {"file": filename, "action": "added_seal", "status": status_line}
    else:
        return {"file": filename, "action": "skip", "reason": f"unknown status: {status_line}"}


def main():
    files = sorted(PLAN_DIR.glob("MHP-*.md"))
    print(f"Processing {len(files)} MHP files...\n")

    stats = {"added_seal": 0, "marked_backfill": 0, "skip": 0, "error": 0}
    details: list[dict] = []

    for fp in files:
        try:
            result = process_file(fp)
            stats[result["action"]] += 1
            if result["action"] not in ("skip",):
                details.append(result)
        except Exception as e:
            stats["error"] += 1
            print(f"  ERROR: {fp.name}: {e}")

    print(f"Results:")
    print(f"  added_seal:     {stats['added_seal']}  (planned/proposed → full seal placeholder)")
    print(f"  marked_backfill:{stats['marked_backfill']}  (completed → SEAL_BACKFILL_NEEDED marker)")
    print(f"  skipped:        {stats['skip']}  (already had seal section)")
    print(f"  errors:         {stats['error']}")
    print(f"  total:          {len(files)}")

    # Print detail for first 5 of each type
    for action, label in [("added_seal", "Added seal"), ("marked_backfill", "Marked backfill")]:
        items = [d for d in details if d["action"] == action]
        if items:
            print(f"\n{label} ({len(items)} files):")
            for d in items[:5]:
                print(f"  {d['file']} ({d.get('status', '')})")
            if len(items) > 5:
                print(f"  ... and {len(items) - 5} more")


if __name__ == "__main__":
    main()
