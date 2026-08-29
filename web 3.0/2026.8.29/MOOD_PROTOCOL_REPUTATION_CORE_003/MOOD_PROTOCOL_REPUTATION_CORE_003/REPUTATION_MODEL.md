# Reputation Model

## What reputation means

Protocol Reputation is:

> A compact, auditable summary of a contributor's verified protocol history under a known policy version.

It is NOT:

- social popularity
- follower count
- financial balance
- market price
- moral score
- legal identity
- KYC status

## Dimensions

The five core dimensions remain:

```text
Contribution
Impact
Quality
Persistence
Early
```

### Contribution

How much meaningful verified work exists.

### Impact

How useful or consequential verified work was under policy.

### Quality

How correct, rigorous, reliable, or maintainable verified work was.

### Persistence

How sustained contribution is across time.

### Early

Whether the contribution occurred in objectively defined early protocol epochs.

## History vs snapshot

History:

```text
all eligible finalized contribution records
```

Snapshot:

```text
a policy-pinned view of that history for an epoch
```

Never treat a snapshot as the raw history.

## Missing aggregate

If no authoritative weighting exists:

```json
{
  "dimensions": {
    "contribution": 74,
    "impact": 61,
    "quality": 88,
    "persistence": null,
    "early": 100
  },
  "aggregate": null
}
```

This is valid.

Do not invent a number just to make UI simpler.
