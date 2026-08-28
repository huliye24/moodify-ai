# Artifact Schema
## Genesis Distribution Engine

### Folder

Recommended:

```text
artifacts/genesis/<snapshot-id>/
```

### `snapshot.json`

Canonical allocation snapshot.

Required:
- schema
- snapshotId
- chainId
- token
- source
- summary
- participants

### `distribution.csv`

Human-auditable flat distribution export.

Required columns:

```text
participant_number
wallet_address
allocation_mood
allocation_atomic
```

### `merkle.json`

Machine-consumable claim data.

Required:
- schema
- leafTypes
- root
- snapshotSha256
- claims/proofs

### `distribution-report.md`

Human review artifact.

### `manifest.json`

Suggested:

```json
{
  "schema": "moodify-genesis-manifest-v1",
  "snapshotId": "...",
  "generatorVersion": "...",
  "sourceGitCommit": "...",
  "participantCount": 0,
  "totalMood": "0",
  "merkleRoot": "0x...",
  "files": [
    {
      "name": "snapshot.json",
      "sha256": "..."
    }
  ]
}
```

### `checksums.txt`

SHA-256 file list.

### Fixture

Create a small non-production fixture for tests, e.g.:

```text
tests/fixtures/genesis-distribution-v1.json
```

Never include real private participant data in public test fixtures unless the wallet addresses are explicitly designated public/test addresses.
