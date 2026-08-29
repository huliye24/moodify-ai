# Secret Ownership Matrix

| Secret Class | Owner | Consumers | Storage Class | Rotation Owner | Forbidden Locations | Notes |
|---|---|---|---|---|---|---|
| Database credential | | | | | Git / Android / task packs | |
| OSS credential / STS | | | | | Git / Android long-term storage | |
| External audio API key | | | | | Git / logs | |
| Service auth secret | | | | | public docs | |
| SSH key | | | | | repo / shared archive | |

## Principle

Prove a credential exists without recording the credential value.
