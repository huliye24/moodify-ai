# Archive Index

What has left the mainline, where it went, and how to get it back.

**Why this file exists.** `AGENTS.md` forbids mass-deletion of legacy code without an
explicit cleanup task. A cleanup task needs a record, or "removed" and "lost" become
indistinguishable six months later. This is that record. It was named as a missing
prerequisite by `AI_CONTEXT_OPTIMIZATION.md` and `docs/reduction/EXECUTION_PLAN_V1.md`
Phase 2.2.1 before this restructure ran.

**The archive is git.** Nothing below needs a separate `archive/` tree — that would only
move clutter from one room to another. Every path is recoverable from history or from the
safety tag.

```bash
# restore a single path as it was before the restructure
git checkout pre-network-restructure-2026-10-03 -- <path>

# inspect the full pre-restructure tree
git ls-tree -r --name-only pre-network-restructure-2026-10-03 | less
```

| | |
|---|---|
| **Safety tag** | `pre-network-restructure-2026-10-03` |
| **Baseline commit** | `c11bc7f5` |
| **Branch** | `deepseek/moodify-network-restructure-001` |
| **Full baseline listing** | [`docs/restructure/BEFORE_TREE.txt`](restructure/BEFORE_TREE.txt) |
| **Per-path justification** | [`docs/restructure/CLEANUP_MANIFEST.md`](restructure/CLEANUP_MANIFEST.md) |
| **Report** | [`docs/restructure/RESTRUCTURE_REPORT.md`](restructure/RESTRUCTURE_REPORT.md) |

---

## Don't archive — deleted outright

Nothing. Every path below is either retained on disk, recoverable from git, or both.

## Left the mainline, kept on disk

These directories stay in the working copy but are no longer tracked. They belong to a
different project line that keeps its own branches.

| Path | Line | Why it is not tracked | Recover |
|---|---|---|---|
| `web 3.0/` | MOOD / Web3 | `.gitignore:63` — "Other project lines living in this workspace are not part of the Moodify mainline." 37 files that predated the ignore rule were un-tracked. | `git checkout pre-network-restructure-2026-10-03 -- "web 3.0/"` |
| `mood-web3-protocol/` | MOOD / Web3 | Formerly `protocol/`. Untracked; ~20 `codex/mood-*` branches carry this line. | `git checkout pre-network-restructure-2026-10-03 -- protocol/` |
| `apps/web/` | MOOD / Web3 | The MOOD dApp. Stays deployable from disk. | `git checkout pre-network-restructure-2026-10-03 -- apps/web/` |
| `e2e/staging/` | MOOD / Web3 | Staging specs for the above. | `git checkout pre-network-restructure-2026-10-03 -- e2e/staging/` |

> **Load-bearing on-disk evidence.** The *untracked* portion of `web 3.0/` holds
> `MOOD_PROTOCOL_CONTRIBUTION_CORE_002/003` schemas (draft 2020-12, including the `allOf`
> guards forbidding `tokenAmount` / `payout` / `claimAmount` / `vesting`) plus
> `CONTRIBUTION_SPEC.md` and `REPUTATION_MODEL.md`. A 2026-09-29 human ruling
> (`docs/audits/2026-09-29_GATE3_CONTRIBUTION_PREEXISTING_FAILURES.md:40`) named that package
> the **contract authority** for shipped code in `moodify-core-package/src/moodify/contribution/`.
> There is no tracked copy of `CONTRIBUTION_SPEC.md` or `REPUTATION_MODEL.md` anywhere.
> **Do not delete `web 3.0/` from disk.** Un-tracking is not deletion, and that distinction is
> what keeps this evidence reachable.

## Removed from the mainline, recoverable from git history

| Path | Files | Class | Where the content lives now |
|---|---|---|---|
| `windows版本开发/` | 330 | historical work packages | nowhere — docs-only, superseded by `moodify-desktop/` |
| `审查包/` | 382 → 9 kept | audit corpus | the 9 authority artifacts moved to [`docs/evidence/`](evidence/README.md); the rest is history |
| `engine/` | 19 | facade | capabilities already in Core (see manifest) |
| `demo/` | 12 | duplicate pipeline | Core's canonical `moodify analyze` |
| `moodify-qa/` | 26 | retired product | `moodify-core-package/src/moodify/auditory/` |
| `moodify-qa-desktop/` | 8 | retired shell | `moodify-desktop/` |
| `products/` | 32 | empty scaffolds | Core |
| `shared/` | 7 | empty scaffolds | Core |
| `sdk/` | 9 | placeholder | Core's `moodify.api` / `moodify.release_cli` |
| `plugins/` | 9 | unbuilt | — |
| `phys-lab/` | 1 | launcher | `moodify.physics` |
| `apps/ear-workbench/android/` | 24 | non-buildable archive | `apps/android` |
| `moodify-pulse/` | 18 | retired product | `moodify-desktop/` |
| `工程经验层/` | 5 | governance | moved to [`docs/governance/constraints/`](governance/constraints/CONSTRAINT_REGISTRY.md) |
| `.codex_tmp/`, `scan_err.txt` | 2 | scratch | — |
| `dashboard.html`, `cloud_status.py` | 2 | 3.0-era cloud experiment dashboard + the HTTP status API serving it | nowhere — superseded; no references outside the temporal-texture baseline snapshot |

## Root-level work products moved to `docs/archive/`

The task spec (§33) requires the repository root to carry only real entry points. These five
were superseded work products sitting at the top level. They are kept, not deleted, because
they document **why** this restructure happened — including the fact that three prior
reduction plans were written and never executed, which is itself the argument for the
structural guard in `scripts/check_repo_structure.py`.

| File | What it was |
|---|---|
| `CURRENT_STATE_AUDIT.md` | 2026-09-17 point-in-time self-described "STEP 1 deliverable" |
| `MOODIFY_PRODUCT_AUDIT.md` | 2026-08-30 product/duplication audit at Canon v1.1 (two versions behind) |
| `REDUCTION_PLAN.md` | 2026-08-30 reduction plan marked "待人类批准；本次未执行任何修改" — **never executed** |
| `AI_CONTEXT_OPTIMIZATION.md` | 2026-08-24 advisory; named `docs/ARCHIVE_INDEX.md` as a missing prerequisite, which this restructure finally created |
| `CODE_FREEZE_MANIFEST.json` | 2026-08-11 freeze manifest for a different branch (`codex/mfy-data-factory-001` @ `b225c30`) |

Root now holds 13 files: `README.md`, `AGENTS.md`, `GOVERNANCE.md`, `MAINTAINERS.md`,
`CONTRIBUTING.md`, `DEVELOPMENT.md`, `CHANGELOG.md`, `CITATION.cff`, `LICENSE`,
`Dockerfile`, `docker-compose.yml`, `.gitignore`, `.env.example`.

> Note: inbound links from the (themselves stale) planning docs under `docs/reduction/`,
> `docs/plan/`, and `docs/reports/` still name the old root paths. Those documents are
> historical records of a superseded state and were left as-is rather than rewritten,
> consistent with `docs/canon/AUTHORITY_ORDER.md` level 8.

## Moved, not archived

| From | To |
|---|---|
| `审查包/W01-P00_*/raw_scan/*.txt` (E13, E14) | `docs/evidence/cloud/` |
| `审查包/W01-P00_*/08_EVIDENCE_INDEX.md` | `docs/evidence/runtime/` |
| `审查包/W01-P00_*/05_MOODIFY_TRUTH_TABLE.*` | `docs/evidence/runtime/` |
| `审查包/W01-P00_*/07_CURRENT_SYSTEM_MAP.mmd` | `docs/evidence/runtime/` |
| `审查包/W01-P00_*/03_CLOUD_INFRASTRUCTURE_REALITY.md` | `docs/evidence/cloud/` |
| `审查包/审查包 8.18完成/W01-P01_*/01_CANONICAL_DECISION_REGISTER.md` | `docs/evidence/decisions/` |
| `工程经验层/*` | `docs/governance/constraints/` |
| `MOODIFY_CLOUD_CURRENT_STATE_2026-08-17.{md,json}` (E18) | `docs/evidence/cloud/` — registered evidence, not a work product |

`git log --follow <new-path>` traces each file through the move.

## Deliberately retained in the mainline

Not everything old is clutter. These were audited and **kept**:

| Path | Why it stays |
|---|---|
| `treatment_records/` (30) | The only surviving provenance for the MHP-026 preset-calibration experiment. Its source audio is gitignored, so the records are the evidence. Consumed by three `scripts/v01_*.py`. |
| `moodify_runtime/` (13) | ~1,550 lines of unique commerce/pricing/settlement/refund logic plus a 938-line test — no Core equivalent, and the server side of `apps/music-android`'s P09/P10 clients. |
| `moodify-music-package/` (54) | Referenced by `ops/schema_dry_run.py` and the MUSIC_CLOUD_RUNBOOK_2_0 production runbook. Unique schema authority; 19 tests. |
| `apps/android`, `apps/music-android` | Both are plausible current Android clients with contradictory evidence. Escalated; neither is touched. |
| `moodify-core-package/` (679) | The real Core. |
| `moodify-desktop/` (21) | The current Studio. |
| `protocol/` (rebuilt) | The retired `protocol/` was the MOOD Web3 line. A fresh `protocol/` now carries the Sound Protocol and the MIP process. |
