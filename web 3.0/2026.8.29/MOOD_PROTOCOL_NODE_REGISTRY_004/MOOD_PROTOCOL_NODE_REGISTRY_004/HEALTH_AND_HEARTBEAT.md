# Health and Heartbeat

## Health is observation

Health is not reputation.

A good contributor can operate a temporarily offline node.

An online node can still have low protocol reputation.

Keep these separate.

## Observation

Recommended:

```json
{
  "nodeId": "mood:node:...",
  "observedAt": "...",
  "source": "registry-probe",
  "status": "healthy",
  "protocolCompatible": true,
  "latencyMs": 42,
  "reason": null
}
```

Latency may be stored as a bucket if exact values are unnecessary.

## Draft health policy

If no authoritative values exist, create draft configuration such as:

```text
healthyFreshnessSeconds
degradedAfterSeconds
inactiveAfterSeconds
```

Do not claim draft thresholds are production policy.

## Retention

Keep:
- latest observation
- lifecycle-relevant state changes
- bounded history for diagnostics

Avoid infinite high-frequency logs inside canonical protocol records.

## Offline nodes

Offline does not mean malicious.

Use:

```text
unreachable
inactive
unknown
```

not punitive terminology.
