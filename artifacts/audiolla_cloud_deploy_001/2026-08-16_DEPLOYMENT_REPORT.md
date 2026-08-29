# Audiolla Deployment Evidence

**Task ID:** MFY-AUDIOLLA-CLOUD-DEPLOY-001  
**Date:** 2026-08-16  
**Operator:** Codex  
**Verdict:** PASS_WITH_LIMITATIONS

## 1. Server

```text
hostname: yisu-6a7bcb73aac20
address: 103.144.246.242
provider: not exposed by host inventory
region: Los Angeles (per Moodify production inventory)
OS: Ubuntu 22.04.2 LTS
arch: Linux x86_64
CPU: 4 vCPU
RAM: 7.7 GiB total, 6.3 GiB available before validation
swap: 0 B
filesystem: ext4
disk: 98 GiB total, 77 GiB available, 19% used
load before validation: 0.04 / 0.03 / 0.03
Docker Engine: 29.1.3
Docker Compose: 2.40.3
```

## 2. Existing workload safety

```text
existing services observed: nginx, cloudflared-moodify, moodify-api,
  moodify-music-bff, moodify-music, moodify-worker
existing application binds: 127.0.0.1:8000, 127.0.0.1:8100,
  127.0.0.1:3100, public nginx :80
Audiolla bind: 127.0.0.1:18080 only
conflicts: none
changes to existing services: NONE
```

## 3. Audiolla runtime

```text
version reported by service: 0.3.0
image: psyb0t/audiolla
digest: sha256:1b76f692326e9311be2d92c3d9b8050b593bba5b93395067bfd1b2610a8af03a
immutable image reference pinned in .env: YES
container: moodify-audiolla
restart policy: unless-stopped
bind: 127.0.0.1:18080 -> 8000/tcp
data path: /srv/moodify/audiolla/data -> /data (rw bind mount)
device: cpu
enabled engines: librosa-analyze,pedalboard-chain,sox-transform,fx-chain,matchering
preload: empty
remote fetch: disabled
auth: Bearer token enabled; secret value not recorded in evidence
secret file permissions: 0600
```

## 4. Health and authorization

```text
container health: healthy
authorized GET /healthz: 200
unauthorized GET /v1/catalog: 401
authorized GET /v1/catalog: 200
compose configuration validation: PASS
```

## 5. Functional evidence

The test input was a 7,056,044-byte WAV of about 40 seconds.

```text
PUT /v1/files/uploads/mfy-smoke.wav: 201
POST /v1/audio/analyze: 200, valid JSON, 37.802 s cold latency
POST /v1/audio/master (chain/transparent): 200, 1.155 s latency
transparent output: out/mfy-smoke-transparent.wav, 7,056,078 bytes
GET transparent output: 200
async master submission: 202
async job: pending/running observed, completed in 0.784 s
async output: out/mfy-smoke-async.wav, 7,056,078 bytes
```

Matchering was tested against the deployed OpenAPI contract. The runtime correctly
rejected an identical target/reference pair with HTTP 400. A distinct `loud` chain
variant was then used as the reference for execution-contract validation:

```text
POST reference variant generation: 200
POST /v1/audio/master mode=reference: 200
engine: matchering
latency: 2 s
output: out/mfy-matchering.wav, 7,056,078 bytes
GET Matchering output: 200
```

This proves the reference-mode execution path, not perceptual quality or reference
selection suitability. Moodify Judge remains authoritative.

## 6. Resource evidence

```text
idle/warm container before restart: 524.4 MiB RAM (6.64% host RAM)
fresh healthy container after restart: 67.89 MiB RAM (0.86% host RAM)
observed CPU at snapshots: 0.35% to 0.44%
container block I/O snapshot: 104 MB read / 109 MB written before restart
host swap: none configured
disk after validation: 77 GiB available, 19% used
```

Peak CPU/RAM were not captured during the first cold analyze run, so snapshot values
must not be represented as peaks.

## 7. Restart, persistence, and rollback

```text
forced container recreation: healthy in 10 s
persisted output retrieval after recreation: 200
persisted SHA-256: 6263daca6d664ab8be7125971b050bacb1f20b19734f166a647a8b6aa4d088b2
hash unchanged after recreation: true

rollback exercise: docker compose down, then docker compose up -d
container count after down: 0
data present after down: true
service healthy after recovery: true (9 s)
persisted output retrieval after rollback: 200
hash unchanged after rollback: true
persistent data deletion: NO
```

## 8. Known limitations

- No independent full-song production test was run; results cover an approximately 40-second WAV only.
- CPU and RAM peak sampling was not active during the cold analyze call.
- Matchering used a derived but distinct reference only to validate the API/execution path; no perceptual quality claim is made.
- The service is intentionally localhost-only and is not yet connected to Moodify production.
- No OSS/S3 staging or public endpoint was configured.
- The host has no swap; longer workloads require monitoring.

## 9. Licensing note

```text
deployment mode: self-hosted internal runtime
image redistributed to users: NO
Matchering/Pedalboard GPL distribution review: required before any future image distribution
```

## 10. Moodify integration boundary

```text
production integration performed: NO
recommended runtime URL variable: MOODIFY_AUDIO_RUNTIME_URL
recommended secret variable: MOODIFY_AUDIO_RUNTIME_TOKEN
Audiolla role: Audio Processing Runtime only
Moodify ProductionCase/Evidence/Judge authority changed: NO
```

## 11. Final verdict

```text
Verdict: PASS_WITH_LIMITATIONS
Reason: all P0 deployment, security, functional, persistence, digest, and rollback
  checks passed; full-song load and peak resource measurement remain unverified.
Evidence path (repository): artifacts/audiolla_cloud_deploy_001/2026-08-16_DEPLOYMENT_REPORT.md
Evidence path (server): /srv/moodify/audiolla/evidence/2026-08-16_DEPLOYMENT_REPORT.md
Next allowed step: MFY-AUDIOLLA-INTEGRATION-002, only with separate authorization.
```
