# Codex Execution Prompt

Execute **Moodify Protocol Genesis 005 — Merkle Airdrop** inside the existing Moodify repository.

## Dependencies

Confirm Packages 001–004 or equivalent implementation exist.

Do not proceed to production configuration unless Package 004 has an explicitly human-approved production snapshot/root.

Official MOOD:

- Network: BNB Smart Chain
- Chain ID: 56
- Contract: `0x1BB3115D43E397f7bb586F090831B02cA639e73E`
- Decimals: 18

## Mission

Build:

1. `MoodGenesisDistributor.sol`
2. comprehensive Foundry/security tests
3. Package 004 compatibility fixture test
4. deployment + verification scripts
5. funding preparation script/calldata
6. `/airdrop` frontend
7. proof/eligibility data access
8. docs and human-signed runbook

## Mandatory audit before editing

1. Read repo instructions/canon.
2. Inspect git status and preserve unrelated changes.
3. Inspect Package 001 token config.
4. Inspect Package 004 leaf encoding/artifacts.
5. Inspect existing Solidity/Foundry structure.
6. Inspect installed OpenZeppelin version.
7. Inspect web3/wallet frontend libraries.
8. Inspect server/API patterns.
9. Inspect deployment conventions.
10. Identify production environment handling.
11. Confirm no private key is needed for coding/testing.

## Contract default

Prefer a minimal immutable-root distributor.

Semantic claim:

```solidity
claim(
  uint256 participantNumber,
  uint256 amount,
  bytes32[] calldata proof
)
```

Claimant is `msg.sender`.

Use Package 004 exact leaf encoding.

Use SafeERC20.

Do not add upgradeability.

Do not add mutable root unless a human-approved requirement explicitly exists.

Do not add arbitrary admin withdrawal during active campaign.

If deadline/recovery policy is not approved, implement the simplest safe no-deadline/no-recovery contract or stop and explain the choice before production.

## Contract tests

At minimum:

- constructor validation;
- valid claim;
- invalid proof;
- wrong wallet;
- wrong amount;
- wrong participant;
- double claim;
- zero amount if invalid per snapshot;
- insufficient distributor balance;
- multiple valid participants;
- proof mutation;
- exact Package 004 fixture compatibility;
- fuzz arbitrary invalid account/amount combinations;
- recovery/deadline tests if feature exists.

## Frontend

Create `/airdrop`.

States:
- disconnected;
- wrong network;
- checking;
- not eligible;
- eligible;
- wallet confirmation;
- pending;
- claimed;
- error.

Claim success must be confirmed from chain receipt/state.

Never ask claimant to approve MOOD.

## Eligibility/proof source

Use approved Package 004 artifact.

If an API is used, it may return only public claim fields.

Do not expose notes/signatures/nonces.

## Deployment

Create scripts for:
- local/test deployment;
- production deployment preparation;
- BscScan verification;
- distributor funding preparation;
- deployment record generation.

Production mainnet action must stop before signing/broadcasting.

Never read a production private key from a committed file.

If Foundry scripts conventionally support private keys via env, document the variable but do not populate it, and do not execute a mainnet broadcast.

## Security verification

Run:
- `forge test`
- fuzz/invariant tests
- gas report if available
- Slither if installed/available
- frontend lint/typecheck/tests/build
- local claim integration fixture

Fix task-related issues.

## Completion output

Return:

1. audit findings;
2. contract architecture;
3. exact leaf encoding;
4. privilege model;
5. deadline/recovery decision;
6. contract test results;
7. static analysis;
8. frontend states;
9. deployment scripts generated;
10. production steps that remain human-only;
11. files changed;
12. git diff summary;
13. exact safety statement:

`No production MOOD transfer, production token approval, production contract deployment, production wallet signature, liquidity operation, or private-key handling was performed by this task.`

## Stop conditions

Stop for human confirmation if:

- Package 004 production root is not approved but mainnet config is requested;
- a mutable Merkle root is requested;
- admin withdrawal during active campaign is requested;
- a deadline/recovery policy decision is required;
- a production wallet/private key is requested;
- mainnet broadcast or funding is about to occur;
- canon conflict exists.
