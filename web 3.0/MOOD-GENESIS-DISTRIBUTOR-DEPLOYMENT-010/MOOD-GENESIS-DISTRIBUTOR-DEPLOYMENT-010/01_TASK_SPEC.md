# Task Specification

## Preconditions

Stop before deployment unless all are true:

- Package 009 is complete.
- `test.crestwavecoin.com` can read BSC mainnet.
- Official MOOD contract is uniquely defined as `0x1BB3115D43E397f7bb586F090831B02cA639e73E`.
- `MoodGenesisDistributor` source exists.
- Contract tests pass.
- Canonical Genesis allocation snapshot exists.
- Merkle root is reproducible.
- No secret material is committed.
- Human owner is available to sign deployment and funding.

## Primary outcome

Create one production distributor on BSC mainnet and record:

- distributor address;
- deployment tx hash;
- chain ID;
- deployer public address;
- MOOD token address;
- Merkle root;
- snapshot hash;
- participant count;
- total approved allocation;
- funding tx hash;
- distributor MOOD balance;
- BscScan verification status;
- exact Git commit used.

## Source-of-truth rule

Deployment must be based on:

1. repository source;
2. one frozen allocation snapshot;
3. one deterministic Merkle root;
4. human-approved deployment inputs.

Never copy a production Merkle root from chat without regenerating it from the snapshot.

## Required sequence

```text
009 complete
→ freeze contract
→ test
→ freeze snapshot
→ regenerate root twice
→ human reviews root + total allocation
→ prepare unsigned deployment
→ HUMAN SIGNATURE GATE #1
→ verify deployment
→ verify source/state
→ prepare funding
→ HUMAN SIGNATURE GATE #2
→ verify funding
→ configure staging distributor address
→ claims remain disabled
```

## Contract freeze

Record source path, compiler version, optimizer settings, dependencies, constructor args, artifact hash, bytecode hash if available, and Git SHA.

Any source change after approval invalidates approval.

## Snapshot freeze

Record:

- snapshot path;
- SHA-256;
- participant count;
- allocation total;
- token decimals/base-unit interpretation;
- generator command;
- Merkle root run #1;
- Merkle root run #2.

Roots must match. Otherwise stop with:

`P0 — NON-DETERMINISTIC DISTRIBUTION`

## Human approval card before deployment

Display exactly:

```text
CHAIN
BNB Smart Chain Mainnet (56)

MOOD TOKEN
0x1BB3115D43E397f7bb586F090831B02cA639e73E

DISTRIBUTOR SOURCE COMMIT
<sha>

MERKLE ROOT
<root>

PARTICIPANTS
<count>

TOTAL ALLOCATION
<amount MOOD>

DEPLOYER
<public address>

ESTIMATED GAS
<estimate>

DEPLOYMENT WILL MOVE MOOD?
NO
```

Do not broadcast until the human explicitly approves.

## Deployment rules

Codex may build, simulate, estimate gas, and prepare unsigned calldata/commands.

Codex must not receive a private key, seed phrase, or sign/broadcast using a secret it controls.

## Post-deploy verification

Verify:

- tx success;
- deployed code exists;
- runtime state matches approved inputs;
- MOOD reference is correct;
- Merkle root is correct;
- owner/admin state matches contract design;
- no unexpected value transfer occurred.

Any mismatch:

`P0 — DEPLOYMENT STATE MISMATCH`

Stop before funding.

## Funding

Compute:

```text
snapshot allocation total
current distributor MOOD balance
required funding delta
```

Do not assume the entire treasury should be sent.

Before funding, show:

```text
FROM
<public treasury address>

TO
<distributor address>

TOKEN
MOOD

TOKEN CONTRACT
0x1BB3115D43E397f7bb586F090831B02cA639e73E

AMOUNT
<exact amount>

CURRENT DISTRIBUTOR BALANCE
<amount>

EXPECTED BALANCE AFTER
<amount>
```

Require explicit human approval. Codex does not sign.

## Public staging

After verification, the real distributor address may be added to `test.crestwavecoin.com`.

Claims must remain disabled.

Package 010 is complete only if:

```text
Distributor deployed
+ deployment verified
+ canonical address recorded
+ snapshot/root recorded
+ approved funding confirmed
+ public claim still disabled
```
