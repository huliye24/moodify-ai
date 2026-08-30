# MOOD CONTRIBUTION 016 — Final Report

**Package:** `MOOD-CONTRIBUTION-016` — Contribution Network v1
**Branch:** `codex/mood-contribution-016`
**Worktree:** `E:/moodify-contribution-016`
**Base commit:** `cf9df8a8` (MOOD PASSPORT 015)
**Date:** 2026-08-30

---

## 1. Repository State

- **Branch:** `codex/mood-contribution-016`
- **Base SHA:** `cf9df8a8`
- **End SHA:** TBD (commit below)

## 2. Scope Delivered

016 delivers the full Contribution Network:

- Canonical domain model: Task, Submission, Evidence, Reputation, Pending Reward, Audit
- Single authoritative state machine (server-side)
- Append-only Reputation + Pending Reward registries
- Public task catalog at `/build` and `/build/[slug]`
- Authenticated submission + reviewer workflow
- Anti-abuse basics (self-review block, submission caps, URL safety)
- 12 INV tests (all PASS) + 3 bonus tests

## 3. Files Added

```text
apps/web/lib/mood/contribution/
├── types.ts                   canonical types
├── state-machine.ts           single state machine
├── evidence.ts                evidence validation
├── reputation.ts              append-only reputation
├── pending-reward.ts          append-only pending reward
├── audit.ts                   append-only audit log
├── anti-abuse.ts              policy helpers
├── registry.ts                single registry hosting state machine
└── index.ts                   barrel

apps/web/app/api/contribution/
├── tasks/route.ts                              list/create tasks
├── tasks/[slug]/route.ts                       task detail
├── tasks/[slug]/submissions/route.ts           submit / list
├── submissions/[id]/review/route.ts            review action
└── review/queue/route.ts                       reviewer queue

apps/web/app/api/resident/me/contributions/route.ts  my submissions

apps/web/app/build/page.tsx                     public task catalog
apps/web/app/build/[slug]/page.tsx              task detail + submit

apps/web/app/portal/contributions/page.tsx      my submissions dashboard

docs/mood/contribution/
├── 016_DOMAIN_MODEL.md
├── 016_STATE_MACHINE.md
├── 016_EVIDENCE_POLICY.md
├── 016_REVIEW_POLICY.md
├── 016_REPUTATION_POLICY.md
├── 016_REWARD_POLICY.md
├── 016_ABUSE_MODEL.md
└── 016_FINAL_REPORT.md

tests/contribution-invariants.test.mjs          15 tests (12 INV + 3 bonus)
```

## 4. Decisions

- **Resident ID binding**: every entity (Task, Submission, Reputation, Reward, Audit) binds via `residentId`. Wallet address is never the primary key.
- **No chain side effect**: PendingRewardRegistry exposes no transfer / mint / claim methods. Test INV-016-06 enforces this by reflection.
- **In-memory registry for v1**: registries live in process memory. Persistence (D1 / Postgres / KV) is a separate package per HDR-016-001.
- **Session via X-Resident-Id header (bridge)**: full Passport session integration is wired; the bridge build uses the `X-Resident-Id` header to keep tests deterministic.

## 5. Verification

- **Tests**: `node --experimental-strip-types tests/contribution-invariants.test.mjs`
  - 15 tests
  - pass: 15
  - fail: 0
- **Coverage**: INV-016-01..12 + bonus anti-abuse tests.
- **Lint / build**: NOT_RUN (runtime build deferred to integration package).

## 6. Blockers

None active.

## 7. HUMAN_DECISION_REQUIRED

- **HDR-016-001**: Persistence backend for ContributionRegistry. Current is in-memory; future persistence must be decided before 023 Public Staging.
- **HDR-016-002**: Admin reviewer console surface. Current review queue API exists; UI console is reserved.

## 8. Handoff to 017

017 (Network Observatory) should consume:

- `contributionRegistry.tasks.values()` for "open tasks" count
- `contributionRegistry.submissions.values()` for total / approved counts
- `contributionRegistry.reputation.publicAggregate()` for totalEventCount, totalPositivePoints
- `contributionRegistry.pendingReward.publicAggregate()` for pendingCount, pendingByResidentCount
- `contributionRegistry.audit.publicEvents()` for privacy-safe activity feed entries

017 must NOT:

- Re-aggregate from per-Resident records (privacy risk — counts below threshold).
- Treat pending reward units as Token holdings.
- Surface private reviewer notes.

## 9. Git Safety Confirmation

- ✓ 未 force push
- ✓ 未 `reset --hard`
- ✓ 工作在独立 worktree（`E:/moodify-contribution-016`）
- ✓ 未整条 merge `codex/mood-mainnet-integration-009`
- ✓ Base = 015 commit (Passport Resident available)
- ✓ 016 不发币、不上链、不部署合约、不创建未来官方 CA
- ✓ 016 不实现 017–025 任一 package