# Codex Execution Prompt

Execute **Moodify Protocol Genesis 002 — Genesis Registration** inside the existing Moodify repository.

## Goal

Build the first public participation gateway:

`/genesis`
→ Connect Wallet
→ BNB Chain
→ One-time nonce
→ Human-readable wallet signature
→ Server verification
→ Genesis Participant record
→ `Genesis Participant #XXXX`

No token is sent in this package.

## Dependency

First confirm `MOOD-GENESIS-001` or its equivalent has established the official MOOD configuration.

Official token context:

- Network: BNB Smart Chain
- Chain ID: 56
- Token: Moodify / Mood
- Contract: `0x1BB3115D43E397f7bb586F090831B02cA639e73E`

The token contract is informational only for this package.

## Mandatory first step: audit

Before editing:

1. read repository instructions and canon;
2. inspect git status and preserve unrelated changes;
3. locate active web app;
4. identify Next.js routing style;
5. identify D1/Drizzle schema + migration conventions;
6. identify existing wallet/web3 packages;
7. identify existing auth/rate-limit/util patterns;
8. identify build/test commands;
9. inspect Package 001 implementation if present.

Do not create duplicate infrastructure when an existing abstraction can be reused.

## Implementation requirements

### Public page

Create `/genesis`.

It must contain:
- clear Genesis explanation;
- connect wallet;
- BNB Chain state;
- sign registration action;
- progress/error states;
- successful participant card.

### Signature flow

Prefer SIWE/EIP-4361 if cleanly compatible with the existing stack.

Otherwise implement a minimal secure message signature flow with:

- domain;
- wallet;
- chain ID 56;
- nonce;
- issued-at;
- expires-at;
- terms version;
- explicit statement that signing authorizes no token transfer.

Nonce must be server-generated, cryptographically random, short-lived and one-time-use.

### Backend

Create repository-consistent equivalent of:

- `POST /api/genesis/nonce`
- `POST /api/genesis/register`
- optional read endpoint/server action for existing registration.

Validate all input server-side.

Registration transaction must:
- verify nonce;
- verify expiry;
- verify signature;
- normalize recovered signer;
- prevent replay;
- prevent duplicate participant;
- allocate race-safe participant number;
- mark nonce consumed atomically where possible.

### Database

Add non-destructive schema/migration for:
- `genesis_participants`
- `genesis_nonces`

Enforce unique wallet at database level.

### Safety

Absolutely do not:
- transfer MOOD;
- approve MOOD;
- deploy a contract;
- create a claim contract;
- ask for private key;
- store seed phrase;
- sign a blockchain transaction;
- implement referral rewards;
- implement token allocation;
- fabricate participants.

### Tests

Add tests for:
- valid registration;
- invalid signature;
- signature from wrong wallet;
- wrong chain;
- expired nonce;
- used nonce;
- duplicate wallet;
- concurrent duplicate registration;
- malformed address;
- already registered lookup;
- wallet signature rejection UI if testable.

Run:
- lint;
- typecheck;
- tests;
- production build;
- migration validation/dry-run where available.

## Completion report

Return:

1. repository audit;
2. architecture choices;
3. files changed;
4. migration details;
5. signature example;
6. test results;
7. screenshots/local render evidence;
8. security notes;
9. git diff summary;
10. this exact safety statement:

`No MOOD token transfer, token approval, smart-contract deployment, wallet transaction, liquidity operation, or private-key handling was performed by this task.`

## Stop conditions

Stop and request human input if:
- a canon conflict exists;
- Package 001 official contract does not match;
- a destructive migration is required;
- production wallet credentials are requested;
- a library requires unsafe wallet permissions;
- deployment or payment is required.
