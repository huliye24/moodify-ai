# Persistence Migration

```text
OLD_SCHEMA = LocalState v2 + renderer moodify.playlists {id,name}
NEW_SCHEMA = LocalState v3 + playlists + playlistItems
BACKUP = local-state.json.v2.bak (or original-version backup); moodify.playlists.v2.backup
MIGRATION = idempotent
```

LocalState v2→v3 adds empty relation collections without changing Library Tracks. On renderer startup, validated legacy playlist IDs/names are imported through `PlaylistService.migrateLegacy`; the original localStorage payload is copied to a backup key before the active shadow key is removed. Repeated migration is a no-op. No legacy PlaylistItem data existed.
