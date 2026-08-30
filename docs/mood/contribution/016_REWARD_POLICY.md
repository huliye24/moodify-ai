# MOOD CONTRIBUTION 016 — Reward Policy

**Authority:** 016 TASK.md Phase H

## Hard rule

**Pending Reward has no chain side effect.**

There is no:

- ❌ automatic chain transfer
- ❌ claim flow
- ❌ distributor contract deployment
- ❌ token mint
- ❌ wallet payout
- ❌ guaranteed MOOD wording

## What 016 records

`PendingRewardEvent`:

```ts
{
  id, residentId, submissionId,
  rewardUnits: string,           // stringly-typed; never on-chain
  status: "pending" | "included_in_future_snapshot" | "cancelled",
  createdAt, updatedAt, reason?,
}
```

The field name `rewardUnits` is intentional. It is **historical field naming**;
it does **not** represent a present on-chain entitlement. Any future Token
distribution must be a separate package (e.g. 025) and must include:

- explicit Governance approval,
- explicit human signature,
- a snapshot dataset,
- a public evidence trail.

## Status transitions

- `pending` — initial state on approve.
- `included_in_future_snapshot` — operator action (future package).
- `cancelled` — operator action (e.g. task retraction).

## Idempotency

`INV-016-05`: each submission records exactly one PendingRewardEvent. A second
approve on the same submission is a no-op.

## Implementation

`apps/web/lib/mood/contribution/pending-reward.ts`.

## What this is NOT

- This is **not** a Token allocation.
- This is **not** an entitlement.
- This is **not** a smart-contract commitment.

It is an off-chain count that lets the network surface "this many approved
contributions across the protocol" without confusing it with Token issuance.