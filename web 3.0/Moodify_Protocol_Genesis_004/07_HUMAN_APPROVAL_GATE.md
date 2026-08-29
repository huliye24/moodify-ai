# Human Approval Gate
## Package 004 → Package 005

Package 004 ends before on-chain distribution.

A production Genesis snapshot must not become claimable merely because Codex generated it.

Before Package 005 consumes a production root, a human operator should approve:

- snapshot ID;
- participant count;
- total MOOD;
- Genesis pool ceiling;
- recipient wallet list;
- allocation policy version;
- Merkle root;
- artifact checksums;
- MOOD contract;
- chain ID.

Recommended approval record:

```text
Snapshot ID:
Participant count:
Total MOOD:
Merkle root:
Snapshot SHA256:
Approved by:
Approved at:
Notes:
```

This approval record can later be stored in protocol docs or a governance log.

## Human-only actions

Future human-only actions include:

- approving final root;
- deploying production distributor;
- transferring MOOD into distributor;
- signing Treasury transactions.

Codex should prepare, verify and report.
Human signs.
