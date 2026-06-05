# MHP-881: AWJ Worker Pack Generator

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-SYSTEM-047 / System Plan-6A / E1
**Depends on**: MHP-880 (Close Build NEM)

## What Was Implemented

Created `scripts/map_judge_check.py` — the AWJ Judge check script for MAP Worker AEP validation. This is the System NEM deliverable that makes the Judge gate executable.

### Script: `scripts/map_judge_check.py`

Three subcommands mirroring the Judge gate formula G_schema × G_scope × G_runtime × G_test × G_evidence × G_arch = 1:

```bash
python3 scripts/map_judge_check.py schema   <report.json>     # G_schema
python3 scripts/map_judge_check.py scope    <diff.txt> <policy.json>  # G_scope
python3 scripts/map_judge_check.py runtime  <task.json>       # G_runtime + G_test
python3 scripts/map_judge_check.py evidence <task.json>       # G_evidence
python3 scripts/map_judge_check.py arch     <diff.txt>        # G_arch
python3 scripts/map_judge_check.py all      <task.json> <diff.txt>  # All gates
```

### Acceptance Criteria

- [x] Judge check script exists and is executable.
- [x] All 6 gates have corresponding subcommands.
- [x] Script validates real v01 report against MAP schema.
- [x] Script correctly rejects scope violations.
- [x] Output is machine-readable JSON.
