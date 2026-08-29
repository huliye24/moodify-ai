# CODEX TASK — MPF-003 Reputation Core

## Task ID

`MOOD-PROTOCOL-REPUTATION-CORE-003`

## Objective

Implement a deterministic, versioned, auditable reputation layer that consumes MPF-002 finalized contribution/reputation-evidence records and produces:

1. contributor protocol profiles;
2. contributor contribution history;
3. epoch-level reputation snapshots;
4. dimension-level reputation totals;
5. provenance for every reputation component;
6. confidence/completeness status;
7. reproducible snapshot fingerprints;
8. superseding snapshots instead of silent mutation.

## Repository authority

Before coding, inspect:

- `AGENTS.md`
- `docs/canon/*`
- MPF-001 output
- MPF-002 implementation and schemas
- existing Genesis/010 contribution scoring
- current test framework
- any existing contributor/profile/identity systems

Do not create duplicate authorities.

If existing authoritative policies conflict, emit:

`HUMAN_DECISION_REQUIRED`

Do not silently choose.

## Canon rule

Default:

`CANON_CHANGE = NO`

If making Protocol Reputation a canonical authority requires Canon changes under repository rules, document:
- why
- affected authority files
- migration
- rollback

and do not silently modify authority.

## Required architecture

Prefer:

```text
protocol/
  reputation/
    README.md
    schema/
      contributor-profile.schema.json
      reputation-snapshot.schema.json
      reputation-attestation.schema.json
    config/
      reputation-policy.json
      epoch-policy.json
    src/
      aggregate.*
      normalize.*
      confidence.*
      snapshot.*
      identity.*
      fingerprint.*
    adapters/
      filesystem.*
    fixtures/
    tests/
```

Adapt to existing repo structure/language.

## Input authority

Only MPF-002 records in approved terminal state may contribute to reputation.

Recommended eligible statuses:

```text
scored
finalized
```

If MPF-002 implementation defines stronger authority, use the stronger rule.

Rejected, draft, pending, or unverified contributions MUST NOT increase reputation.

## Reputation dimensions

Maintain the same five dimensions from MPF-002:

- `contribution`
- `impact`
- `quality`
- `persistence`
- `early`

Do not rename or collapse them silently.

## Aggregation

The reputation layer must aggregate across verified contribution history.

If approved weights exist:
- reuse them;
- pin the exact policy version.

If weights do not exist:
- preserve dimension totals separately;
- aggregate reputation may remain `null`;
- do not invent weights.

## Contributor Profile

At minimum:

```json
{
  "profileVersion": "1.0.0",
  "protocolId": "mood:contributor:...",
  "primaryIdentity": {
    "type": "wallet",
    "id": "0x..."
  },
  "linkedPublicIdentities": [],
  "createdAt": "...",
  "status": "active",
  "firstVerifiedContributionAt": "...",
  "lastVerifiedContributionAt": "...",
  "verifiedContributionCount": 0,
  "currentSnapshotId": null
}
```

Private keys and seed phrases are forbidden.

## Protocol ID

Generate a stable protocol contributor ID from canonical public identity inputs.

Recommended:

```text
mood:contributor:<sha256(normalized identity namespace + id)>
```

Protocol ID must not expose secrets.

## Identity linking

MPF-003 may support linking public identities such as:

- wallet
- GitHub
- protocol node ID
- public contributor ID

But linking must require explicit verifiable evidence.

Do not merge identities only because names look similar.

If identity proof is insufficient:
- keep identities separate;
- mark link as `unverified` or `inconclusive`.

## Reputation Snapshot

A snapshot should include:

- snapshot version
- snapshot ID
- protocol ID
- epoch
- policy version
- contribution input IDs
- contribution input fingerprints
- dimension values
- aggregate if policy allows
- verified contribution count
- category diversity
- persistence evidence
- confidence/completeness
- generated timestamp
- snapshot fingerprint
- supersedes

## Epochs

Reputation must be calculated for a defined epoch or period.

Example:

```text
GENESIS
2026-09
2026-Q4
```

Do not depend on local timezone.

Epoch definition must be explicit and versioned.

## Confidence

Add a non-financial `confidence` or `completeness` status.

Example:

```text
low
medium
high
```

or a structured object.

Confidence reflects evidence completeness, not human worth.

Do not present confidence as moral ranking.

## Persistence

Persistence must be computed from longitudinal contribution history.

It must not be copied blindly from a single contribution score.

Prefer a deterministic rule such as:
- active verified periods;
- number of distinct contribution epochs;
- accepted contribution cadence;
- minimum history length.

If no approved formula exists, produce persistence evidence but do not invent an authoritative score.

## Early participation

Early score must derive from an objective protocol epoch boundary.

It must not increase forever.

It should be versioned and reproducible.

## Category diversity

Track contribution categories for observability.

Do not automatically reward category diversity unless policy explicitly says so.

## Attestations

Support optional public attestations.

Attestation may say:

> Reviewer X confirms that snapshot Y was generated from inputs Z under policy P.

Attestations are evidence.

They are not reputation by themselves unless policy explicitly defines them.

## Immutability

Snapshots are immutable.

New evidence or policy changes create a new snapshot that may `supersede` the previous one.

Never rewrite old snapshots in place.

## Policy changes

Changing a policy version must NOT silently rewrite historical reputation.

Historical snapshots remain pinned to historical policy.

Recalculation under a new policy creates a new snapshot version.

## No economics

MPF-003 must not create:

- token balance
- token entitlement
- claim allocation
- voting power
- staking power
- yield
- price multiplier
- treasury allocation
- liquidity privilege

## CLI / developer harness

Provide a repo-native method equivalent to:

```bash
reputation profile build <contributor>
reputation snapshot create <contributor> --epoch GENESIS
reputation snapshot inspect <snapshot-id>
reputation snapshot verify <snapshot-id>
```

No production dashboard required.

## Required fixtures

At least:

1. contributor with one finalized code contribution
2. contributor with multiple categories
3. contributor across multiple epochs
4. contributor with rejected contribution mixed into history
5. missing MPF-002 evidence
6. duplicate contribution input
7. policy mismatch
8. identity-link evidence valid
9. identity-link evidence insufficient
10. historical snapshot superseded by new snapshot
11. persistence with insufficient history
12. aggregate weights missing

## Required tests

Demonstrate:

- stable protocol ID generation
- contributor normalization
- only eligible contribution states count
- deterministic dimension aggregation
- rejected contributions excluded
- duplicate inputs rejected
- policy version pinned
- epoch boundary deterministic
- persistence requires longitudinal evidence
- identity linking does not guess
- snapshot immutability
- superseding snapshots work
- same inputs + same policy → same fingerprint
- no economic fields
- no chain writes

## Completion report

Return:

```text
TASK_ID
STATUS
CANON_CHANGE
BASE_COMMIT
FINAL_COMMIT
BRANCH
FILES_CHANGED
TESTS
POLICY_STATUS
EPOCH_POLICY
SAMPLE_PROTOCOL_ID
SAMPLE_SNAPSHOT_ID
SNAPSHOT_FINGERPRINT
IDENTITY_LINK_TEST
PERSISTENCE_TEST
NO_CHAIN_WRITE_PERFORMED
NO_TOKEN_DISTRIBUTION_PERFORMED
NO_PROTOCOL_RIGHTS_ASSIGNED
HUMAN_DECISION_REQUIRED
ROLLBACK
```
