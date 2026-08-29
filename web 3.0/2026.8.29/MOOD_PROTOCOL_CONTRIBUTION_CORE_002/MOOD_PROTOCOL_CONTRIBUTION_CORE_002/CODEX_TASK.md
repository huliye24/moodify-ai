# CODEX TASK — MPF-002 Contribution Core

## Task ID

`MOOD-PROTOCOL-CONTRIBUTION-CORE-002`

## Objective

Implement an auditable, deterministic and storage-agnostic contribution core for MOOD Protocol.

The system must be able to:

1. represent a contributor without requiring custody of their wallet;
2. create a contribution record;
3. attach structured evidence;
4. validate the record against a versioned schema;
5. move the record through a deterministic review state machine;
6. score verified contributions across defined dimensions;
7. produce a reputation-evidence artifact;
8. reproduce the result from the same inputs and policy version;
9. reject malformed, duplicate or policy-incompatible records;
10. do all of the above without any chain write or token movement.

## Repository authority

Before coding, inspect and obey:

- `AGENTS.md`
- `docs/canon/*`
- current repository status
- MPF-001 output
- any existing Web3 / Genesis / allocation / contribution policy
- current tests

If an existing authoritative contribution policy already exists, adapt to it.

If two authoritative sources conflict, DO NOT choose silently.

Emit:

`HUMAN_DECISION_REQUIRED`

with:
- conflicting files
- conflicting values
- proposed resolution
- effect of each option

## Canon rule

This task should default to:

`CANON_CHANGE = NO`

unless the repository's authority system requires contribution policy itself to become Canon.

If implementation would change product identity, chain authority, treasury authority, token authority, or existing Genesis allocation policy, stop and emit `HUMAN_DECISION_REQUIRED`.

## Required architecture

Prefer:

```text
protocol/
  contribution/
    README.md
    schema/
      contribution.schema.json
      evidence.schema.json
      reputation-evidence.schema.json
    config/
      contribution-policy.json
    src/
      ids.*
      normalize.*
      validate.*
      state-machine.*
      score.*
      fingerprint.*
    adapters/
      filesystem.*
    fixtures/
      valid/
      invalid/
    tests/
```

Adapt paths to the repository's language/tooling if needed. Do not create a second framework when an existing canonical subsystem already exists.

## Required data model

A contribution must include at minimum:

- `schemaVersion`
- `contributionId`
- `contributor`
- `category`
- `title`
- `description`
- `submittedAt`
- `evidence[]`
- `status`
- `policyVersion`
- `contentFingerprint`
- `review`
- `scores`
- `reputationEvidence`

Contributor identity must support a public wallet address but must not require a private key.

Example contributor:

```json
{
  "type": "wallet",
  "id": "0x...",
  "displayName": null
}
```

Other contributor identity types may exist only if justified by existing repository requirements.

## Contribution categories

The core must support a controlled category registry.

At minimum the policy model must be able to represent:

- `code`
- `documentation`
- `data`
- `compute`
- `research`
- `design`
- `community`
- `infrastructure`
- `security`
- `other`

Do not assume every category is currently eligible for scoring. Eligibility belongs in policy.

## Evidence types

At minimum the schema must be able to represent:

- git commit / pull request
- issue / review
- file hash
- dataset hash
- compute receipt
- benchmark / test report
- document URL
- transaction hash as READ-ONLY evidence
- signed public message
- manual review note

A transaction hash may be recorded as evidence, but MPF-002 must not send a transaction.

## State machine

Implement a single authoritative contribution state machine:

```text
draft
  ↓
submitted
  ↓
under_review
  ├──> rejected
  ├──> needs_more_evidence
  └──> verified
             ↓
          scored
             ↓
          finalized
```

Rules:

- finalized records are immutable except through an explicit superseding record;
- rejected records must retain rejection reason;
- `needs_more_evidence` must retain missing-evidence reasons;
- scoring before `verified` is forbidden;
- finalization before scoring is forbidden if the active policy requires scoring;
- no transition may silently skip mandatory states.

If existing repository authority defines a different state machine, reuse it instead of creating a duplicate.

## Deterministic IDs

Generate contribution IDs deterministically or collision-resistently.

Recommended canonical input:

```text
schemaVersion
contributor.type
normalized contributor.id
category
contentFingerprint
submittedAt
```

If UUID is used, store a separate deterministic `contentFingerprint`.

## Content fingerprint

Create a canonical normalized representation and hash it.

Use a standard cryptographic hash supported by the repo, preferably SHA-256.

The same evidence payload in different key order must produce the same normalized fingerprint.

Do not include mutable review fields in the immutable content fingerprint.

## Duplicate detection

At minimum reject exact duplicate fingerprints for the same contributor and category unless an explicit supersede relationship exists.

Provide hooks for stronger semantic duplicate detection later, but do not invent AI-based duplicate scoring in 002.

## Scoring

Implement dimension-level scoring only after verification.

Required dimensions:

- `contribution`
- `impact`
- `quality`
- `persistence`
- `early`

These match the known Genesis/010 policy vocabulary and should remain separable.

Each dimension must expose:
- numeric value
- evidence references
- scoring rule/version
- reviewer or deterministic rule source

Do not hardcode an economic conversion from score → MOOD.

If existing policy has approved weights, use them.

If no approved weights exist:
- keep dimension scores;
- mark aggregate reputation score as `null`;
- set policy lock state to `draft`;
- emit `HUMAN_DECISION_REQUIRED` for weight approval.

## Reputation evidence

Produce a non-economic artifact such as:

```json
{
  "contributionId": "...",
  "policyVersion": "...",
  "dimensions": {...},
  "aggregate": null,
  "status": "scored",
  "generatedAt": "...",
  "inputFingerprint": "...",
  "artifactFingerprint": "..."
}
```

This artifact may later be consumed by a Reputation package.

It MUST NOT contain:
- token amount
- token price
- vesting amount
- claim amount
- treasury transfer instruction

## Storage

Core logic must be independent from Cloudflare/D1 availability.

Provide a filesystem/JSON fixture adapter first, or reuse an existing repository abstraction.

If a D1 adapter already exists and can be integrated without making D1 a hard dependency, it may be added.

Cloud/network unavailability must not block unit tests.

## CLI or test harness

Provide a minimal developer-facing way to exercise the core, for example:

```bash
contribution create ...
contribution validate ...
contribution verify ...
contribution score ...
contribution inspect ...
```

or equivalent repository-native scripts.

Do not build a production dashboard in this package.

## Required fixtures

Create at least:

1. valid code contribution
2. valid documentation contribution
3. valid compute contribution
4. missing evidence
5. malformed contributor
6. duplicate contribution
7. invalid state transition
8. attempt to score unverified record
9. altered finalized record
10. policy-version mismatch

## Tests

Tests must demonstrate:

- deterministic normalization
- deterministic fingerprints
- schema validation
- state transition guards
- duplicate detection
- scoring guard
- policy-version pinning
- finalization immutability
- no economic fields
- no chain write path
- repeatable reputation-evidence output

## Chain boundary

MPF-002 may READ:
- wallet addresses
- public chain IDs
- public transaction hashes
- public explorer evidence

MPF-002 may NOT:
- request private keys
- request seed phrases
- sign transactions
- transfer MOOD
- mint MOOD
- approve MOOD
- claim MOOD
- add liquidity
- modify treasury
- deploy contracts

## Completion report

Return a markdown execution report containing:

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
SAMPLE_CONTRIBUTION_IDS
DUPLICATE_TEST
IMMUTABILITY_TEST
CHAIN_WRITE = NONE
TOKEN_DISTRIBUTION = NONE
HUMAN_DECISION_REQUIRED
ROLLBACK
```

Do not report PASS when mandatory tests are failing.
