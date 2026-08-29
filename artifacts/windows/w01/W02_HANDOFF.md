# W02 Handoff

```text
W02_GATE = PASS
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```

The facts needed to begin W02 are known. “Missing” is an audited state, not an unknown authority.

SAFE_TO_REUSE:
- Electron/React/Vite/Forge shell and secure preload boundary.
- Public BFF `Track` DTO for cloud tracks.
- `PlaybackService`, `PlaybackQueue`, and single Chromium audio engine.
- `LocalStateStore` atomic/versioned JSON mechanism, after fixing read/wiring boundaries.
- Existing playlist `{id,name}` values as migration input.

MUST_REPAIR_FIRST:
- Define durable local Track identity and source locator/availability separately.
- Add Library schema and allowlisted main/preload IPC repository operations.
- Wire startup rehydration and corruption/migration evidence.
- Add duplicate import normalization and missing/moved/deleted behavior.
- Add renderer integration tests before W03 uses Track references.

DO_NOT_DUPLICATE:
- Do not add a second PlaybackService, queue, or audio element.
- Do not add a third persistence store.
- Do not treat raw path/blob URL as Track identity.
- Do not expose Ear/internal production complexity.

DATA_MIGRATION_REQUIRED: YES — preserve and import `moodify.playlists` names; retain rollback copy. PlaylistItem membership has no legacy data to migrate.

RECOMMENDED_FIRST_COMMIT:
- Add a tested v2 `LocalState` Library/Track schema plus repository IPC adapter, read existing v1 JSON, preserve old playlist-name localStorage for later migration, and render the rehydrated Library without changing the frozen visual direction.

EVIDENCE:
- `repository-map.md`, `state-authority-map.md`, `persistence-audit.md`, `playlist-add-root-cause.md`.
- `npm run verify`: 79/79 tests passed.
- Forge produced fresh Alpha 4 package and Squirrel installer artifacts.
