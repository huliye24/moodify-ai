# API Contract

## Base

Recommended:

```text
/api/protocol/v1
```

## Public read endpoints

### Health

```text
GET /health
```

### Protocol

```text
GET /protocol
GET /protocol/mainnet
```

### Contributions

```text
GET /contributions
GET /contributions/{contributionId}
```

### Contributors

```text
GET /contributors/{protocolId}
GET /contributors/{protocolId}/contributions
GET /contributors/{protocolId}/reputation
```

### Nodes

```text
GET /nodes
GET /nodes/{nodeId}
GET /nodes/{nodeId}/capabilities
GET /nodes/{nodeId}/health
```

### Network

```text
GET /network/summary
GET /network/snapshot
```

## Response metadata

Every success response:

```json
{
  "apiVersion": "v1",
  "data": {},
  "meta": {
    "requestId": "req_...",
    "generatedAt": "2026-08-29T00:00:00Z"
  }
}
```

## List pagination

Recommended:

```json
{
  "limit": 50,
  "nextCursor": null
}
```

Maximum page size must be bounded.

## Public-data discipline

Any field returned publicly must have an explicit public reason.

Default-deny internal fields.
