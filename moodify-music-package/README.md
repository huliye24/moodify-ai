# Moodify Music Service

**Role:** internal service and data layer for the public Moodify Music / Player surfaces

This package owns Music-domain identity, catalogue, track/version metadata, library relationships, playlists, publishing state, audit records, and the BFF boundary. It does not own Ear production cases, measurements, evidence decisions, or the cloud production job state machine.

## Authority boundary

```text
Music Web / Android
        ↓
Music BFF
        ↓
Music Data API
        ↓
Music database authority
```

Cross-system analysis or reconstruction requests use explicit bridge contracts. Music must not create a second Ear state machine, and Ear must not write Music publication or ownership state.

## Package layout

- `src/moodify_music/api/` — HTTP routes, identity, idempotency, and dependencies
- `src/moodify_music/bff/` — public-client boundary and media delivery
- `src/moodify_music/models.py` — Music-domain persistence models
- `alembic/` — forward migrations
- `tests/` — API, BFF, ownership, lifecycle, security, and data-boundary tests

## Development

```bash
python -m pip install -e ".[test]"
pytest
```

Database changes require a backup, migration dry run, idempotency review, post-migration verification, and a forward-fix or restore plan. Presence of a database adapter or migration does not prove that PolarDB or any cloud database is reachable in production.

## Security and evidence

- Secrets belong in deployment configuration, never source control.
- Write routes require authenticated authority and idempotency where applicable.
- Public responses must not expose internal paths, credentials, private media, Ear evidence, or operator-only state.
- Capability claims require runtime evidence in addition to passing tests.
