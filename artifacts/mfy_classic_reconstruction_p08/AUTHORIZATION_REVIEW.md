# MFY-CR-P08 — AUTHORIZATION REVIEW

## Model

- `MOODIFY_AUTH_MODE=single_user` (DEFAULT): any request is recorded under the
  fixed owner `dev-user`. This is a development/dev boundary.
  **STATUS: NOT_MULTIUSER_PRODUCTION_READY — do not deploy as multiuser auth.**
- `MOODIFY_AUTH_MODE=owner`: `X-Moodify-Actor-User-Id` header required (401
  when missing); every read/cancel/result is owner-filtered at the store level.

## Boundary guarantees (owner mode)

| Access | Guarantee |
|---|---|
| Query User B job | 404 (existence not revealed) |
| Fetch User B source | impossible: source is inside User B's workspace; no source endpoint exists |
| Fetch User B result | 404 via owner-filtered `get_job` |
| Fetch User B evidence | no evidence endpoint in v0.1 (evidence stays in workspace + artifacts) |
| Cancel User B job | 404 |
| Audio access | HMAC token bound to (job_id, owner_id), 15 min TTL, cross-owner 403 |

## Token design

`token = "{job_id}:{owner_id}:{exp}:{hmac_sha256(secret, payload)}"`
- Secret from env `MOODIFY_AUDIO_TOKEN_SECRET`; missing secret -> 500
  TOKEN_SECRET_MISSING (fail-closed, never open).
- Constant-time compare via `hmac.compare_digest`; expiry enforced; owner
  mismatch 403.

## Honest limits

- Single-user mode is not production auth; no OAuth/JWT integration yet.
- Session management lives on the LA BFF (music package, auth_sessions);
  this API is designed to sit behind it. Wire-up to the BFF is P09 scope.
- The actor header is a trust boundary assumption until BFF integration;
  documented, not hidden.
