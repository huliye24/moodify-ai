# MIP Lifecycle

Single canonical lifecycle for all MIPs in the registry.

## State Diagram

```text
draft
  ↓
discussion
  ↓
review
  ├── accepted
  │      ↓
  │  implemented
  │
  └── rejected

draft → withdrawn
accepted → superseded
implemented → superseded
discussion / review / accepted / rejected / implemented
  ↓
archived (terminal)
```

## Forbidden Transitions

```text
draft → implemented
discussion → implemented
rejected → implemented
```

These are forbidden because a MIP must be **accepted** (with an explicit
decision record) before any implementation can be marked as completed.
Enforced by `INV-020-02` and `INV-020-03`.

## Required Preconditions

### Transition to `implemented`

1. The MIP must currently be in status `accepted`.
2. At least one `accepted` Decision record must exist
   (`INV-020-03`).
3. At least one Implementation reference must be recorded
   (`INV-020-04`).

### Transition to `accepted`

1. The MIP must currently be in status `review`.
2. An `accepted` Decision record must exist with actor IDs and rationale.

### Transition to `rejected`

1. The MIP must currently be in status `review`.
2. A `rejected` Decision record must exist with rationale.

### Transition to `superseded`

1. The MIP must currently be in `accepted` or `implemented` status.
2. The replacing MIP must already exist as a record.

## Auto-transitions

The `recordDecision` method automatically moves a MIP from `review` to
`accepted` / `rejected` / `draft` (returned-for-revision) based on the
decision type.

Other transitions are explicit calls to `transition()` so the audit event
captures the actor.

## Withdrawal

A MIP in `draft`, `discussion`, `review`, or `accepted` can be moved to
`withdrawn` by the author or a maintainer. Withdrawal is reversible only
via a new MIP, never by undoing the withdrawal record.
