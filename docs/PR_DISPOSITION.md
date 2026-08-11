# PR Disposition — Moodify 1.0 Data Foundation

**Date:** 2026-08-11
**Protocol reference:** MOODIFY_AUGUST_2026_FREEZE_PROTOCOL Gate 1 — PR disposition plan
**Canonical mainline:** `codex/mfy-data-factory-001` (PR #21) — sole carrier of the August freeze work

## Disposition table

| PR | Branch | State after | Disposition | Evidence |
|---|---|---|---|---|
| #21 | codex/mfy-data-factory-001 | OPEN / DRAFT | **KEEP** — canonical release carrier | Contains all Gate 1–6 deliverables; merge + tag at Gate 6 close |
| #20 | codex/moodify-1.0-release-convergence | CLOSED | Superseded by #21 | release-convergence is a direct ancestor of #21 head (git merge-base); v1.0.0-rc.1 packaging lives on #21 |
| #19 | codex/auditory-intelligence-unification | CLOSED | Superseded by #16 (MERGED) + #21 | The Ear of AI reconstitution and Phase I default surfaces delivered; 3030-file draft never merged |
| #18 | codex/mfy-mig-001-canonical-contracts | CLOSED | Superseded by #21 | moodify.contracts present in current tree (src/moodify/contracts/) |
| #15 | codex/mainline-cloud-dev-20260603 | CLOSED | CLOSE_AS_SUPERSEDED_AFTER_EXTRACTION | Per artifacts/pr15_extraction_001/PR15_FINAL_DISPOSITION.md; extraction completed (PR #17, MIG-001..011) |
| #13 | huliye24-patch-1 | CLOSED | Superseded by #14 (MERGED) | GPL-3.0 LICENSE on main (0b355e7) |
| #9 | feat/brand-integration | CLOSED | Superseded by #11 (MERGED) + Android nav restructure | Key removal f463eee; AppTabLayout absent from current codebase (bottom-nav 4-tab) |

## Rules going forward

- Branches of closed PRs are retained as-is (immutable archives); no force-delete.
- New PRs against `main` are not expected during the freeze window; all freeze work lands on #21 and is released at Gate 6 close (tag `Moodify 1.0 — Data Foundation`).
- Reopen only if a closed PR's intent is discovered to be *not* represented in the canonical line.
