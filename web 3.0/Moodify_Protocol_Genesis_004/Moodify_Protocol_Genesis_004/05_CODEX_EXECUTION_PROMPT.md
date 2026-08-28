# Codex Execution Prompt

Execute **Moodify Protocol Genesis 004 — Distribution Engine** inside the existing Moodify repository.

## Dependency check

Confirm Packages 001–003 or equivalent architecture exist.

Official MOOD facts:

- Network: BNB Smart Chain
- Chain ID: 56
- Token: Moodify / Mood
- Contract: `0x1BB3115D43E397f7bb586F090831B02cA639e73E`
- Decimals: 18
- Total supply: 33,000,000 MOOD

Package 004 does not transfer any token.

## Mission

Convert approved Genesis allocations into a deterministic, auditable distribution snapshot and Merkle artifact set.

Target command:

```bash
npm run genesis:snapshot
```

Adapt command naming to repository conventions if necessary.

## Mandatory audit first

Before editing:

1. Read repo instructions/canon.
2. Inspect git status and preserve unrelated work.
3. Locate Package 001 MOOD config authority.
4. Inspect Package 002 participant schema.
5. Inspect Package 003 status/allocation/audit model.
6. Identify approved allocation pool ceiling configuration.
7. Identify current CLI/script conventions.
8. Identify existing crypto/hash/OpenZeppelin dependencies.
9. Identify build/test commands.
10. Identify artifact directory policy in repo.

If production allocation ceiling is not approved/configured:
- implement validation/config support;
- allow fixture/dev testing;
- block production snapshot finalization;
- report the stop condition instead of inventing a number.

## Build

Implement deterministic distribution pipeline.

### Input
Include only valid participants according to approved status/allocation model.

### Exact arithmetic
Use integer atomic units. No float token arithmetic.

### Canonical ordering
Explicitly sort before hashing/tree generation.

### Outputs
Create:

```text
snapshot.json
distribution.csv
merkle.json
distribution-report.md
manifest.json
checksums.txt
```

under a snapshot-specific output folder.

### Merkle
Prefer OpenZeppelin StandardMerkleTree if compatible.

Preferred leaf types:

```text
["uint256", "address", "uint256"]
```

Values:

```text
participantNumber
walletAddress
allocationAtomic
```

Generate and locally verify every proof.

### Validation
Fail hard on:
- invalid wallet;
- duplicate wallet;
- duplicate participant number;
- invalid status;
- invalid amount;
- total over pool ceiling;
- wrong chain/token config;
- duplicate leaf;
- mismatch between summary and row totals.

### Reproducibility
Add tests proving:
- same canonical data => same dataset hash;
- same canonical data => same Merkle root;
- order-independent DB retrieval => same canonical output.

### Dry run
Support dry run that:
- performs validation;
- computes summary/root;
- does not mutate DB;
- does not execute blockchain writes.

### Documentation
Create/update:

`docs/protocol/GENESIS_DISTRIBUTION.md`

## Hard prohibitions

Do not:
- modify participant allocation policy;
- send MOOD;
- construct scripts that load private keys;
- call MetaMask;
- deploy claim contracts;
- publish a production root automatically;
- fund a distributor;
- add/remove liquidity;
- overwrite an existing approved snapshot silently.

## Tests

At minimum:

- empty set behavior;
- valid fixture;
- duplicate wallet;
- duplicate participant #;
- malformed wallet;
- negative amount;
- zero amount behavior;
- >18 decimal precision;
- pool ceiling exceeded;
- wrong status;
- exact total calculation;
- deterministic ordering;
- deterministic Merkle root;
- proof verification for all recipients;
- snapshot overwrite protection;
- exports exclude admin notes/signatures/nonces.

Run:
- lint;
- typecheck;
- tests;
- production build if script integration touches app build;
- snapshot fixture command.

## Completion output

Return:

1. audit findings;
2. input inclusion rule;
3. allocation ceiling source;
4. artifact paths;
5. sample snapshot summary;
6. Merkle root for test/dev fixture only unless human-approved production snapshot exists;
7. proof verification result;
8. checksums;
9. tests/build result;
10. git diff summary;
11. exact safety statement:

`No MOOD token transfer, token approval, wallet transaction, smart-contract deployment, liquidity operation, production Merkle publication, or private-key handling was performed by this task.`

## Stop conditions

Stop and ask for human confirmation if:
- approved production pool ceiling is missing and a production snapshot is requested;
- canon conflict exists;
- destructive migration is somehow required;
- a production Merkle root would be published externally;
- any signing/payment/private key is required.
