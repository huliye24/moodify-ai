# Package Manifest

Package: `MOOD_PROTOCOL_REPUTATION_CORE_003`

Purpose:

> Convert verified contribution history into auditable Protocol Reputation and Protocol Identity.

## Files

- START_HERE.md
- CODEX_TASK.md
- ARCHITECTURE.md
- REPUTATION_MODEL.md
- IDENTITY_MODEL.md
- EPOCH_POLICY.md
- ATTESTATION_POLICY.md
- DECAY_AND_PERSISTENCE.md
- ANTI_GAMING.md
- SECURITY_BOUNDARY.md
- TEST_PLAN.md
- ACCEPTANCE_GATE.md
- IMPLEMENTATION_CHECKLIST.md
- ROLLBACK.md
- EVIDENCE_TEMPLATE.md
- schema/contributor-profile.schema.json
- schema/reputation-snapshot.schema.json
- schema/reputation-attestation.schema.json
- config/reputation-policy.draft.json
- config/epoch-policy.draft.json
- fixtures/contributor-profile.example.json
- fixtures/reputation-snapshot.example.json
- SHA256SUMS.txt

## Explicit exclusions

MPF-003 does NOT implement:

- MOOD reward conversion
- Genesis claim
- staking
- governance voting power
- treasury allocation
- liquidity
- node economics
- on-chain identity
- NFT / SBT
- public reputation leaderboard

Those are future concerns.

## Success condition

A contributor with finalized MPF-002 records can be represented as:

```text
Public Identity
      ↓
Protocol ID
      ↓
Verified Contribution History
      ↓
Versioned Reputation Snapshot
      ↓
Auditable Protocol Identity
```
