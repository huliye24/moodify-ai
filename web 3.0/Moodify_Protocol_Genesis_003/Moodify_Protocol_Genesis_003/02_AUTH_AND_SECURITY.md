# Authentication and Security
## Genesis Admin

### Core principle

Every sensitive read or mutation in `/admin/genesis` must be authorized server-side.

A hidden route is not authentication.

### Required authorization controls

Use existing project authentication if present.

Admin authorization should resolve to a stable internal identity.

Recommended pattern:

```text
authenticated user
→ server-side admin role/allowlist check
→ authorized admin action
```

Do not use:

```text
localStorage.isAdmin = true
```

or a client-only environment flag.

### Mutation security

For all mutations:

- validate request schema;
- authenticate actor;
- authorize actor;
- load current DB state;
- validate transition;
- execute DB transaction;
- append audit event;
- return updated state.

Where possible, allocation/status update + audit event must happen in the same DB transaction.

### Allocation safety

Allocation is sensitive protocol data.

Controls:

- exact integer/decimal parsing;
- upper bound;
- total pool ceiling;
- no negative values;
- no NaN;
- no scientific notation ambiguity;
- no client-calculated total trusted by server;
- all totals recomputed server-side.

### Notes privacy

Internal notes may contain operational context.

Never:
- include them in public API responses;
- include them in exports;
- index them into public pages;
- expose them in client bundle prefetch for unauthorized users.

### Audit integrity

Audit log is append-only at application level.

No regular admin UI action may:
- edit an audit row;
- delete an audit row;
- rewrite historical values.

### Rate limiting / abuse

Admin mutations should use existing rate limit / CSRF / session protections where applicable.

### Logging

Log operational metadata, not secrets.

Do not log:
- private keys;
- seed phrases;
- auth tokens;
- raw participant signatures unless essential and already safely handled.

### Stop conditions

Stop and request human confirmation if:

- no safe admin authentication can be established;
- production admin identity is unknown;
- a destructive migration is required;
- allocation ceiling is required for production but no approved value exists;
- existing auth canon conflicts with implementation.
