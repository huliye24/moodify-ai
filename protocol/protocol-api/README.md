# MOOD Protocol API (MPF-005)

## Overview

The Protocol API exposes authoritative state from MPF-001 (Mainnet Facts), MPF-002 (Contributions), MPF-003 (Reputation), and MPF-004 (Nodes) through a single versioned application boundary.

**Read-only by design.** No chain writes, token transfers, or remote execution.

## Architecture

```
protocol/protocol-api/
├── core/
│   ├── envelope.js              # Response envelope
│   ├── errors.js                # Standardized error codes
│   └── domain-services.js       # Adapters to MPF-001/002/003/004
├── routes/
│   └── handlers.js              # Thin route handlers
├── openapi/
│   └── openapi-spec.js          # OpenAPI 3.0 specification
├── tests/
│   └── protocol-api.test.js     # T1-T24 test suite
├── fixtures/                    # Sample request/response fixtures
└── README.md
```

## API Version

```
/api/protocol/v1
```

## Endpoints

### Health
- `GET /health` - API health status

### Protocol
- `GET /protocol` - Protocol status
- `GET /protocol/mainnet` - Mainnet facts (MPF-001)

### Contributions
- `GET /contributions` - List contributions
- `GET /contributions/{contributionId}` - Get contribution detail

### Contributors
- `GET /contributors/{protocolId}` - Get contributor profile
- `GET /contributors/{protocolId}/reputation` - Get reputation snapshot
- `GET /contributors/{protocolId}/contributions` - List contributor contributions

### Nodes
- `GET /nodes` - List nodes
- `GET /nodes/{nodeId}` - Get node detail
- `GET /nodes/{nodeId}/capabilities` - Get node capabilities
- `GET /nodes/{nodeId}/health` - Get node health

### Network
- `GET /network/summary` - Aggregate network summary
- `GET /network/snapshot` - Deterministic network snapshot

## Response Envelope

Success:
```json
{
  "apiVersion": "v1",
  "data": {},
  "meta": {
    "requestId": "req_...",
    "generatedAt": "2026-08-29T00:00:00Z",
    "pagination": {}
  }
}
```

Error:
```json
{
  "apiVersion": "v1",
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found",
    "details": null
  },
  "meta": {
    "requestId": "req_..."
  }
}
```

## Error Codes

| Code | HTTP Status |
|------|-------------|
| INVALID_REQUEST | 400 |
| UNAUTHORIZED | 401 |
| FORBIDDEN | 403 |
| NOT_FOUND | 404 |
| CONFLICT | 409 |
| HUMAN_DECISION_REQUIRED | 409 |
| POLICY_BLOCKED | 422 |
| RATE_LIMITED | 429 |
| DEPENDENCY_UNAVAILABLE | 503 |
| INTERNAL_ERROR | 500 |

## Layering Rule

```
HTTP/API
  ↓
Application Service (handlers)
  ↓
Protocol Domain (domain-services)
  ↓
Repository/Adapter (MPF-001/002/003/004)
```

Never:
```
HTTP Route → Direct DB Mutation
```

## Security Boundaries

**Allowed:**
- Public read of protocol facts
- Public read of contribution records
- Public read of reputation records
- Public read of node registry
- Aggregate public network summary
- Local/offline tests

**Forbidden:**
- Private keys
- Seed phrases
- Transaction signing
- Token transfers
- SSH
- Shell
- Arbitrary remote execution

## Pagination

Default limit: 50
Maximum limit: 200

## Privacy

- Default-deny internal fields
- Location precision respected (country/region/city/exact/hidden)
- Private evidence excluded from public responses
- No private IPs or credentials exposed

---

*MPF-005 Status: COMPLETED*
