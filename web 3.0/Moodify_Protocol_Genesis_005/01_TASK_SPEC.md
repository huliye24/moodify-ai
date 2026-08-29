# Task Specification
## Merkle Airdrop

### 1. Mission

Build the first production-capable Moodify Genesis claim system.

The system must use the approved Merkle snapshot produced by Package 004 and expose a safe claim flow for eligible Genesis Participants.

### 2. Contract

Preferred contract name:

`MoodGenesisDistributor.sol`

Use the repository's established Solidity project layout. If none exists, prefer a minimal Foundry workspace under an existing contracts/protocol location rather than a separate unrelated repository.

### 3. Contract responsibilities

The distributor must:

- hold MOOD tokens for the Genesis campaign;
- store the approved Merkle root;
- allow each eligible claim exactly once;
- verify:
  - participant number;
  - claimant account;
  - allocation amount;
  - Merkle proof;
- transfer the exact approved MOOD amount;
- emit auditable events;
- reject malformed or duplicate claims;
- expose useful read methods;
- support an optional campaign deadline if approved;
- support post-expiry recovery only under explicit and documented governance rules.

### 4. Token

Official MOOD:

- Network: BNB Smart Chain
- Chain ID: `56`
- Token: Moodify / Mood
- Contract: `0x1BB3115D43E397f7bb586F090831B02cA639e73E`
- Decimals: `18`

The distributor must not assume mint authority.

It distributes only MOOD actually transferred into the distributor.

### 5. Merkle compatibility

Package 004 preferred leaf:

```text
["uint256", "address", "uint256"]
```

Values:

```text
participantNumber
account
amountAtomic
```

Package 005 must import or reproduce at least one Package 004 fixture and prove contract verification matches the off-chain generator.

If Package 004 ultimately used a different approved leaf encoding:
- do not silently change it;
- adapt the contract;
- document exact compatibility;
- add a fixture regression test.

### 6. Recommended claim API

Semantic Solidity shape:

```solidity
function claim(
    uint256 participantNumber,
    uint256 amount,
    bytes32[] calldata proof
) external;
```

The claimant account should normally be `msg.sender`.

This prevents a third party from redirecting a claim to another account unless meta-claiming is intentionally added later.

Do not add delegated claims in v1 unless already required.

### 7. Claim state

Recommended:

```solidity
mapping(uint256 => bool) public claimedParticipant;
```

and/or wallet-based protection where needed.

Because Package 004 leaf includes participant number + account + amount, claim uniqueness should be designed explicitly.

Required invariant:

> The same approved allocation cannot be claimed twice.

If participant number and wallet uniqueness are both guaranteed by Package 004, choose the simplest safe representation and document it.

### 8. Root lifecycle

Preferred v1:

- immutable Merkle root at deployment.

This is safer and simpler than an admin-updatable root.

If operational requirements demand root updates:
- stop for human approval before implementing mutable root;
- require explicit governance controls;
- provide a reasoned threat model.

Default to immutable root.

### 9. Deadline

Deadline is optional.

If used:

- immutable `claimDeadline`;
- must be in the future;
- claims after deadline revert;
- recovery can only occur after deadline;
- deadline must be shown on `/airdrop`.

If no approved deadline exists:
- do not invent one;
- support no-deadline v1 or stop before production depending on protocol decision.

### 10. Recovery

If a deadline is used, unclaimed tokens may need recovery.

Safer shape:

```solidity
function recoverUnclaimed(address recipient) external onlyOwner afterDeadline
```

But this introduces privileged control.

If implemented:
- use OpenZeppelin Ownable with clearly assigned owner;
- recommend a Safe/multisig as owner;
- emit event;
- disallow recovery before deadline;
- recover only the distributor's remaining MOOD;
- document owner risk.

If no deadline/recovery policy is approved, omit recovery in v1.

### 11. Reentrancy and token handling

Use:

- OpenZeppelin `SafeERC20`;
- checks before effects before interactions where applicable;
- `nonReentrant` only if justified rather than added mechanically.

MOOD is expected to be a standard BEP-20/ERC-20 token, but contract logic should still use safe transfer helpers.

### 12. Events

At minimum:

```solidity
event Claimed(
    uint256 indexed participantNumber,
    address indexed account,
    uint256 amount
);
```

If recovery exists:

```solidity
event UnclaimedRecovered(
    address indexed recipient,
    uint256 amount
);
```

### 13. Read methods

Expose or inherit:

- `merkleRoot()`
- `token()`
- claim status lookup
- optional deadline
- contract token balance through standard token balance query

Avoid unnecessary state duplication.

### 14. Funding model

The distributor must be funded by transferring the approved total MOOD allocation after deployment.

Codex may prepare:
- exact amount;
- transfer calldata;
- Safe transaction specification;
- MetaMask/manual runbook.

Codex must **not** sign or broadcast the production funding transaction.

### 15. Frontend `/airdrop`

Create:

`/airdrop`

The page must support:

#### Disconnected
- explain Genesis claim;
- connect wallet.

#### Wrong network
- require BNB Smart Chain;
- safe network-switch prompt.

#### Not eligible
- clear non-eligible state;
- no misleading failure.

#### Eligible
Show:
- Genesis Participant #
- wallet
- approved allocation
- claim status
- Merkle root/snapshot reference where appropriate
- claim button

#### Claiming
- wallet transaction pending;
- transaction hash if available.

#### Claimed
- amount claimed;
- BscScan transaction link;
- status persisted/read from chain.

### 16. Proof delivery

Preferred options:

A. Static proof artifact derived from approved Package 004 snapshot.
B. Server endpoint that returns only the proof/amount for the requesting wallet.
C. CDN/public JSON if privacy model permits.

The canonical eligibility must remain derivable from the approved snapshot.

Do not require a trusted server to decide eligibility at claim time if the Merkle proof already encodes eligibility.

### 17. Public API

If a proof endpoint is used:

```text
GET /api/airdrop/eligibility?address=0x...
```

Return only:

- eligible;
- participantNumber;
- amountMood;
- amountAtomic;
- proof;
- claim status if chain query is available.

Do not return:
- internal admin notes;
- raw signatures;
- nonces;
- private user profile fields.

### 18. Claim transaction safety UX

Before wallet transaction request:

Show:

- Network: BNB Smart Chain
- Contract: MoodGenesisDistributor
- Claim amount
- estimated gas if available
- statement:
  `This transaction claims your approved MOOD allocation. It does not approve token spending.`

Never request MOOD approval from the claimant.

The distributor sends MOOD to claimant; claimant should not need to approve any token.

### 19. Deployment preparation

Provide scripts for:

1. local deployment;
2. BSC testnet if project policy allows;
3. BSC mainnet production deployment;
4. BscScan verification;
5. distributor funding;
6. post-deployment validation.

Production scripts must require explicit environment values and fail closed.

Never ship a real private key.

### 20. Deployment record

Create a schema/document for:

```text
chainId
tokenAddress
distributorAddress
merkleRoot
snapshotId
snapshotSha256
participantCount
totalMood
deployedTx
fundedTx
deployedAt
claimDeadline
owner
gitCommit
```

Do not fill production values until real human-signed deployment occurs.

### 21. Documentation

Create:

`docs/protocol/GENESIS_AIRDROP.md`

and:

`docs/protocol/GENESIS_AIRDROP_RUNBOOK.md`

Document:
- contract architecture;
- Merkle compatibility;
- claim flow;
- funding;
- ownership;
- deadline/recovery;
- deployment;
- verification;
- emergency response;
- human checkpoints.

### 22. Explicit non-goals

Do not add:
- staking;
- vesting;
- referral rewards;
- buy-to-claim;
- volume incentives;
- trading rewards;
- tax token logic;
- blacklist;
- upgrade proxy;
- arbitrary admin claim overrides;
- hidden minting;
- auto-market-making.
