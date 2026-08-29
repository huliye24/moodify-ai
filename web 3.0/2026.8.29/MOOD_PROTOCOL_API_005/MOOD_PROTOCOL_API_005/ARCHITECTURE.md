# Architecture — Protocol API

## Position

```text
 ┌─────────────┐
 │ MPF-001     │  Mainnet Facts
 └──────┬──────┘
        │
 ┌──────▼──────┐
 │ MPF-002     │  Contributions
 └──────┬──────┘
        │
 ┌──────▼──────┐
 │ MPF-003     │  Reputation
 └──────┬──────┘
        │
 ┌──────▼──────┐
 │ MPF-004     │  Nodes
 └──────┬──────┘
        │
        ▼
 ┌────────────────────┐
 │ MPF-005 Protocol API│
 └────────────────────┘
        │
   ┌────┼─────┐
   ▼    ▼     ▼
 Web  Transparency  Genesis
```

## Layering rule

```text
HTTP/API
  ↓
Application Service
  ↓
Protocol Domain
  ↓
Repository/Adapter
```

Never:

```text
HTTP Route
  ↓
Direct DB Mutation
```

for protocol-critical state.

## Read model

The API may build denormalized read models for fast public reads.

A read model:
- may aggregate authority;
- may cache authority;
- may index authority;

but must not redefine authority.

## Write model

A write command must call the canonical domain service from MPF-002/003/004.

The API itself should not create new state transitions.
