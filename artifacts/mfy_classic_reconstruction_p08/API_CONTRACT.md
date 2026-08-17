# MFY-CR-P08 — API CONTRACT v0.1

Base prefix: `/api/v1/reconstruction` (FastAPI, registered in
`moodify.api.main`). Product-facing only; no engineering parameters, no
internal paths, no public URLs.

## Endpoints

### GET /capabilities
```json
{"api_version":"v0.1","supported_formats":[".aac",".flac",".m4a",".mp3",".ogg",".wav"],
 "max_file_size_bytes":52428800,"max_duration_seconds":null,
 "reconstruction_mode":["auto"],"reconstruction_version":"reconstruction-job-v0.1",
 "stems_available":false,"human_review_available":true,"auth_mode":"single_user|owner"}
```

### POST /jobs  (multipart)
- Fields: `source` (file), `reconstruction_mode=auto` (only "auto" accepted),
  `training_permission=false`, `public_demo_permission=false`.
- Headers: `Idempotency-Key` (optional), `X-Moodify-Rebuild: true` (optional),
  `X-Moodify-Actor-User-Id` (required in owner mode).
- Responses: 202 `{job, source_sha256, idempotency:"CREATED"}`;
  200 `{job, source_sha256, idempotency:"RETURN_EXISTING"}` on idempotent
  replay; 400 (mode/params disallowed), 413 (too large), 415 (type), 422
  (empty), 503 (queue full).

### GET /jobs/{job_id}
Product projection only: `job_id, status, progress, source_sha256, created_at,
updated_at, result_available, user_action_required`. No workspace paths, no
failure internals. 404 for unknown or cross-owner.

### POST /jobs/{job_id}/cancel
202 on success; 409 for terminal jobs (incl. HUMAN_REQUIRED); 404 unknown/
cross-owner.

### GET /jobs/{job_id}/result
- 200 result metadata + `audio_url` with short-lived HMAC token (15 min,
  owner-bound).
- 200 `{status:"HUMAN_REQUIRED", ...}` when stopped for review.
- 409 RESULT_NOT_READY otherwise; 404 unknown/cross-owner.

### GET /jobs/{job_id}/result/audio?token=...
Owner-only short-lived audio access. 401 expired/invalid token, 403
cross-owner, 500 TOKEN_SECRET_MISSING (fail-closed when secret unset), 404
missing file. Path traversal is impossible: resolved path must stay under the
workspace root.

## Privacy defaults

`training_permission=false`, `public_demo_permission=false`, `shareable=false`,
`searchable=false` (job fields carry the first two; sharing/search features do
not exist). No public catalog, no public track IDs, no recommendation over
private uploads.

## Android (P09) contract

Android only needs: select source, submit, poll/observe, play result. It never
sees ProductionCase internals, diagnostics, A/B/C, identity guard, stems, or
algorithms.
