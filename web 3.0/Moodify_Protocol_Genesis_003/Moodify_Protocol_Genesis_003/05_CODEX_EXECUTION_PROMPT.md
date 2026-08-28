# Codex Execution Prompt

Execute **Moodify Protocol Genesis 003 — Genesis Admin** inside the existing Moodify repository.

## Dependency

Confirm Package 001 and 002 foundations exist.

Expected registration data:

- Genesis participants
- unique participant number
- wallet address
- registration timestamp
- status
- contribution score
- allocation field or compatible extension

Official MOOD context:

- Network: BNB Smart Chain
- Chain ID: 56
- Contract: `0x1BB3115D43E397f7bb586F090831B02cA639e73E`

No blockchain write is needed for this task.

## Mission

Build a secure internal control plane for reviewing Genesis participants and assigning provisional MOOD allocations.

Target:

`/admin/genesis`

Admin should be able to:

- see participant overview;
- search/filter;
- inspect participant;
- change reviewed/eligible/rejected/allocated status;
- change contribution score;
- assign provisional allocation;
- add internal note;
- see complete audit history;
- export deterministic CSV/JSON.

## Mandatory audit before editing

1. Read repo instructions/canon.
2. Inspect git status.
3. Preserve unrelated changes.
4. Inspect Package 002 implementation.
5. Inspect auth system.
6. Inspect admin routes.
7. Inspect D1/Drizzle schema.
8. Inspect current UI/table/dialog components.
9. Inspect existing CSV/JSON export helpers.
10. Identify test/build commands.

If no safe admin auth exists, design the smallest secure solution consistent with current architecture.

Do not use a client-only admin flag.

## Data model

Implement/extend:

- `genesis_admin_events`
- `genesis_admin_notes`
- participant fields needed for status/score/allocation

Audit events must record:

- participant;
- actor;
- event type;
- field;
- old value;
- new value;
- reason;
- timestamp.

Use DB transactions for mutation + audit wherever possible.

## Status model

Allowed core states:

- registered
- reviewed
- eligible
- allocated
- rejected

Validate transitions server-side.

Do not pretend `distributed` or `claimed` occurred.

## Allocation

Allocation is off-chain and provisional.

Rules:

- exact arithmetic only;
- no float-based token accounting;
- non-negative;
- configurable Genesis pool ceiling;
- total allocation enforced server-side;
- if no approved production pool ceiling exists, do not invent one.

If production allocation cannot safely be enabled without a human-approved pool ceiling, implement the UI/data model in disabled/readiness mode and report the stop condition.

## Admin UX

Implement:

### Overview cards
- registered
- reviewed
- eligible
- allocated
- rejected
- total provisional MOOD

### Participant table
- participant #
- wallet
- joined
- status
- contribution score
- allocation
- updated

### Detail
- immutable identity
- BscScan wallet link
- admin note
- audit timeline
- controlled edit actions

### Export
CSV and JSON.

Do not export:
- raw signatures;
- internal notes;
- auth/session data.

## Hard prohibitions

Do not:

- transfer MOOD;
- approve MOOD;
- call MetaMask;
- create transactions;
- deploy contracts;
- add liquidity;
- remove liquidity;
- use token price to determine allocation;
- create fake participants;
- fabricate contribution scores.

## Tests

At minimum test:

- unauthorized read denied;
- unauthorized mutation denied;
- allowed status transition;
- invalid status transition;
- score update audit;
- allocation update audit;
- negative allocation rejected;
- pool ceiling enforced;
- concurrent allocation updates maintain integrity;
- rejected participant allocation guard;
- notes remain private;
- export deterministic;
- export contains no signatures/notes;
- pagination/filter/search;
- migration preserves Package 002 rows.

Run:
- lint;
- typecheck;
- tests;
- production build;
- migration validation.

## Completion output

Return:

1. audit findings;
2. auth strategy;
3. schema changes;
4. files changed;
5. status model;
6. allocation ceiling behavior;
7. export schema;
8. tests/build results;
9. screenshots;
10. git diff summary;
11. exact safety statement:

`No MOOD token transfer, token approval, wallet signature, smart-contract deployment, liquidity operation, or private-key handling was performed by this task.`

## Stop conditions

Stop for human confirmation if:

- admin identity cannot be securely determined;
- canon conflicts;
- destructive migration required;
- production allocation ceiling is undefined and allocation writes would otherwise go live;
- any wallet credential/payment/signature is requested.
