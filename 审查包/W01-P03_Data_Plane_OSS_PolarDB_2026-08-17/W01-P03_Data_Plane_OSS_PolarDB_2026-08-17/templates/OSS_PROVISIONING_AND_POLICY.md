# OSS Provisioning & Policy

## Bucket

- region:
- bucket:
- ownership:
- public access:
- versioning:
- lifecycle:
- encryption:
- access logging:
- endpoint:
- network path:

## Access

### Control API
- read:
- write:
- delete:

### Worker
- read:
- write:
- delete:

### Mobile Client
- direct credentials: FORBIDDEN
- access method:
- signed URL / proxy:
- TTL:

## Prefix Retention

| Prefix | Artifact | Retention Class | Delete Authority |
|---|---|---|---|
| source | canonical source | long-lived | explicit |
| stems | derived | configurable | policy |
| analysis | derived/evidence support | medium/long | policy |
| intermediate | transient | short | automated/manual |
| renders | user-facing | versioned | explicit/policy |
| evidence | provenance | long-lived | explicit |

## Write Gate

No bucket creation or real upload unless explicitly authorized.
