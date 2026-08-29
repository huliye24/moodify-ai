# Read-Only Discovery API

## Goal

Allow Protocol Web and future schedulers to inspect the resource map.

MPF-004 discovery is read-only.

## Suggested routes

Adapt to repository conventions.

```text
GET /protocol/nodes
GET /protocol/nodes/{nodeId}
GET /protocol/nodes/{nodeId}/capabilities
GET /protocol/nodes/{nodeId}/health
GET /protocol/registry/snapshot
```

## Filters

Support where appropriate:

```text
type
lifecycle
health
country
region
capability
protocolVersion
verificationStatus
```

## Response discipline

Do not imply self-declared capability is verified.

Expose fields separately:

```json
{
  "declared": true,
  "verificationStatus": "unverified"
}
```

## No control operations

MPF-004 API must not expose:

```text
POST /execute
POST /shell
POST /deploy
POST /transfer
POST /stake
POST /reward
```

Registration/update APIs may exist only if authenticated safely and consistent with repository architecture.

A read-only registry prototype is acceptable for this package.
