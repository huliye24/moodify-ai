# Architecture — Reputation Core

## Position

```text
      MPF-002
Finalized Contributions
        │
        ▼
Reputation Evidence
        │
        ▼
┌──────────────────────┐
│ MPF-003 Reputation   │
│ Core                 │
└──────────────────────┘
        │
        ├── Contributor Profile
        ├── Identity Links
        ├── Epoch Aggregation
        ├── Persistence Evidence
        ├── Reputation Snapshot
        └── Snapshot Attestation
        │
        ▼
   Protocol Identity

        │
        │ future boundary
        ▼

 Protocol Rights
        ↓
       MOOD
```

## Design goals

### Evidence-derived

Reputation must be traceable back to contribution IDs and evidence fingerprints.

### Versioned

Every snapshot pins:
- schema version
- policy version
- epoch policy version
- input fingerprints

### Non-economic

Reputation must be useful before token economics exist.

### Portable

A contributor's protocol identity should survive:
- frontend replacement
- storage migration
- node changes
- later chain integration

### No hidden mutation

History is append/supersede, not overwrite.
