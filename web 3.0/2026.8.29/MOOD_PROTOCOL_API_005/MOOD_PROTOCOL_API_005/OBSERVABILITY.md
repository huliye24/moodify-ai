# Observability

## Required

At minimum log:

- request ID
- route
- method
- response status
- duration
- dependency status
- timestamp

## Do not log

- private keys
- seed phrases
- auth tokens
- cookies
- credentials
- private evidence
- full sensitive request bodies

## Health

API health and network health are different.

```text
API = healthy
Node network = degraded
```

is valid.

Do not collapse them into one boolean.

## Metrics

Optional:

- request count
- error rate
- latency
- dependency failure count

Avoid market metrics in core API observability.
