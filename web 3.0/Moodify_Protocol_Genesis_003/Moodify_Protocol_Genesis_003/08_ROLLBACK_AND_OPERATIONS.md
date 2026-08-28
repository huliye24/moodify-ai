# Rollback and Operations
## Genesis Admin

### Git

Suggested commit:

```text
feat(protocol): add genesis admin control plane
```

All code changes should be reversible through Git.

### Database

Package 003 should be additive/non-destructive.

Never:
- renumber existing participants;
- delete Package 002 registrations;
- drop audit rows containing real history.

If rollback is required after real admin usage, prefer disabling the UI rather than deleting historical audit data.

### Allocation configuration

Genesis allocation ceiling must be configuration-driven and documented.

If not approved:
- production mutation should remain disabled or explicitly blocked;
- admin can still review participants and scores.

### Audit retention

Treat audit events as durable protocol-operational history.

### Backups

If the project has D1 export/backup operations, document a pre-production backup step before applying migrations.

Do not invent a backup mechanism if Cloudflare tooling is not currently configured; document the gap instead.

### Human boundary

Package 003 never authorizes or executes asset movement.
