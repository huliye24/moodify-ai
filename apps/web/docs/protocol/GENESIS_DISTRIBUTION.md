# Genesis Distribution

**Package:** MOOD-GENESIS-004  
**Name:** Distribution Engine  
**Purpose:** Deterministic Genesis allocation snapshot, export, Merkle tree and proof generation

This document describes the distribution pipeline that converts approved Genesis allocations into a reproducible distribution artifact set.

## Overview

The Distribution Engine is the bridge between off-chain allocation decisions (Package 003) and the on-chain airdrop (Package 005). It:

1. Reads approved allocation records from the database
2. Validates wallet addresses and allocation amounts
3. Generates a deterministic snapshot with canonical ordering
4. Builds a Merkle tree for future on-chain verification
5. Exports artifacts for human review and audit

**Critical Safety Boundaries:**

- ✅ Reads allocation data
- ✅ Generates snapshots and Merkle trees
- ✅ Creates audit reports
- ❌ **Does NOT transfer MOOD tokens**
- ❌ **Does NOT approve token transfers**
- ❌ **Does NOT sign transactions**
- ❌ **Does NOT deploy contracts**
- ❌ **Does NOT handle private keys**

## Inclusion Rules

Participants are included in the distribution snapshot only if ALL of the following are true:

| Field | Requirement |
|-------|-------------|
| `status` | Must be `"allocated"` |
| `walletAddress` | Must be valid EVM address (0x + 40 hex chars) |
| `allocationMood` | Must be > 0 |
| `allocationMood` | Must not exceed 18 decimal places |
| `allocationMood` | Must not be negative |
| `participantNumber` | Must be unique across snapshot |

**Excluded statuses:**

- `registered` — initial registration, not reviewed
- `reviewed` — reviewed but not yet allocated
- `eligible` — eligible but allocation not set
- `rejected` — explicitly rejected
- `distributed` — already distributed (Package 005)

## Token Arithmetic

### MOOD Token Configuration

- **Network:** BNB Smart Chain
- **Chain ID:** 56
- **Contract:** `0x1BB3115D43E397f7bb586F090831B02cA639e73E`
- **Symbol:** MOOD
- **Decimals:** 18
- **Total Supply:** 33,000,000 MOOD

### Atomic Unit Conversion

```
1 MOOD = 10^18 atomic units
```

**Conversion formula:**

```typescript
// MOOD to atomic
atomic = whole * 10^18 + decimal * 10^(18 - decimal_places)

// Example: 1000.5 MOOD
atomic = 1000 * 10^18 + 5 * 10^17
       = 1000500000000000000000
```

**Constraints:**

- No floating-point arithmetic for token amounts
- Maximum 18 decimal places
- Reject scientific notation
- Reject locale formatting (commas, underscores)
- Reject negative values
- Reject NaN/Infinity

## Snapshot Schema

### snapshot.json

```json
{
  "schema": "moodify-genesis-snapshot-v1",
  "snapshotId": "genesis-2026-08-27",
  "createdAt": "2026-08-27T12:00:00.000Z",
  "chainId": 56,
  "token": {
    "name": "Moodify",
    "symbol": "Mood",
    "address": "0x1BB3115D43E397f7bb586F090831B02cA639e73E",
    "decimals": 18
  },
  "source": {
    "gitCommit": "abc123...",
    "databaseFingerprint": "sha256-of-canonical-data",
    "allocationPolicyVersion": "genesis-v1"
  },
  "summary": {
    "participantCount": 100,
    "totalMood": "100000",
    "totalAtomic": "100000000000000000000000"
  },
  "participants": [
    {
      "participantNumber": 1,
      "walletAddress": "0x1BB3115D43E397f7bb586F090831B02cA639e73E",
      "walletAddressNormalized": "0x1bb3115d43e397f7bb586f090831b02ca639e73e",
      "allocationMood": "1000",
      "allocationAtomic": "1000000000000000000000"
    }
  ]
}
```

### Canonical Ordering

Participants are sorted before hashing:

1. **Primary:** `participantNumber` ascending
2. **Tie-breaker:** `walletAddressNormalized` (lowercase) lexicographically

This ensures deterministic output regardless of database retrieval order.

## Merkle Format

### Leaf Encoding

Following OpenZeppelin StandardMerkleTree convention:

```solidity
// Leaf types
["uint256", "address", "uint256"]

// Leaf values
[participantNumber, walletAddress, allocationAtomic]

// Leaf hash
leaf = keccak256(abi.encode(
    uint256 participantNumber,
    address walletAddress,
    uint256 allocationAtomic
))
```

### merkle.json

```json
{
  "schema": "moodify-genesis-merkle-v1",
  "leafTypes": ["uint256", "address", "uint256"],
  "root": "0xabc123...",
  "snapshotSha256": "sha256-of-snapshot.json",
  "claims": [
    {
      "participantNumber": 1,
      "account": "0x1bb3115d43e397f7bb586f090831b02ca639e73e",
      "amountMood": "1000",
      "amountAtomic": "1000000000000000000000",
      "proof": ["0xdef456...", "0xghi789..."]
    }
  ]
}
```

### Proof Verification

Each proof is locally verified against the root before export:

```typescript
// Verify: hash(leaf + proof[0]) + proof[1] ... = root
const computedRoot = computeRoot(leafHash, proof);
assert(computedRoot === merkleRoot);
```

## Reproducibility

### Deterministic Content

The following must be identical across runs with the same canonical data:

- Participant order
- Allocation amounts (atomic units)
- Merkle leaf hashes
- Merkle root
- Snapshot data hash

### Non-Deterministic Metadata

These fields may differ between runs:

- `createdAt` timestamp
- Output file paths
- Generator version (if different)

### Database Fingerprint

A SHA-256 hash of the canonical participant data allows operators to verify the exported snapshot matches the reviewed allocation set:

```
fingerprint = SHA256(JSON.stringify(sortedParticipants, canonicalKeys))
```

## CLI Usage

### Generate Snapshot

```bash
# Production run
npm run genesis:snapshot

# Dry run (validate without writing)
npm run genesis:snapshot -- --dry-run

# Custom output directory
npm run genesis:snapshot -- --output ./my-snapshots

# Custom snapshot ID
npm run genesis:snapshot -- --snapshot-id genesis-batch-001
```

### Output Artifacts

```
artifacts/genesis/<snapshot-id>/
├── snapshot.json          # Canonical snapshot data
├── distribution.csv       # Human-readable CSV export
├── merkle.json            # Merkle tree with proofs
├── distribution-report.md # Human-readable report
├── manifest.json          # File manifest with hashes
└── checksums.txt          # SHA-256 checksums of all files
```

## Validation Gates

Before artifact creation passes:

| Gate | Check |
|------|-------|
| Chain ID | Must be 56 (BNB Smart Chain) |
| Token Contract | Must match `0x1BB3115D43E397f7bb586F090831B02cA639e73E` |
| Decimals | Must be 18 |
| Wallet Valid | All addresses must be valid EVM format |
| Wallet Unique | No duplicate wallets allowed |
| Participant # Unique | No duplicate participant numbers |
| Allocation > 0 | All allocations must be positive |
| Pool Ceiling | Total must not exceed configured ceiling |
| Status Valid | All participants must have `allocated` status |
| No Rejected | No rejected participants included |
| No Duplicate Leaves | Merkle leaves must be unique |
| Merkle Root | Must be non-zero for non-empty dataset |

Any validation failure stops generation with clear diagnostics.

## Human Approval Boundary

**STOP before any on-chain operation.**

The Distribution Engine stops after generating artifacts. Before proceeding to Package 005 (Merkle Airdrop):

1. ✅ Review `distribution-report.md`
2. ✅ Verify participant count matches expectations
3. ✅ Verify total MOOD matches allocation policy
4. ✅ Sample 3+ wallet allocations against source
5. ✅ Verify Merkle root with local verifier
6. ✅ Inspect all checksums
7. ✅ Confirm no chain transaction occurred

## Relationship to Package 005

Package 004 produces the Merkle root and proofs consumed by Package 005:

```
Package 004 (Distribution Engine)
    ↓
[merkle.json] → Merkle root + proofs
    ↓
Package 005 (Merkle Airdrop Contract)
    ↓
On-chain claim verification
```

Package 005 will:

- Deploy Merkle distributor contract
- Fund contract with MOOD tokens
- Accept claims with Package 004 proofs
- Verify proofs against Package 004 root

## Error Codes

| Code | Description |
|------|-------------|
| `INVALID_AMOUNT` | Allocation amount is empty or invalid |
| `SCIENTIFIC_NOTATION` | Scientific notation not allowed |
| `LOCALE_FORMAT` | Locale formatting (commas) not allowed |
| `MULTIPLE_DECIMALS` | Multiple decimal points found |
| `PRECISION_EXCEEDED` | More than 18 decimal places |
| `INVALID_CHARS` | Amount contains invalid characters |
| `NEGATIVE_AMOUNT` | Negative allocations not allowed |
| `SNAPSHOT_EXISTS` | Snapshot ID already exists |
| `VALIDATION_FAILED` | One or more validation gates failed |

## Test Matrix

See `tests/genesis-distribution.test.mjs` for complete test coverage:

- D-001 to D-030: Core functionality tests
- Empty set behavior
- Duplicate detection
- Malformed data handling
- Deterministic ordering
- Merkle proof verification
- Snapshot overwrite protection

Run tests:

```bash
npm test
```

## Security Considerations

### Private Key Handling

**The Distribution Engine NEVER:**

- Requests private keys
- Stores private keys
- Signs transactions
- Generates key scripts

### Production Safety

- Dry-run mode validates without side effects
- Existing snapshots cannot be silently overwritten
- All validation failures are hard stops
- Clear audit trail in generated reports

### Chain Interaction

- No blockchain write APIs called
- No contract deployments
- No token transfers
- No approvals

## License

SPDX-License-Identifier: GPL-3.0-only

Copyright (c) 荣景文川 2024-2026
