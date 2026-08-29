# Moodify Music — Identity & Ownership Contract

Status: FROZEN (Rev.2 Phase B)
Authority: MFY-DATA-FOUNDATION-001-REV2 04_IDENTITY_OWNERSHIP_CONTRACT.md

## Platform User

- `users` is Moodify Platform Identity, not a Music-only account.
- Future linkage: Music listener, Creator, Ear permissions, CWC, organizations.
- V1 does not require unified SSO, but ID design must allow future unification
  (`auth_subject` nullable unique for external identity binding).
- Passwords are never stored; public auth completion is honestly marked
  `PUBLIC_USER_AUTH_NOT_PRODUCTION_READY` until it exists.

## Creator

- Creator is NOT a second login account. Relationship: `users 1 ── 1 creator_profiles`.
- V1: one user at most one primary creator profile.
- `handle` is globally unique and normalized; handle is mutable identity,
  resource `id` is the immutable key. Public URL: `/c/{handle}`.

## Track Ownership

- Tracks carry `creator_id` + `created_by_user_id`. Permission to modify/publish
  is decided by ownership service checks, never by knowing a public track ID.

## Track Version

- A track is the stable public identity; `track_versions` are immutable media
  revisions with `UNIQUE(track_id, version_no)`.
- `tracks.current_version_id` points at the published/current version.

## Publication State

- States: `draft → published → unlisted → archived` (explicit transitions only).
- Never reuse Ear job status as publication state.

## Ear Linkage

- Music may hold nullable external references (`ear_production_case_ref`,
  `approved_evidence_ref`) as stable IDs/strings only.
- No FK into Ear SQLite; Music cannot mutate Ear state.
- Ear experimental scores are never public music-quality certification.

## Publication-Safe Evidence

- Default private. Only explicitly approved (`publish_safe`) evidence may be
  shown by Music. Prompts, internal paths, judgment logs stay private.

## Known V1 limitation

`PUBLIC_USER_AUTH_NOT_PRODUCTION_READY` — bootstrap/dev identity only.
