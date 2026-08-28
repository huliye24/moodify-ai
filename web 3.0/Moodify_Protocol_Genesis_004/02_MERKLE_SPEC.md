# Merkle Specification
## Genesis Distribution v1

### Goal

Produce a root and proofs that can be consumed by the future Package 005 claim contract.

### Preferred implementation

Use OpenZeppelin's standard Merkle tooling if compatible with the current stack.

Preferred leaf types:

```text
uint256 participantNumber
address account
uint256 amount
```

Where `amount` is MOOD atomic units.

### Canonical leaf values

Example:

```text
participantNumber = 1
account = 0x1234...
amount = 1000000000000000000000
```

for 1000 MOOD.

### Why participant number is included

Including the participant number:
- binds the claim to the immutable Genesis registry identity;
- prevents two participants with accidentally duplicated allocation rows from producing semantically indistinguishable records;
- improves auditability.

The wallet remains the actual claimant identity.

### Address normalization

Before generating leaves:
- validate EVM address;
- convert to checksum/canonical form for display;
- use canonical address bytes for encoding.

### Amount handling

Use integer atomic units.

Never hash a human-readable decimal string directly if the future contract expects `uint256`.

### Proof export

For each participant, export:

```json
{
  "participantNumber": 1,
  "account": "0x...",
  "amountMood": "1000",
  "amountAtomic": "1000000000000000000000",
  "proof": ["0x...", "0x..."]
}
```

### Root metadata

`merkle.json` must include:

```json
{
  "schema": "moodify-genesis-merkle-v1",
  "leafTypes": ["uint256", "address", "uint256"],
  "root": "0x...",
  "snapshotSha256": "...",
  "claims": []
}
```

### Cross-check

Add a local verifier that:
- verifies every generated proof against root;
- verifies the claim data round-trips;
- fails if any proof does not verify.

### Compatibility checkpoint

Before Package 005 production deployment, the smart contract test suite must import or reproduce one Package 004 fixture and confirm identical root/proof behavior.

That final compatibility test belongs to Package 005, but Package 004 should provide a fixture.
