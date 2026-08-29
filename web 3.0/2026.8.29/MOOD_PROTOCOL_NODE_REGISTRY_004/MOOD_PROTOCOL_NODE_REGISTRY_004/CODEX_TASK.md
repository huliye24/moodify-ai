# CODEX TASK — MPF-004 Node Registry

## Task ID

`MOOD-PROTOCOL-NODE-REGISTRY-004`

## Objective

Implement a storage-agnostic, auditable registry of independent MOOD network nodes.

The system must be able to:

1. create a stable node identity;
2. associate a node with a public operator/protocol identity;
3. register a node type;
4. publish a capability manifest;
5. verify basic ownership/control of a node endpoint where applicable;
6. record verification evidence;
7. maintain node lifecycle state;
8. record heartbeat/health observations;
9. expose read-only discovery/search;
10. produce a deterministic registry snapshot;
11. work offline in tests;
12. avoid any token, treasury, staking or remote-execution behavior.

## Repository authority

Before coding inspect:

- `AGENTS.md`
- `docs/canon/*`
- MPF-001 outputs
- MPF-002 implementation
- MPF-003 implementation
- any existing node/cloud/worker/agent/service-discovery code
- current tests

Do not create a second authoritative node identity or health system if one already exists.

If authority conflicts:

`HUMAN_DECISION_REQUIRED`

with:
- conflicting files
- conflicting definitions
- proposed migration
- risk

## Canon rule

Default:

`CANON_CHANGE = NO`

If node registry becomes a new authority requiring Canon updates, follow repository Canon change rules explicitly.

## Node types

Registry must support at minimum:

- `developer`
- `compute`
- `data`
- `storage`
- `validation`
- `gateway`

Optional future types may be represented through versioned policy.

Do not equate node type with economic reward.

## Required node record

At minimum:

```json
{
  "schemaVersion": "1.0.0",
  "nodeId": "mood:node:...",
  "operatorProtocolId": "mood:contributor:...",
  "nodeType": "compute",
  "displayName": "Optional public label",
  "region": {
    "countryCode": "SG",
    "regionCode": null,
    "city": null,
    "precision": "country"
  },
  "endpoint": {
    "type": "https",
    "uri": "https://example.org/node"
  },
  "capabilityManifestId": "mood:capability:...",
  "verification": {
    "status": "pending"
  },
  "health": {
    "status": "unknown"
  },
  "lifecycleStatus": "registered",
  "registeredAt": "...",
  "updatedAt": "...",
  "recordFingerprint": "sha256:..."
}
```

Endpoint may be `null` for node classes that should not expose a network endpoint.

## Stable node ID

Node ID must not depend on IP address because infrastructure can move.

Recommended derivation:

```text
mood:node:
sha256(
  nodeIdVersion
  + operatorProtocolId
  + nodeType
  + stable public node key / generated registry nonce
)
```

If using a random nonce:
- store it as public node metadata;
- do not treat it as a secret;
- keep ID stable after infrastructure migration.

## Operator identity

Prefer MPF-003 Protocol ID when available.

MPF-004 must not require private keys or seed phrases.

A public operator identity may register multiple nodes.

## Capability manifest

Each node has a versioned capability manifest.

Examples:

### Compute

- cpu architecture
- vCPU capacity class
- memory capacity class
- GPU model/capability if public
- supported runtimes
- maximum job class
- availability declaration

### Storage

- storage class
- available capacity class
- supported object protocols
- retention capabilities

### Data

- dataset categories
- data access mode
- metadata/provenance availability
- licensing status class

### Validation

- supported validation types
- benchmark suites
- verification runtime

### Developer

- supported repositories / domains
- contribution interface
- optional public GitHub identity

### Gateway

- supported protocol versions
- ingress/egress capabilities
- public endpoint

Do not expose secrets, internal topology, private IPs, billing credentials or customer data.

## Capability declaration vs verification

Every capability must expose verification status:

```text
declared
verified
partially_verified
unverified
rejected
```

Do not present a self-declared GPU, storage volume or dataset as verified truth.

## Node lifecycle state machine

Implement a single authoritative state machine:

```text
draft
  ↓
registered
  ↓
pending_verification
  ├──> rejected
  └──> verified
           ↓
         active
           ├──> degraded
           ├──> inactive
           ├──> suspended
           └──> retired
```

Allowed recovery transitions should be explicit, for example:

```text
degraded -> active
inactive -> active
suspended -> pending_verification
```

No silent skipping.

## Verification

Verification should prove control or observability, not ownership of the physical asset.

Allowed examples:

- HTTPS challenge token served at a known path
- signed public challenge with a node public key
- repository verification for developer node
- deterministic response to a registry challenge
- manually approved evidence with reviewer provenance

Do not require:
- wallet transaction
- payment
- token staking
- KYC
- private cloud credentials

## Heartbeat

The registry must support health observations without conflating health with reputation.

Recommended:

```text
healthy
degraded
unreachable
unknown
```

Heartbeat record:

- node ID
- observed at
- observation source
- latency bucket or optional measurement
- protocol compatibility
- health status
- evidence / reason

Do not store high-frequency telemetry forever by default.

## Heartbeat policy

Use a versioned policy for:

- healthy freshness window
- degraded threshold
- inactive threshold

If authoritative thresholds do not exist:
- use draft policy;
- do not claim production truth;
- mark it clearly.

## Discovery

Expose read-only querying by:

- node type
- lifecycle status
- health status
- country / region
- capability key
- protocol version

Discovery result must clearly distinguish:

```text
declared capability
verified capability
current health observation
```

## Registry snapshot

Create a deterministic, immutable snapshot representing registry state at a defined time/epoch.

At minimum:

- snapshot ID
- schema version
- registry policy version
- included node IDs
- node record fingerprints
- generatedAt
- snapshot fingerprint

This snapshot can later feed the public Transparency page.

## Storage

Core logic must be storage-agnostic.

Provide filesystem/JSON adapter for tests.

If D1/Postgres already exists:
- optional adapter is allowed;
- do not make cloud DB mandatory for unit tests.

## Network behavior

MPF-004 may perform safe verification reads in integration tests if infrastructure is available.

Unit tests must run offline.

No remote execution.

No SSH.

No shell deployment.

No cloud mutation.

## Required fixtures

At least:

1. valid compute node
2. valid storage node
3. valid data node
4. valid validation node
5. endpoint-less developer node
6. malformed node ID
7. invalid region precision
8. self-declared unverified GPU capability
9. successfully verified HTTPS challenge
10. failed challenge
11. healthy heartbeat
12. stale heartbeat → inactive
13. degraded → active recovery
14. illegal lifecycle transition
15. duplicate node record
16. registry snapshot determinism

## Tests

Required:

- stable node ID
- node normalization
- schema validation
- capability schema validation
- verification status separation
- lifecycle guards
- heartbeat freshness
- stale node state
- recovery
- duplicate detection
- location privacy
- no secret fields
- no remote execution path
- no chain writes
- no economic fields
- offline core tests
- deterministic registry snapshot

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
NODE_POLICY_VERSION
HEALTH_POLICY_VERSION
SAMPLE_NODE_IDS
SAMPLE_REGISTRY_SNAPSHOT
VERIFICATION_TEST
HEARTBEAT_TEST
NO_REMOTE_CODE_EXECUTION_ADDED
NO_CHAIN_WRITE_PERFORMED
NO_TOKEN_ECONOMICS_ADDED
HUMAN_DECISION_REQUIRED
ROLLBACK
```

Do not report PASS with failed mandatory tests.
