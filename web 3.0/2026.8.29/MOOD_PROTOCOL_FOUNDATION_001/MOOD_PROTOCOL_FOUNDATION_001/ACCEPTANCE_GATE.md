# MPF-001 Acceptance Gate

This is a **P0 release gate**. Do not mark the task complete by counting files. Mark it complete by proving the foundation is coherent.

## Gate 1 — Authority

- [ ] Root `AGENTS.md` and current Canon files were read before edits.
- [ ] `CANON_CHANGE = YES — protocol authority addition only` is recorded where repository policy requires.
- [ ] No unrelated product Canon was silently rewritten.
- [ ] Public protocol identity migration, if needed, is explicitly deferred or separately approved.

## Gate 2 — Single source of truth

- [ ] `protocol/mainnet.json` exists.
- [ ] `protocol/mainnet.schema.json` exists.
- [ ] Token identity has exactly one authoritative machine-readable source.
- [ ] Chain identity has exactly one authoritative machine-readable source.
- [ ] Treasury/genesis public-address facts, if known, have exactly one authoritative source.
- [ ] Docs are explanatory mirrors, not parallel authority.

## Gate 3 — Evidence

- [ ] Every locked canonical fact has an evidence reference.
- [ ] Deployed facts use verified deployed/public-chain evidence when available.
- [ ] Source/deployment commit is recorded when available.
- [ ] Conflicting facts are documented, not hidden.
- [ ] No value was guessed from naming conventions or stale documentation.

## Gate 4 — Validation

Run:

```bash
node scripts/validate-mainnet-config.mjs protocol/mainnet.json
```

Expected:

- [ ] valid JSON;
- [ ] valid schema version;
- [ ] address format matches declared chain family;
- [ ] decimals valid;
- [ ] total supply represented as atomic integer string;
- [ ] URLs valid;
- [ ] no duplicate RPC entries;
- [ ] no unresolved placeholders when locked;
- [ ] locked config contains `lockedAt` + `sourceCommit` + evidence.

## Gate 5 — Lock integrity

Only for `launch.status = locked`:

```bash
node scripts/generate-mainnet-lock.mjs protocol/mainnet.json protocol/mainnet.lock.json
```

Then verify:

- [ ] lock file exists;
- [ ] config SHA-256 matches current canonical file bytes;
- [ ] chain identity matches config;
- [ ] token identifier matches config;
- [ ] source commit matches config;
- [ ] regenerating without config changes yields the same fact identity/hash.

If status is draft:

- [ ] lock generation refuses to proceed;
- [ ] no misleading `mainnet.lock.json` is committed.

## Gate 6 — Runtime compatibility

- [ ] Existing Web3 read flow still builds/tests.
- [ ] Existing wrong-network protection still works.
- [ ] Existing claim code is not silently pointed at a new token/network.
- [ ] Public RPC override behavior, if retained, is documented.
- [ ] Production token/chain identity cannot be silently replaced by ordinary env vars.
- [ ] Legacy/testnet constants are clearly scoped.

## Gate 7 — Safety

- [ ] No private key added.
- [ ] No seed phrase added.
- [ ] No wallet secret added.
- [ ] No signed transaction created.
- [ ] No deploy performed.
- [ ] No transfer/mint/burn performed.
- [ ] No liquidity operation performed.
- [ ] No new unlimited token approval introduced.

## Gate 8 — Repository health

- [ ] relevant unit tests pass;
- [ ] relevant typecheck passes;
- [ ] relevant build passes;
- [ ] validator passes;
- [ ] changed-file diff reviewed for secrets and accidental scope expansion.

## Final report format

```text
MOOD Protocol Foundation 001 — RESULT

Base branch:
Work branch:
Commit:

MAINNET_LOCKED = TRUE | FALSE

Canonical facts:
- Chain:
- Chain ID / Cluster:
- Token contract/mint:
- Symbol:
- Decimals:
- Total supply atomic:
- Treasury:
- Genesis pool:
- Explorer:

Evidence:
- ...

Unresolved:
- NONE | HUMAN_DECISION_REQUIRED: ...

Files added:
- ...

Files modified:
- ...

Validation:
- ...

Tests/build:
- ...

Chain writes performed:
- NONE

Secrets handled:
- NONE

Next safe task:
- MPF-002 Contribution Core (only after Foundation 001 gate is accepted)
```
