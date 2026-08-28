# Contract Security Specification
## MoodGenesisDistributor

### Security goals

1. Only approved Merkle leaves can claim.
2. Approved allocation can be claimed once.
3. Claim amount cannot be changed by claimant.
4. Claim wallet cannot be redirected.
5. Root cannot be silently changed.
6. Contract cannot mint MOOD.
7. Claimant never approves MOOD.
8. Admin privileges are minimized.
9. Funding and recovery behavior are transparent.
10. Contract behavior matches Package 004 proof generation exactly.

### Preferred v1 architecture

- immutable token address;
- immutable Merkle root;
- immutable optional deadline;
- claim state mapping;
- SafeERC20;
- no proxy;
- no upgradeability;
- no arbitrary pause unless a clear threat model justifies it;
- no arbitrary owner withdrawal during active campaign.

### Constructor validation

Validate:

- token != zero address;
- merkleRoot != zero root;
- if deadline used, deadline > block.timestamp;
- owner address valid if ownership exists.

### Claim validation order

Semantic order:

1. campaign active/deadline check;
2. participant not already claimed;
3. construct leaf from participantNumber + msg.sender + amount;
4. verify proof;
5. mark claimed;
6. transfer MOOD;
7. emit Claimed.

### Insufficient distributor balance

If distributor does not hold enough MOOD:
- claim reverts;
- claim state must not become permanently consumed.

State ordering and transaction atomicity naturally protect this, but add test coverage.

### Fee-on-transfer tokens

The current MOOD token is expected to be standard.

Do not add fee-on-transfer compatibility unless verified necessary.

### Root mutability

Default: no setter.

If a mutable root is requested later, treat as a new security review and governance change.

### Owner

Prefer no owner if no recovery/admin feature is needed.

If recovery is needed:
- use a minimal owner role;
- recommend Safe multisig;
- no active-campaign arbitrary withdrawal.

### Solidity compiler

Use the repository's current audited compiler/toolchain range.

Do not pin an arbitrary old compiler.

### Dependencies

Use current repository-approved OpenZeppelin version.

Codex must inspect installed/desired versions before implementation and use APIs consistent with that version.

### Static analysis

Run if available:
- Slither;
- Foundry tests;
- Foundry fuzz;
- invariant tests.

Document any unavailable tool.

### Fuzz targets

At minimum fuzz:
- valid amounts;
- invalid amounts;
- arbitrary wallets;
- arbitrary participant numbers;
- proof mutation;
- duplicate claim attempts.

### Invariants

Recommended:

- a participant can transition from unclaimed → claimed at most once;
- contract never transfers more than funded MOOD;
- successful claim amount equals approved leaf amount;
- failed claim does not mark claim as claimed;
- no claimant can consume another participant's allocation.
