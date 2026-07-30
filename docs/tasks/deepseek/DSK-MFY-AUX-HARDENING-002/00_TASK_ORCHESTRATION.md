# DSK-MFY-AUX-HARDENING-002 — Bounded Auxiliary Hardening

**Date:** 2026-07-30  
**Owner and final Judge:** Codex / authorized human owner  
**Implementation worker:** DeepSeek in the local PyCharm terminal  
**Status:** READY FOR EXECUTION

## 1. Purpose

Use DeepSeek for bounded, evidence-heavy implementation and test work while reserving product boundaries, architectural exceptions, rights decisions, listening judgments, and final acceptance for Codex and the authorized human owner.

This is a directly authorized implementation session, not the JSON-only audit Worker described in `DSK-MFY-THICKNESS-001/03_DEEPSEEK_SYSTEM_PROMPT.md`. The worker may edit only the scope declared below. It may not self-promote the result to `VERIFIED`, `PRODUCTION-PROVEN`, Mainline, or Annual Stable.

## 2. Execution Order

Complete the batches serially. Stop after any failed exit gate; do not hide the failure by continuing.

### Batch A — P0 Automated Writeback Containment

Objective: make it impossible for automated recommendations to enter reusable approved Craft knowledge without an explicit, evidence-bearing promotion.

Required investigation:

- `data_loop_runner._writeback_craft()`
- `product_integration.write_craft_learning_feed()`
- all readers, APIs, and CLI paths that expose or promote Craft records

Required behavior:

1. Automated output is stored in an explicitly unapproved proposal namespace.
2. Its default state is `proposal`/`pending`; it is never implicitly `candidate`, `stable`, `adopted`, approved, or production-eligible.
3. Approved Craft readers cannot return proposals as approved knowledge.
4. Promotion is a separate explicit operation requiring:
   - rights evidence;
   - identified human reviewer and review timestamp;
   - source run ID;
   - regression evidence;
   - traceable proposal identity.
5. Missing, malformed, mismatched, or replayed evidence fails closed.
6. Repeated execution is deterministic or explicitly idempotent and cannot duplicate an approved record.

Required tests:

- direct-function bypass;
- API bypass when the capability has an API surface;
- CLI bypass when the capability has a CLI surface;
- repeated execution and replay;
- approved-reader isolation;
- malformed and mismatched evidence.

Exit gate: no automated recommendation can appear as reusable approved Craft knowledge without explicit promotion evidence.

### Batch B — P1 Atomic Treatment Pair and Interruption Recovery

Objective: prevent Treatment JSON and Markdown from ever being presented as a mixed-generation current pair.

Required behavior:

1. Generate both artifacts in a run-scoped temporary location.
2. Validate both before either becomes current.
3. Use a recoverable transaction marker or equivalent explicit state protocol.
4. Recover deterministically from interruption:
   - before first promotion;
   - between promotions;
   - after promotion and before cleanup.
5. Preserve source inputs and the complete previous pair.
6. Retry must converge without duplicate or mixed current artifacts.

Required tests:

- fault injection at each boundary above;
- retry after every injected fault;
- current-pair consistency checks;
- source immutability checks;
- stale temporary-state recovery.

Exit gate: every injected interruption exposes either the complete previous pair or the complete new pair, never a mixed pair as current.

### Batch C — P1 Historical Compatibility Fixtures

Objective: turn compatibility claims into executable evidence.

Required fixtures:

- representative v0.1 Treatment;
- v2 Workspace;
- rights manifest;
- approval record;
- delivery record.

Use synthetic metadata only. Do not copy private audio or user data into fixtures.

Required behavior and tests:

1. Declare supported schema versions in one authoritative location.
2. For each fixture, demonstrate one explicit outcome: exact load, evidence-bearing migration, or actionable rejection.
3. Preserve unknown fields unless the schema contract explicitly forbids them.
4. Never overwrite the original historical artifact during migration.
5. Record migration lineage, source version, target version, tool/code identity, time, and source identity/hash.
6. Failed migration leaves the source intact and no falsely complete target.

Exit gate: every frozen fixture loads, migrates with lineage, or fails with a documented actionable reason.

## 3. Allowed Changes

- The smallest runtime/core modules necessary for Batches A–C.
- Tests and synthetic fixtures directly covering Batches A–C.
- This task pack's `ENGINEERING_LOG.md` and `HANDOFF.md`.
- Existing authoritative schema/version documentation only when required by an implemented contract.

## 4. Forbidden Changes

- Product positioning, creator-facing workflows, artistic direction, signing, or artist operations.
- Audio rights approval or professional listening approval.
- MRS authority or release standards.
- Unrelated refactors, formatting sweeps, dependency upgrades, or new frameworks.
- Destructive Git commands, pushes, remote operations, uncontrolled staging, branch changes, test deletion, or weakening assertions.
- Processing private, rights-pending, or unidentified audio.
- Editing `DSK-MFY-THICKNESS-001/03_DEEPSEEK_SYSTEM_PROMPT.md` to relax its audit-worker constraints.
- Declaring final acceptance, `PRODUCTION-PROVEN`, or release readiness.

## 5. Working-Tree and Evidence Rules

1. Inspect `git status --short`, current branch, and applicable `AGENTS.md` before editing.
2. Treat all pre-existing changes as user-owned; do not revert or overwrite them.
3. Use repository evidence before assumptions. Do not invent files, test results, rights, or historical versions.
4. Prefer the smallest complete patch. New abstraction is justified only by a tested invariant.
5. Never weaken or delete a test to get green.
6. Log each batch as work occurs: files, decisions, exact commands, exit codes, counts, warnings, limitations.
7. State what tests do not prove. Automated tests do not prove sound quality or production operation.
8. Follow `GIT_CHECKPOINT_PROTOCOL.md`. Commits are permitted only as task-scoped local recovery checkpoints after a Codex-created baseline checkpoint exists.
9. Never use `git add .`, `git add -A`, wildcard staging, `git commit -a`, stash, reset, clean, checkout-discard, rebase, or amend.

## 6. Verification Economy

To reduce token and compute waste:

1. Search narrowly with `rg`/`rg --files`.
2. Run focused tests during implementation.
3. Run the affected subsystem suite at each batch exit.
4. Run Runtime and root regression suites once after all completed batches.
5. Do not repeatedly paste full logs; record commands, exit codes, counts, and only relevant failure excerpts.

If an unrelated baseline failure appears, reproduce it without the patch when safely possible, record it, and stop claiming the affected gate. Do not repair unrelated work without authorization.

## 7. Required Handoff

DeepSeek must finish by writing:

- `ENGINEERING_LOG.md` — chronological evidence;
- `HANDOFF.md` — concise summary using the schema below.

`HANDOFF.md` must contain:

1. batches attempted and gate decision (`PASS`, `REWORK`, or `HOLD`);
2. changed files grouped by batch;
3. invariants implemented;
4. exact verification commands, exit codes, pass/fail/skip counts, and warnings;
5. fault-injection and recovery evidence;
6. compatibility fixture outcomes;
7. pre-existing changes preserved;
8. untested areas and remaining risks;
9. questions requiring Codex or human judgment;
10. exact next action.

After writing the handoff, stop. Codex will inspect the diff and independently rerun acceptance tests.

## 8. Budget Guidance

- Recommended DeepSeek context budget: 120k–220k tokens total, used serially.
- Expected active implementation time: approximately 8–14 hours, depending on repository coupling and baseline failures.
- Recommended human cadence: one batch per four-hour work block; do not compress all gates into a superficial single pass.

These are planning bounds, not completion targets. Evidence quality controls completion.
