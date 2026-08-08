# Codex Independent Acceptance — DSK-MFY-THICKNESS-001

**Date:** 2026-07-30  
**Judge:** Codex, independent repository and test audit  
**Decision:** `REWORK` — valuable hardening landed, but the sprint is not complete

## Executive Finding

The reported `18/18 Final Acceptance` is not supported by repository evidence. Two tasks were explicitly deferred, two safety predicates were not connected to their production boundaries, the rights implementation confused listening feedback with copyright authorization, and the reported test total double-counted 28 tests.

The useful work has been retained. This audit corrected the rights model, hardened source-record rejection, added regression tests, and recorded the remaining gaps. It does not promote the sprint to complete.

## Material Findings

| ID | Severity | Finding | Current disposition |
|---|---|---|---|
| IA-001 | P0 | Rights status was inferred from `human_feedback.status`; completed listening is not authorization. | Fixed with an explicit fail-closed five-asset rights manifest and tests. Production preflight integration remains open. |
| IA-002 | P0 | `can_write_back()` is an unused predicate; actual Craft write paths do not call it. | `REWORK`; production enforcement remains open. |
| IA-003 | P0 | `mrs_can_release()` is not called by delivery or approval boundaries. | `REWORK`; release enforcement remains open. |
| IA-004 | P1 | Invalid Treatment Records were warned about but still aggregated. | Fixed: invalid records are excluded and reported as errors. |
| IA-005 | P1 | Aggregator robustness was claimed without aggregator regression tests. | Fixed with six focused tests. |
| IA-006 | P1 | Interrupted-run recovery was deferred. | Incomplete. |
| IA-007 | P1 | Historical compatibility was deferred. | Incomplete. |
| IA-008 | P1 | Backup-before-overwrite is not an interruption/recovery test. | `REWORK`; it does not satisfy DSK-013. |
| IA-009 | P1 | The stated 1,198 test total double-counted the 28 hardening tests. | Corrected below. |

## Independent Verification

| Scope | Result |
|---|---|
| Rights, Craft predicate, and aggregator hardening | 29 passed |
| Root `tests/` after declaring cloud-only X-CLP optional | 130 passed, 1 skipped |
| Runtime suite | 695 passed, 9 skipped |
| Core suite | 447 passed, 32 warnings |
| Total independent passing tests | 1,272 passed |
| Total skips | 10 skipped |
| Treatment summary | 27 active records, 3 completed feedback records, 3 excluded `.bak` artifacts |
| Rights manifest | 5 assets pending, 0 ready, rights gate false |
| Determinism | JSON and Markdown byte-identical across two fresh runs |
| Audio processed by this audit | none |

X-CLP is skipped because `xclp` is an undeclared cloud-side package expected at `/home/ubuntu/X-CLP`. Its absence no longer aborts unrelated local test collection. X-CLP itself remains unverified on this workstation.

## Task-Level Promotion Decision

- Verified or corrected: DSK-002, DSK-003, DSK-004, DSK-005, DSK-010, DSK-016, DSK-017.
- Hardened but not production-enforced: DSK-007, DSK-008, DSK-009.
- Evidence remains insufficient: DSK-006, DSK-011, DSK-012, DSK-015.
- Incomplete by explicit deferral: DSK-013, DSK-014.
- Final promotion rejected: DSK-001 and DSK-018.

## Required Work Before Final Acceptance

1. Enforce the structured rights manifest at the real audio-processing preflight boundary.
2. Enforce Craft eligibility in every Craft Library write path, including delivery writeback and automated data-loop feeds.
3. Require explicit human listening approval at delivery/release boundaries; an MRS result or default parameter must not grant it.
4. Add interruption injection and partial-artifact recovery tests.
5. Add historical workspace/manifest fixtures and explicit load, migration, or refusal tests.
6. Replace summary overwrite with a tested atomic generation/recovery contract for JSON and Markdown.
7. Run X-CLP in its declared cloud environment or package it as a reproducible optional dependency.

Until these are complete, the truthful sprint state is `HARDENING / REWORK`, not final acceptance and not production-proven.

## P0 Corrective Update

After this independent decision, the principal production boundaries were integrated and verified:

- live processing now requires exact-source rights authorization;
- delivery now requires identified human listening approval and persisted rights evidence;
- delivery-based Craft writeback now requires technical approval, matching delivery, human approval, and rights evidence;
- Runtime passes 695 tests with 10 skips; root tests pass 131 with one optional X-CLP skip.

This closes the main direct bypasses. Automated recommendation feeds, interruption recovery, and historical compatibility remain open, so the overall decision remains `HARDENING / REWORK`.
