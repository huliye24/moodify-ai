# Moodify Music v1 Domain Contract

Status: Phase C foundation  
Authority: Moodify Music commercial data only

## Data authority

- D1 is the v1 relational authority for users, creators, catalogue metadata,
  relationships, publication audit events, and commercial intents.
- R2 binding `MEDIA` is the intended authority for uploaded audio and optional
  covers. D1 stores object keys and integrity metadata, never audio blobs.
- Moodify Ear retains its own job queue, production cases, measurements, and
  evidence. Music may reference approved Ear IDs but cannot mutate Ear state.
- Authentication adapters must resolve an external identity to one `users.id`.
  Ear device-pairing tokens are not Music user sessions.

## Identity and IDs

- IDs are opaque strings created with cryptographically secure UUIDs at the
  application boundary.
- `auth_subject` is the stable external identity key. Email is mutable contact
  data and is not an authorization key.
- One user owns at most one creator profile in v1.
- Creator handles are globally unique and must be normalized before insertion.

## Track and version lifecycle

```text
draft -> published -> unlisted -> withdrawn
  |          |           |
  +----------+-----------+ (explicit, authorized transitions only)
```

- A track is the stable public identity; a track version is immutable media.
- `tracks.current_version_id` is assigned only after its media object and
  integrity metadata have been verified.
- Publishing requires an owned track, a current version, a rights statement,
  and a basic creation passport.
- `publication_events` records every publication-state transition.
- A missing cover never blocks publication; clients render Moodify vinyl.

## Creation Passport boundary

The passport is a creator declaration attached to a specific immutable track
version. It is not copyright certification, an Ear quality score, or proof that
rights are uncontested. Private prompts must never be returned by public APIs.

## Relationships

- Follow and favorite writes are authenticated and idempotent through composite
  primary keys.
- Public counters are derived data; they are not authoritative balances and
  should not dominate the user experience.

## Commercial intents

- A license intent is a real lead, not a license grant or completed sale.
- Guest license inquiries may provide an email after abuse controls are added.
- Only the owning creator and authorized operators may change intent status.
- A support record starts as `intent`. It may become `paid` only after verified
  payment-provider evidence. CWC is never a currency or payment instrument.

## Privacy and evidence

- Listen events collect only the minimum fields in the schema.
- Internal file paths, raw prompts, private audio, experimental measurements,
  and unapproved Ear conclusions are not Music public fields.
- Public APIs expose an explicit view model; database rows are never serialized
  wholesale.

## Failure and recovery

- Media upload and database publication are separate steps. Orphaned objects
  remain private and are reconciled asynchronously.
- Failed publication leaves the track in `draft` and retains evidence needed to
  retry or investigate.
- Database migrations are append-only once deployed. Rollback restores the
  previous application release; destructive schema reversal requires a reviewed
  data-recovery procedure.
