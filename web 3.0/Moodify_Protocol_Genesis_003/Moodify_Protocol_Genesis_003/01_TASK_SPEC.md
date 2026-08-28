# Task Specification
## Genesis Admin

### 1. Mission

Build the internal administration layer for Moodify Genesis.

Package 002 created registration.

Package 003 creates review and allocation control.

The system must support the transition:

```text
registered
→ reviewed
→ eligible
→ allocated
```

Future packages may add:

```text
distributed
claimed
```

Do not implement on-chain distribution here.

### 2. Required admin route

Preferred:

`/admin/genesis`

Use the repository's existing admin routing conventions if present.

Required views:

#### A. Overview
Show:

- total registered;
- reviewed;
- eligible;
- allocated;
- rejected;
- total provisional MOOD allocation;
- unallocated eligible participants;
- latest registrations.

#### B. Participant table
Columns should include:

- Participant #
- wallet
- joined at
- status
- contribution score
- provisional allocation
- claim/distribution state if already present in schema
- last updated

Actions:

- view;
- review;
- edit score;
- edit allocation;
- change status;
- add note.

#### C. Participant detail
Show:

- immutable participant number;
- full wallet address;
- BscScan link;
- registration timestamp;
- signature/terms version metadata;
- current status;
- contribution score;
- provisional allocation;
- internal notes;
- complete audit history.

### 3. Status model

Recommended allowed states:

```text
registered
reviewed
eligible
allocated
rejected
```

Future-compatible values may include:

```text
distributed
claimed
```

But Package 003 must not pretend on-chain distribution occurred.

Required transition rules:

- `registered` → `reviewed`
- `reviewed` → `eligible`
- `reviewed` → `rejected`
- `eligible` → `allocated`
- `allocated` → `eligible` only with explicit reason if allocation is removed/changed
- `rejected` should not receive allocation unless explicitly restored through an audited action

Do not allow arbitrary free-text status values.

### 4. Allocation model

Allocation means:

> an off-chain provisional amount of MOOD assigned for future distribution.

It does **not** mean:
- token has been sent;
- token is claimable;
- token has market value;
- participant owns the tokens already.

Requirements:

- exact decimal handling;
- never use floating point for token amounts;
- store canonical atomic/string representation if consistent with repo;
- validate non-negative allocation;
- define a package-level configurable Genesis pool ceiling;
- total provisional allocation must never exceed that ceiling;
- admin UI must show total allocated / pool ceiling.

If the Genesis pool size is not yet approved in project canon:
- do not invent a production number;
- support configuration;
- default to a disabled/unset state or clearly labeled local development value;
- stop before production if allocation ceiling is missing.

### 5. Contribution score

Package 003 only provides a simple administrative score.

Requirements:

- integer score;
- default 0;
- cannot be modified silently;
- every change creates an audit event;
- score is not automatically convertible to MOOD yet.

Package 006 will formalize the contribution network.

### 6. Internal notes

Add admin-only notes.

Recommended fields:

```text
id
participant_id
author_admin_id
body
created_at
```

Notes must never appear on public participant pages.

### 7. Audit log

Create a first-class audit table.

Suggested:

`genesis_admin_events`

Fields:

```text
id
participant_id
actor_id
event_type
field_name
old_value
new_value
reason
created_at
metadata_json_optional
```

Events to audit:

- status change;
- contribution score change;
- allocation change;
- rejection;
- restoration;
- admin note creation;
- bulk eligibility change;
- bulk allocation change if supported.

Audit history must be append-only at application level.

Do not expose a delete button for audit events.

### 8. Authentication and authorization

Use existing admin authentication if available.

If no admin system exists:

1. inspect current user/auth architecture;
2. implement the smallest secure admin gate consistent with the project;
3. prefer allowlisted authenticated identities over a shared password;
4. do not ship hard-coded passwords;
5. do not rely only on hidden URLs;
6. do not trust client-side `isAdmin`.

Authorization must be checked server-side for every mutation.

### 9. Search and filters

Support:

- wallet address;
- participant number;
- status;
- joined date where reasonable.

Pagination or virtualized table is required if current design patterns support it.

Target usable range:

10–1,000 participants initially.

### 10. Bulk operations

Safe bulk operations allowed:

- mark reviewed;
- mark eligible;
- export selected.

Optional:
- bulk set allocation only if accompanied by a clear preview and audit reason.

No bulk transfer.

### 11. Export

Required:

#### CSV
At minimum:

```text
participant_number
wallet_address
status
contribution_score
allocation_mood
joined_at
updated_at
```

#### JSON
Equivalent canonical fields plus metadata.

Exports must:
- be deterministically ordered;
- normalize wallet addresses;
- not expose raw signatures;
- not expose internal notes;
- include export timestamp;
- include schema/version.

### 12. Allocation integrity

Provide summary validation:

- number of allocated participants;
- total provisional MOOD;
- minimum allocation;
- maximum allocation;
- zero-allocation eligible participants;
- duplicate wallet check;
- invalid state/allocation combinations.

### 13. UI requirements

Preserve Moodify visual system.

Admin UI should feel operational and quiet, not like a trading dashboard.

Required UX:

- destructive/rejection actions require confirmation;
- allocation changes show old/new values;
- reason field required for sensitive changes;
- optimistic UI only if rollback-safe;
- visible saved/error state.

### 14. Documentation

Create:

`docs/protocol/GENESIS_ADMIN.md`

Document:

- admin role;
- status model;
- allocation semantics;
- audit model;
- export format;
- security boundary;
- what remains off-chain;
- relationship to Package 004.

### 15. Explicit non-goals

Do not implement:

- MOOD transfers;
- Merkle tree;
- claim smart contract;
- wallet signing;
- Treasury signing;
- liquidity changes;
- public referral system;
- automatic reward formula;
- token-price based allocation.
