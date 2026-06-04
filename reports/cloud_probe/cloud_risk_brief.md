# Cloud Risk Brief — MHP-255 | **Date**: 2026-06-04

## Risks

| Risk | Likelihood | Severity | Mitigation |
|------|-----------|----------|------------|
| Worker data leak (audio files on cloud) | Low | Critical | Encrypted artifact store, ephemeral workers |
| Cost overrun (runaway scaling) | Medium | High | Max worker cap, cost alerts, daily budget |
| Multi-worker queue corruption | Medium | High | Atomic claims, TTL leases, idempotent writes |
| Network partition causes split-brain | Low | High | Heartbeat-based lease expiry, no split writes |
| Vendor lock-in | Medium | Medium | Abstract scheduler interface, cloud-agnostic models |
| Idle worker costs | Medium | Medium | Auto-scale to zero on empty queue |
| Cloud API rate limits | Low | Medium | Exponential backoff on API calls |
