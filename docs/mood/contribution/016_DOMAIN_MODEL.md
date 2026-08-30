# MOOD CONTRIBUTION 016 — Domain Model

**Package:** `MOOD-CONTRIBUTION-016`
**Authority:** 016 TASK.md Phase C

## Purpose

The Contribution Network binds real Resident activity to verifiable Records.
Every contribution has:

1. a Task (the ask)
2. a Submission (the work)
3. Evidence (proof)
4. Review (human decision)
5. Reputation (append-only consequence)
6. Pending Reward (off-chain accounting only)
7. Audit Event (immutable trail)

All Records are owned by Resident.id. Wallet address is never the primary id.

## Canonical Entities

### `ContributionTask`

```ts
{
  id, slug, title, summary, description,
  category: code | audio-testing | dataset | research | documentation
         | translation | bug-report | community | other,
  status: draft | active | paused | completed | archived,
  evidenceRequirements: string[],
  defaultReputationPoints: number,
  defaultRewardUnits?: string,        // historical naming; not on-chain
  deadline?: string,
  maxApprovals?: number,
  createdByResidentId, createdAt, updatedAt,
}
```

### `ContributionSubmission`

```ts
{
  id, taskId, residentId, summary,
  evidenceText?: string,
  status: submitted | under_review | changes_requested | approved | rejected | withdrawn,
  revision: number,
  reviewedByResidentId?, reviewedAt?, reviewerNote?,
  createdAt, updatedAt,
}
```

### `ContributionEvidence`

```ts
{
  id, submissionId,
  type: url | github-pr | github-commit | document | artifact | text,
  value: string,                  // url or text
  label?: string,
  createdAt,
}
```

### `ReputationEvent`

Append-only. Created on approve. Compensated via `adjust()` (new event, not mutation).

### `PendingRewardEvent`

Append-only. Status: `pending` → `included_in_future_snapshot` → `cancelled`.
**No chain side effect.**

### `ContributionAuditEvent`

Append-only. Records every state change, decision, reputation grant, reward record.

## Decisions

- **Resident ID**: every entity binds via `residentId` (or `createdByResidentId`/`reviewedByResidentId`). Wallet address is not a primary ID.
- **Reward units** are strings: we do not encode any on-chain semantics. The schema never references a token contract.
- **Reviewer notes** are stored on the submission record but stripped from public serializers.
- **Audit** is closed-form: actor + timestamp + previous + next + reason.

## Non-goals

- No DAO voting.
- No Token gating of tasks.
- No chain settlement of any kind.
- No automated AI approval (suggestion only).
- No deletion / redaction — corrections only via adjustment events.