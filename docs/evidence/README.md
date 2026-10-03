# Evidence

Verified runtime evidence. This directory answers the question **"why do we believe
this?"** with primary artifacts rather than summaries.

It exists because `docs/canon/AUTHORITY_ORDER.md` places *verified runtime evidence* at
**authority tier 4** — above canonical main behavior, above subsystem documentation, and
above anything a historical document claims about itself. A tier-4 claim must be backed by
an artifact here, not by a narrative.

## Layout

| Directory | Holds |
|---|---|
| `cloud/` | Primary captures of deployed infrastructure |
| `runtime/` | Evidence index, truth table, system map |
| `decisions/` | Canon-level decision records |

## Provenance

These files were migrated on 2026-10-03 out of `审查包/W01-P00_*` and
`审查包/审查包 8.18完成/W01-P01_*` during
[MOODIFY_NETWORK_RESTRUCTURE_001](../restructure/RESTRUCTURE_REPORT.md).

The migration was **mandatory before removal**, because `AGENTS.md:101` and
`docs/canon/AUTHORITY_ORDER.md:10` both name the *W01-P00 Evidence Index* as an authority
source, and three canonical documents cite these artifacts directly. Per the task spec §3.6,
evidence may not be lost as a side effect of cleanup. `git log --follow <path>` still traces
each file to its original location.

## What is here

### `cloud/` — the primary deployed-infrastructure evidence

| Evidence | File | Claim it supports | Confidence |
|---|---|---|---|
| **E13** | `LA_103_144_246_242_scan.txt` | Full read-only scan of the Los Angeles production node (`yisu-6a7bcb73aac20`, Ubuntu 22.04.2), captured 2026-08-17 19:52 +08:00 | **HIGH** |
| **E14** | `HZ_120_55_191_146_scan.txt` | Full read-only scan of the Hangzhou node (`iZln9jrdhi9iv6Z`, Ubuntu 26.04 LTS), captured 2026-08-17 19:54 +08:00 | **HIGH** |
| — | `03_CLOUD_INFRASTRUCTURE_REALITY.md` | Node roles, PolarDB instances, OSS absent — the basis of `docs/canon/CURRENT_ARCHITECTURE.md` §1 | HIGH |
| — | `readonly_node_scan.sh` | The generator for E13/E14. Kept so the scans stay reproducible. | — |

E13 and E14 are the **strongest cloud evidence in the repository** and previously existed in
exactly one place. The root-level `MOODIFY_CLOUD_CURRENT_STATE_2026-08-17.md/.json` pair is a
*different, weaker* artifact — registered separately as E18 at **MEDIUM** confidence, from a
same-day black-box investigation that the index records as not directly re-verifiable (E17).

### `runtime/`

| File | Role |
|---|---|
| `08_EVIDENCE_INDEX.md` | The **W01-P00 Evidence Index** referenced by `AGENTS.md` and `AUTHORITY_ORDER.md`. Registers E01–E27 with sources, timestamps and confidence. |
| `05_MOODIFY_TRUTH_TABLE.csv` / `.md` | 51-row schema-validated fact table (E27) behind the `docs/REPOSITORY_STATUS.md` capability table |
| `07_CURRENT_SYSTEM_MAP.mmd` | System map referenced by the W01-P00 reality snapshot |

### `decisions/`

| File | Role |
|---|---|
| `01_CANONICAL_DECISION_REGISTER.md` | **CD-001 … CD-016**, the decision record behind Canon v1.0 identity convergence. Cited by `docs/REPOSITORY_STATUS.md:12` and `docs/canon/CANON_CHANGELOG.md:186`. |

## Confidence discipline

The index deliberately records what could **not** be verified:

- **E17 — PolarDB direct verification: BLOCKED.** `mysql SHOW DATABASES` returned access
  denied. Database state is therefore not independently confirmed.
- **E18 — MEDIUM confidence**, not reproducible by the W01-P00 investigation itself.
- No full `pytest` run was part of W01-P00 (read-only scan on a constrained machine).

This is the intended behaviour: where evidence is insufficient, the record says so rather
than manufacturing certainty. `AGENTS.md` requires the same of machine judgment —
insufficient evidence must produce `HUMAN_REQUIRED` or `INCONCLUSIVE`, never invented
confidence.

## Keeping this current

Do not add narrative summaries here. Add the **artifact** — a scan, a run log, a signed
decision — with its timestamp, host, and confidence. When a new claim changes a canonical
statement, the artifact that supports it belongs in this tree, and the affected
`docs/canon/*` entry should link to it.

New evidence files must be checked against `.gitignore` before adding
(`git check-ignore -v <path>`), because this repository ignores broad patterns
(`*.png`, `*.html`, `*.json` subsets) that have silently swallowed new artifacts before.
