# Node Lifecycle State Machine

## States

```text
draft
registered
pending_verification
verified
active
degraded
inactive
suspended
rejected
retired
```

## Core transitions

```text
draft -> registered
registered -> pending_verification
pending_verification -> verified
pending_verification -> rejected
verified -> active
active -> degraded
active -> inactive
active -> suspended
active -> retired
degraded -> active
degraded -> inactive
degraded -> suspended
inactive -> active
inactive -> pending_verification
inactive -> retired
suspended -> pending_verification
suspended -> retired
```

## Rules

- `rejected` cannot become active without a new registration/review path.
- `retired` is terminal for that node identity unless future policy explicitly allows restoration.
- heartbeat alone must not unsuspend a policy-suspended node.
- verification and health are separate.
- lifecycle history must be retained.

## Reason codes

Every transition should retain:

- previous state
- next state
- timestamp
- reason code
- authority/source
- evidence reference when applicable
