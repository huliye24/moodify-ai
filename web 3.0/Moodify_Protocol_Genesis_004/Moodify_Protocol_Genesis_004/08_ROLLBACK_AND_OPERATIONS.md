# Rollback and Operations
## Distribution Engine

### Git

Suggested commit:

```text
feat(protocol): add genesis distribution engine
```

### Artifact retention

Do not casually delete approved snapshot artifacts.

Recommended:
- development snapshots may be regenerated;
- approved production snapshots are immutable records;
- later corrections should create a new snapshot ID/version.

### No DB mutation

Package 004 should be read-only against participant/allocation records unless the project explicitly adds a harmless metadata record for snapshot tracking.

If snapshot tracking table is introduced:
- it must be additive;
- it must not alter participant allocation;
- it must record snapshot ID/hash/root/status only.

### Snapshot lifecycle

Suggested future states:

```text
draft
reviewed
approved
superseded
```

Package 004 may support `draft`; human approval process determines later state.

### Artifact location

If repository policy forbids committing generated artifacts:
- store them under ignored artifact/output path;
- commit schemas, fixtures and generator code only;
- document secure retention location.

Follow repo policy instead of forcing generated outputs into Git.
