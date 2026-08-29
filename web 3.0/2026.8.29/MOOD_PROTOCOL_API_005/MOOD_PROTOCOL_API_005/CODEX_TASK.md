# CODEX TASK — MPF-005 Protocol API

## Task ID

`MOOD-PROTOCOL-API-005`

## Objective

Implement a versioned protocol-facing API that exposes the authoritative state created by MPF-001 through MPF-004.

The API must:

1. read MPF-001 mainnet facts;
2. read MPF-002 contributions;
3. read MPF-003 protocol profiles and reputation snapshots;
4. read MPF-004 nodes, capabilities and health;
5. expose a unified network summary;
6. provide stable versioned response envelopes;
7. centralize API errors;
8. expose public/restricted visibility correctly;
9. support safe, limited protocol writes only where domain modules already authorize them;
10. remain free of chain writes, token transfers and remote node execution.

## Repository authority

Before coding inspect:

- `AGENTS.md`
- `docs/canon/*`
- MPF-001 implementation
- MPF-002 implementation
- MPF-003 implementation
- MPF-004 implementation
- existing web/API framework
- existing auth middleware
- existing database/storage adapters
- existing tests

Do not introduce a second backend framework if a canonical one already exists.

If domain rules differ across existing services:

`HUMAN_DECISION_REQUIRED`

Do not resolve silently.

## Canon rule

Default:

`CANON_CHANGE = NO`

The API must delegate to existing protocol/domain authorities rather than redefining them.

## Required API version

Start with:

```text
/api/protocol/v1
```

or equivalent existing project convention.

Version must be explicit and documented.

## Required read endpoints

At minimum support equivalents of:

```text
GET /api/protocol/v1/health

GET /api/protocol/v1/protocol
GET /api/protocol/v1/protocol/mainnet

GET /api/protocol/v1/contributions
GET /api/protocol/v1/contributions/{contributionId}

GET /api/protocol/v1/contributors/{protocolId}
GET /api/protocol/v1/contributors/{protocolId}/reputation
GET /api/protocol/v1/contributors/{protocolId}/contributions

GET /api/protocol/v1/nodes
GET /api/protocol/v1/nodes/{nodeId}
GET /api/protocol/v1/nodes/{nodeId}/capabilities
GET /api/protocol/v1/nodes/{nodeId}/health

GET /api/protocol/v1/network/summary
GET /api/protocol/v1/network/snapshot
```

Adapt paths to repository conventions if necessary.

## Optional write endpoints

Writes are allowed only if the corresponding domain package already exposes a validated safe command.

Potential examples:

```text
POST /contributions
POST /nodes
POST /nodes/{nodeId}/heartbeat
```

But only if:
- existing domain validation is reused;
- auth boundary is defined;
- no protocol logic is reimplemented in route handlers;
- no chain transaction is triggered;
- no token distribution occurs;
- no remote execution occurs.

If no safe domain write command exists, keep MPF-005 read-only.

Read-only PASS is acceptable.

## Route-handler rule

Route handlers should do only:

```text
parse
authenticate/authorize
call domain service
map result
return response
```

They must NOT:
- calculate reputation
- score contributions
- mutate node state directly
- derive official contract addresses
- calculate token rewards
- call shell/SSH
- send blockchain transactions

## Response envelope

Use a consistent envelope:

```json
{
  "apiVersion": "v1",
  "data": {},
  "meta": {
    "requestId": "...",
    "generatedAt": "..."
  }
}
```

For lists:

```json
{
  "apiVersion": "v1",
  "data": [],
  "meta": {
    "requestId": "...",
    "generatedAt": "...",
    "pagination": {}
  }
}
```

## Protocol mainnet response

Must be sourced from MPF-001 canonical facts.

It must not duplicate hard-coded chain/token values inside route files.

## Contribution API

Read from MPF-002 authority.

Filters may include:

- contributor
- category
- status
- policy version
- time range

Public API must not expose private evidence or secrets.

## Reputation API

Read from MPF-003 authority.

Return:
- protocol profile
- current snapshot
- historical snapshot list if available
- dimensions
- aggregate if policy defines it
- confidence/completeness
- policy version

Do NOT synthesize an aggregate if MPF-003 says `aggregate = null`.

## Node API

Read from MPF-004 authority.

Expose:
- node type
- region at approved public precision
- lifecycle status
- health
- declared capabilities
- verification state

Do NOT expose:
- private IP
- internal cloud metadata
- SSH details
- secret endpoints
- credentials

## Network summary

Build a read model from authoritative modules.

Suggested fields:

```json
{
  "protocol": {
    "status": "..."
  },
  "contributors": {
    "count": 0
  },
  "contributions": {
    "total": 0,
    "verified": 0
  },
  "nodes": {
    "total": 0,
    "active": 0,
    "byType": {},
    "byRegion": {}
  },
  "reputation": {
    "profiles": 0,
    "snapshots": 0
  },
  "generatedAt": "..."
}
```

No token price, market cap or trading volume in core network summary.

## Network snapshot

Expose a deterministic read-only aggregate snapshot referencing:

- MPF-001 facts fingerprint/lock
- MPF-002 contribution snapshot/version if available
- MPF-003 reputation snapshot/version
- MPF-004 registry snapshot

The API snapshot itself must be fingerprintable.

## Pagination

List endpoints must use bounded pagination.

Use cursor or limit/offset according to existing project standards.

Set safe defaults and maximum limits.

## Filtering

Validate all query parameters.

Reject unknown/unsafe filter values rather than silently using them.

## Sorting

Expose a small allowlist of sort keys.

Do not concatenate untrusted sort fields into SQL.

## API documentation

Generate or maintain:
- OpenAPI document, or
- equivalent framework-native API schema.

It must describe:
- routes
- request schemas
- response schemas
- auth requirements
- public vs restricted data

## Health endpoint

`/health` must report API health, not falsely claim every node/network component is healthy.

Recommended:

```json
{
  "status": "ok",
  "components": {
    "protocolFacts": "ok",
    "contributions": "ok",
    "reputation": "ok",
    "nodeRegistry": "ok"
  }
}
```

Use `degraded` when dependencies are partially unavailable.

## Errors

Use standardized errors:

```text
INVALID_REQUEST
NOT_FOUND
CONFLICT
UNAUTHORIZED
FORBIDDEN
RATE_LIMITED
DEPENDENCY_UNAVAILABLE
POLICY_BLOCKED
HUMAN_DECISION_REQUIRED
INTERNAL_ERROR
```

Do not leak stack traces to public responses.

## Request IDs

Every request should have a request ID for observability.

Do not use a request ID as security authorization.

## Auth boundary

Public read endpoints can be unauthenticated if policy allows.

Restricted writes require existing safe authentication.

Do not invent production admin credentials in code.

Do not use wallet signatures unless a later package explicitly introduces them.

## CORS

Use explicit allowed origins for production.

Do not blindly use `*` together with credentials.

## Cache

Public stable reads may use safe caching.

Do not cache restricted data in public caches.

## Storage independence

The API must call repository/domain abstractions.

It should not bypass those abstractions with ad-hoc SQL.

## Required fixtures/tests

At minimum test:

1. API health
2. mainnet facts read
3. contribution list
4. contribution detail
5. contributor profile
6. reputation snapshot with aggregate null
7. node list
8. node capability verification distinction
9. node health
10. network summary
11. network snapshot determinism
12. invalid pagination
13. invalid filters
14. not found
15. restricted/private fields excluded
16. route handler cannot bypass domain rule
17. no chain-write path
18. no RCE path
19. OpenAPI/schema generation
20. offline/local test mode

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
API_VERSION
ENDPOINTS
OPENAPI_PATH
TESTS
NETWORK_SUMMARY_SAMPLE
NETWORK_SNAPSHOT_FINGERPRINT
READ_ONLY_OR_WRITE_MODE
NO_CHAIN_WRITE_PERFORMED
NO_TOKEN_TRANSFER_PATH_ADDED
NO_REMOTE_EXECUTION_PATH_ADDED
HUMAN_DECISION_REQUIRED
ROLLBACK
```
