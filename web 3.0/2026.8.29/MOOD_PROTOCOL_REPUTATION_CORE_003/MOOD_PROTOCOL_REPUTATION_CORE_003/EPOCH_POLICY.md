# Epoch Policy

## Why epochs exist

Reputation needs a stable time boundary so that persistence, early participation, and historical snapshots are reproducible.

## Recommended initial epochs

The implementation may use an approved existing policy.

If none exists, bootstrap as draft:

```text
GENESIS_2026
```

with explicit UTC boundaries.

Do not invent a production launch date if human approval is required.

## Epoch object

```json
{
  "epochPolicyVersion": "003-draft-1",
  "epochId": "GENESIS_2026",
  "startsAt": "2026-08-01T00:00:00Z",
  "endsAt": null,
  "status": "draft"
}
```

Dates in this file are examples only unless repository/human authority approves them.

## Rules

- UTC only
- inclusive/exclusive boundary behavior documented
- no local timezone dependence
- historical epoch definitions immutable after lock
- correcting an epoch requires a new policy version
