# Error Model

## Error envelope

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

## Codes

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

## Public safety

Do not expose:
- stack traces
- SQL
- internal paths
- secrets
- raw exceptions
- private infrastructure metadata
