# MOOD CONTRIBUTION 016 — Reputation Policy

**Authority:** 016 TASK.md Phase G

## Properties

- **Non-transferable** — `ReputationEvent.residentId` is a Resident ID. There is no
  mechanism to transfer points between Residents.
- **Off-chain v1** — Reputation lives in the in-memory registry. No on-chain record is
  produced.
- **Append-only** — Events are never mutated. Corrections only via new adjustment events.

## Grant flow

```text
Submission approved
  → ReputationRegistry.recordEvent({ pointsDelta: task.defaultReputationPoints, source: "contribution" })
  → Returns new ReputationEvent
  → INV-016-04: same submissionId cannot grant twice
```

## Adjustment flow

```text
Correction required
  → ReputationRegistry.adjust({ pointsDelta: <signed>, reason: "...", source: "system-adjustment" })
  → New compensating event (never mutates prior)
  → Cached aggregate recomputes from event sum
```

## Aggregation

`aggregateFor(residentId)` returns a `ResidentReputation`:

```ts
{
  score,                  // sum of pointsDelta
  lastEventAt,
  contributionCount,      // distinct submissionIds
  approvedContributionCount,
  source: "events" | "no-contributions-yet",
}
```

`INV-016-07`: cached aggregate MUST equal sum of events for the resident.

## Public aggregate (for /network)

`publicAggregate()` returns only:

- `totalEventCount`
- `totalPositivePoints`

Internal adjustment reasons are never exposed.

## What is NOT in Reputation

- Wallet balance / token holding.
- Network stake / lockup.
- Manual override outside the audit trail.

## Implementation

`apps/web/lib/mood/contribution/reputation.ts`.