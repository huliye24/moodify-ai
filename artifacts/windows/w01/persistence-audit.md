# W01 Persistence Audit

## Main-process store

- Location: `<Electron userData>\moodify\local-state.json`.
- Schema version: `1`.
- Fields: playback (`lastTrackId`, `positionMs`, `volume`), window bounds, app version/first-run time.
- Writes: debounced, temporary file then rename.
- Recovery: invalid JSON falls back to defaults; future schema also resets.
- Migration: hook exists, but no migration has been implemented.
- Backup: none. Corrupt data is reset rather than quarantined.
- Wiring gap: window changes write; playback values are not wired into this store and window values are not read when creating the window.

## Renderer playlist store

- Location: Chromium localStorage key `moodify.playlists`.
- Schema: unversioned JSON array containing only `{id,name}`.
- Validation: filters for string `id` and `name` on read.
- Atomicity, migration, backup, corruption evidence: none; parse failure silently returns `[]`.

## Library and file identity

There is no durable local Library or PlaylistItem schema. Import creates IDs of `local-${Date.now()}-${index}` and `blob:` URLs. It does not store absolute/normalized paths, file URI, hash, metadata tuple, or UUID. Selecting the same file again creates a different identity and replaces the previous in-memory list/queue. Same-name files are not distinguished in UI beyond their generated ID. Move/rename/delete after selection is insulated temporarily by the live `File`/blob object, but no reference exists after restart and no unavailable/relink state exists.

Existing playlist names must be preserved during W02 migration. Read the old key, validate/dedupe IDs, import into the versioned authority, retain a rollback copy until migration tests pass, and never delete playlist relations merely because a source file is unavailable.
