# Task Specification
## Distribution Engine

### 1. Mission

Build the deterministic data pipeline that converts approved Genesis allocations into distribution-ready artifacts.

Package 003 owns review and provisional allocation.

Package 004 must not make policy decisions. It only turns approved data into a verified snapshot.

### 2. Input eligibility

Default inclusion rule:

- participant status is `allocated`;
- wallet address is valid;
- allocation > 0;
- participant is not rejected;
- participant record is not duplicated;
- allocation is within approved Genesis pool ceiling.

Do not silently include:
- `registered`;
- `reviewed`;
- `eligible` without allocation;
- `rejected`;
- zero allocation;
- malformed wallet.

If existing canon uses a slightly different approved-state model, adapt after audit and document it.

### 3. Deterministic command

Create a repository-consistent CLI command, for example:

```bash
npm run genesis:snapshot
```

Recommended flags:

```bash
npm run genesis:snapshot -- --dry-run
npm run genesis:snapshot -- --output artifacts/genesis
npm run genesis:snapshot -- --snapshot-id genesis-2026-08-xx
```

Do not require production credentials for dry-run/local validation where avoidable.

### 4. Canonical ordering

Before hashing or Merkle generation, sort participant rows deterministically.

Recommended order:

1. participant number ascending;
2. wallet address normalized as tie-breaker.

Never rely on database implicit row order.

### 5. Token arithmetic

MOOD:
- decimals: 18
- contract: `0x1BB3115D43E397f7bb586F090831B02cA639e73E`

Allocation conversion must use exact integer arithmetic.

For each participant:

```text
allocation_mood
allocation_atomic
```

Where:

```text
1 MOOD = 10^18 atomic units
```

No JavaScript floating point for token amounts.

Reject:
- fractional precision > 18 decimals;
- negative values;
- scientific notation unless normalized safely;
- NaN/Infinity;
- locale-formatted numbers.

### 6. Snapshot JSON

Create a canonical `snapshot.json`.

Suggested structure:

```json
{
  "schema": "moodify-genesis-snapshot-v1",
  "snapshotId": "...",
  "createdAt": "...",
  "chainId": 56,
  "token": {
    "name": "Moodify",
    "symbol": "Mood",
    "address": "0x1BB3115D43E397f7bb586F090831B02cA639e73E",
    "decimals": 18
  },
  "source": {
    "gitCommit": "...",
    "databaseFingerprint": "...",
    "allocationPolicyVersion": "..."
  },
  "summary": {
    "participantCount": 0,
    "totalMood": "0",
    "totalAtomic": "0"
  },
  "participants": []
}
```

Participant record:

```json
{
  "participantNumber": 1,
  "walletAddress": "0x...",
  "walletAddressNormalized": "0x...",
  "allocationMood": "1000",
  "allocationAtomic": "1000000000000000000000"
}
```

Do not include:
- raw signatures;
- nonces;
- internal admin notes;
- private user data;
- admin auth identifiers unless necessary for provenance.

### 7. Distribution CSV

Required columns:

```text
participant_number
wallet_address
allocation_mood
allocation_atomic
```

Recommended additional non-sensitive fields:

```text
status
snapshot_id
```

Sort identically to snapshot JSON.

### 8. Merkle generation

Generate a Merkle tree suitable for future Solidity verification.

The leaf encoding must be explicit and versioned.

Recommended future-compatible leaf:

```solidity
keccak256(
    bytes.concat(
        keccak256(
            abi.encode(
                uint256 participantNumber,
                address account,
                uint256 amount
            )
        )
    )
)
```

If using OpenZeppelin `StandardMerkleTree`, prefer its canonical format and document exact leaf types:

```text
["uint256", "address", "uint256"]
```

Values:

```text
participantNumber
walletAddress
allocationAtomic
```

Do not invent a non-standard encoding without strong reason.

`merkle.json` must contain:

- schema/version;
- root;
- leaf encoding;
- tree format;
- participant proofs;
- amount in atomic units;
- source snapshot hash.

### 9. Reproducibility

The pipeline must clearly separate:

#### Deterministic content
- participant order;
- allocations;
- leaves;
- proofs;
- root;
- canonical JSON representation.

#### Non-deterministic metadata
- generatedAt timestamp;
- output path;
- environment notes.

If timestamps would make whole-file hashes differ between identical runs, either:
- exclude non-deterministic metadata from canonical hash inputs; or
- support a reproducible mode with provided snapshot timestamp/id.

Document exact behavior.

### 10. Database fingerprint

Create a deterministic fingerprint of the included allocation dataset.

Example:

```text
SHA256(canonical participant allocation rows)
```

This is not a database backup.

It allows an operator to confirm the exported snapshot matches the reviewed allocation set.

### 11. Validation gates

Before artifact creation passes:

- chain ID = 56;
- MOOD contract matches Package 001 authority;
- decimals = 18;
- all wallets valid;
- wallets unique;
- participant numbers unique;
- allocations > 0;
- total <= configured Genesis pool ceiling;
- participant statuses valid;
- total participant count > 0 unless explicit empty dry-run mode;
- no rejected participant included;
- no duplicate Merkle leaf;
- Merkle root non-zero for non-empty dataset.

Any failure must stop generation with clear diagnostics.

### 12. Distribution report

Create:

`distribution-report.md`

Required summary:

- snapshot ID;
- source git commit;
- participant count;
- total MOOD;
- min allocation;
- max allocation;
- median allocation;
- mean allocation;
- allocation distribution bands if useful;
- Merkle root;
- MOOD contract;
- BNB Smart Chain chain ID;
- validation results;
- excluded-row summary;
- explicit statement that no token transfer occurred.

Do not include personal notes.

### 13. Checksums

Generate SHA-256 checksums for final artifacts.

Example:

```text
<sha256>  snapshot.json
<sha256>  distribution.csv
<sha256>  merkle.json
<sha256>  distribution-report.md
<sha256>  manifest.json
```

### 14. Manifest

Create `manifest.json` describing:

- package schema;
- snapshot ID;
- source commit;
- files;
- file hashes;
- Merkle root;
- total allocation;
- participant count;
- generator version.

### 15. Dry-run

`--dry-run` must:

- read/validate allocation state;
- print summary;
- compute prospective Merkle root;
- avoid mutating DB;
- avoid publishing artifacts unless explicitly requested;
- never call blockchain write APIs.

### 16. Snapshot immutability

Once a snapshot ID is generated and approved, regenerating the same ID with different data must fail unless an explicit non-production override is used.

Do not silently overwrite approved snapshots.

Package 004 can implement local immutability/manifest checks; Package 005 will consume the approved root.

### 17. Documentation

Create:

`docs/protocol/GENESIS_DISTRIBUTION.md`

Document:
- inclusion rules;
- exact allocation arithmetic;
- snapshot schema;
- leaf encoding;
- Merkle format;
- reproducibility model;
- checksums;
- approval boundary;
- relationship to Package 005.

### 18. Explicit non-goals

Do not:
- send MOOD;
- generate private-key scripts;
- auto-sign Safe/MetaMask transactions;
- deploy distributor contract;
- fund distributor contract;
- create liquidity;
- change participant allocations;
- determine contribution policy;
- fabricate recipients.
