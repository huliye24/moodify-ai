# MPF-002 — MOOD Protocol Contribution Core

**Package:** `MOOD_PROTOCOL_CONTRIBUTION_CORE_002`
**Status:** ✅ Implemented
**Tests:** 27/27 passing

---

## Overview

The Contribution Core provides an auditable, deterministic, and storage-agnostic layer for representing contributor records in the MOOD Protocol. It is the protocol's evidence layer for answering:

> Who contributed what, when, with which evidence, under which policy version, and what deterministic reputation evidence did that contribution produce?

This module is **NOT** an airdrop system, token-distribution system, or claim frontend. It ends at **Reputation Evidence**.

---

## Architecture

```
protocol/contribution/
├── schema/
│   ├── contribution.schema.json      # Contribution record schema
│   ├── evidence.schema.json          # Evidence object schema
│   └── reputation-evidence.schema.json
├── config/
│   └── contribution-policy.draft.json
├── src/
│   ├── ids.js            # Deterministic ID generation
│   ├── normalize.js      # Canonical JSON normalization
│   ├── fingerprint.js    # SHA-256 fingerprinting
│   ├── validate.js      # Schema + economic-field validation
│   ├── state-machine.js  # Authoritative state transitions
│   ├── duplicate-guard.js # Duplicate and cross-contributor detection
│   ├── score.js         # Dimension scoring engine
│   ├── reputation-evidence.js # Reputation artifact builder
│   ├── policy.js        # Policy loading and category rules
│   └── service.js       # Single authoritative service
├── adapters/
│   └── filesystem.js    # JSON-file storage adapter
├── fixtures/            # 11 test fixtures
├── tests/
│   └── suite.test.js    # 27 tests (T1–T18)
└── cli/
    └── index.js        # Developer CLI
```

---

## Key Design Decisions

### Deterministic IDs

Contribution IDs are derived from canonical inputs (schemaVersion, contributor.type, normalized contributor.id, category, contentFingerprint, submittedAt) using SHA-256. The same contribution always produces the same ID.

### Content Fingerprint

SHA-256 fingerprint of the canonically normalized contribution content, excluding mutable fields (review, scores, status, reputationEvidence). Fingerprint is stable across state transitions.

### State Machine

Single authoritative machine with enforced legal transitions:

```
draft → submitted → under_review → verified → scored → finalized
                      ↓              ↓
                   rejected    needs_more_evidence
```

### Economic Isolation

The core produces **NO** economic outputs:
- No token amounts
- No payout fields
- No claim fields
- No vesting fields
- No treasury instructions

### Chain Boundary

- ✅ READ public wallet addresses, transaction hashes, file hashes
- ❌ NO private keys, seed phrases, signing, transactions, token transfers

### Policy

Aggregate scoring is disabled until approved weights are available. Aggregate is `null` under current draft policy. `HUMAN_DECISION_REQUIRED` for weight approval.

---

## Usage

### Installation

```bash
cd protocol/contribution
npm install
```

### Run Tests

```bash
npm test
# → 27/27 tests pass
```

### CLI

```bash
# Show system info
node cli/index.js info

# Validate a contribution record
node cli/index.js validate fixtures/valid-code-contribution.json

# Create a contribution
node cli/index.js create fixtures/valid-code-contribution.json --submit

# Inspect stored contribution
node cli/index.js inspect <contribution-id>
```

### Programmatic

```javascript
import { ContributionService, ContributionStatus } from './src/service.js';
import { FilesystemRepository } from './src/adapters/filesystem.js';
import { DuplicateGuard } from './src/duplicate-guard.js';

const repo = new FilesystemRepository();
const guard = new DuplicateGuard();
const svc = new ContributionService({ repository: repo, duplicateGuard: guard });

// Create
const { contribution, errors } = svc.create(rawData, { submit: true });

// Review flow
svc.beginReview(contribution.contributionId, 'reviewer-address');
svc.verify(contribution.contributionId, 'reviewer-address', 'Looks good');

// Score
svc.score(contribution.contributionId, {
  contribution: { value: 85, ruleId: 'manual.v1', evidenceIds: ['e1'], source: { type: 'human_review', id: 'r1' } },
  impact: { value: 80, ruleId: 'manual.v1', evidenceIds: [], source: { type: 'human_review', id: 'r1' } },
  quality: { value: 90, ruleId: 'manual.v1', evidenceIds: [], source: { type: 'human_review', id: 'r1' } },
  persistence: null,
  early: null,
});

// Finalize
svc.finalize(contribution.contributionId);
```

---

## Scored Dimensions

| Dimension | Description |
|---|---|
| `contribution` | Amount / substance of work |
| `impact` | Protocol usefulness or reach |
| `quality` | Correctness, rigor, maintainability |
| `persistence` | Sustained or repeated contribution |
| `early` | Early-stage contribution factor |

Each dimension exposes: `value` (0-100), `scale`, `ruleId`, `evidenceIds`, `source`.

Aggregate is `null` under current draft policy (weights not approved).

---

## Evidence Types

- `git_commit`, `pull_request`, `issue`, `review`
- `file_hash`, `dataset_hash`, `compute_receipt`
- `benchmark_report`, `document_url`
- `transaction_hash` (read-only evidence)
- `signed_public_message`, `manual_review_note`

---

## Completion Report

```
TASK_ID:           MOOD-PROTOCOL-CONTRIBUTION-CORE-002
STATUS:            ✅ COMPLETE
CANON_CHANGE:      NO
BRANCH:            (not committed — working directory)
BASE_COMMIT:       (not in git)
FINAL_COMMIT:      (not committed)
FILES_CHANGED:     protocol/contribution/* (new package)

TESTS:             27/27 PASS (T1–T18)

POLICY_STATUS:     draft — aggregate disabled — HUMAN_DECISION_REQUIRED for weight approval

SAMPLE_CONTRIBUTION_IDS: mood-contrib-[deterministic-12-char-base36]

DUPLICATE_TEST:    ✅ EXACT_DUPLICATE rejected
                   ✅ CROSS_CONTRIBUTOR_DUPLICATE flagged

IMMUTABILITY_TEST: ✅ finalized records reject immutable-field mutation

CHAIN_WRITE:        NONE
TOKEN_DISTRIBUTION: NONE

NO_CHAIN_WRITE_PERFORMED
NO_TOKEN_DISTRIBUTION_PERFORMED

HUMAN_DECISION_REQUIRED:
  - Approve dimension weights for aggregate score computation
  - Lock policy from 'draft' to 'approved' once weights are confirmed

ROLLBACK:
  - Delete protocol/contribution/ directory
  - No chain state, treasury, or token state is affected
```

---

## Integration with Other Packages

| Package | Relationship |
|---|---|
| MPF-001 (Foundation) | Consumes mainnet facts for chain identity |
| MPF-003 (Reputation) | Consumes reputation-evidence artifacts from MPF-002 |
| MPF-004+ | Future packages may connect reputation to protocol rights |
